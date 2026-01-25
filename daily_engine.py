from telegram.ext import Application, MessageHandler, filters
from datetime import datetime, time
from telegram.ext import ContextTypes
import gspread
from google.oauth2.service_account import Credentials
import re

# ================== HELPERS ==================

def is_valid_telegram_username(text: str) -> bool:
    return bool(re.match(r"^@[a-zA-Z0-9_]{5,32}$", text or ""))


def get_active_task(chat_id):
    if chat_id in TELEGRAM_TASK:
        return TELEGRAM_TASK[chat_id]
    return FORM_TASK.get(chat_id)


def get_current_partner(chat_id):
    partners = PARTNER_LIST.get(chat_id, [])
    idx = PARTNER_INDEX.get(chat_id, 0)
    if not partners:
        return None
    return partners[idx % len(partners)]

# ================== USER STATE ==================

FORM_TASK = {}
TELEGRAM_TASK = {}
DISCIPLINE_TIME = {}

PARTNER_WAITING = set()
PARTNER_LIST = {}
PARTNER_INDEX = {}

# ================== PRESSURE ENGINE ==================

from pressure_engine import (
    get_last_3_logs,
    count_no,
    proof_expected,
    is_proof,
    mark_proof_expected,
    mark_proof_received
)

from config import TELEGRAM_BOT_TOKEN

# ================== GOOGLE SHEET ==================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

import os, json
from google.oauth2.service_account import Credentials

creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=scope
)


client = gspread.authorize(creds)
sheet = client.open("Discipline Accountability System")
log_ws = sheet.worksheet("Daily_Log")

# ================== STEP-9 REMINDERS ==================

async def morning_ping(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in FORM_TASK.keys():
        task = get_active_task(chat_id)
        if not task:
            continue
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "🌅 Good Morning!\n\n"
                f"Today's Task:\n{task}\n\n"
                "Complete hua?\nReply YES / NO\n\n"
                "✏️ Task badalne ke liye:\n"
                "/set_task New task"
            )
        )


async def night_ping(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in FORM_TASK.keys():
        task = get_active_task(chat_id)
        if not task:
            continue
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "🌙 Night Check-in\n\n"
                f"Today's Task:\n{task}\n\n"
                "Complete hua?\nReply YES / NO\n\n"
                "✏️ Task badalne ke liye:\n"
                "/set_task New task"
            )
        )

# ================== MESSAGE HANDLER ==================

async def handle_message(update, context):
    if not update.message or not update.message.text:
        return

    chat_id = update.message.chat_id
    raw_message = update.message.text.strip()
    message = raw_message.upper()
    today = datetime.now().strftime("%Y-%m-%d")

    # ---------- COMMANDS ----------
    if raw_message.startswith("/set_task"):
        task = raw_message.replace("/set_task", "").strip()
        if not task:
            await update.message.reply_text(
                "❌ Example:\n/set_task Daily 2 hours coding"
            )
            return
        TELEGRAM_TASK[chat_id] = task
        await update.message.reply_text(f"✅ Task updated:\n{task}")
        return

    if raw_message == "/view_task":
        task = get_active_task(chat_id)
        await update.message.reply_text(
            f"📌 Current Task:\n{task}" if task else "❌ No task set."
        )
        return

    if raw_message == "/clear_task":
        TELEGRAM_TASK.pop(chat_id, None)
        await update.message.reply_text("✅ Telegram task cleared.")
        return

    if raw_message.startswith("/change_time"):
        DISCIPLINE_TIME[chat_id] = raw_message.replace("/change_time", "").strip()
        await update.message.reply_text("⏰ Discipline time updated.")
        return

    if raw_message == "/help":
        await update.message.reply_text(
            "🆘 Commands:\n\n"
            "/set_task New task\n"
            "/view_task\n"
            "/clear_task\n"
            "/change_time 10 PM\n\n"
            "🤝 Add partner:\n"
            "@username (e.g. @mentor_01)\n\n"
            "Daily reply:\nYES / NO"
        )
        return

    # ---------- PARTNER INPUT ----------
    if chat_id in PARTNER_WAITING:
        if not is_valid_telegram_username(raw_message):
            await update.message.reply_text(
                "❌ Invalid username.\nExample: @bestfriend_123"
            )
            return
        PARTNER_WAITING.remove(chat_id)
        PARTNER_LIST.setdefault(chat_id, [])
        PARTNER_INDEX.setdefault(chat_id, 0)
        PARTNER_LIST[chat_id].append(raw_message)
        await update.message.reply_text(f"✅ Partner {raw_message} added.")
        return

    # ---------- PROOF MODE ----------
    if proof_expected(chat_id, log_ws):
        if is_proof(update):
            mark_proof_received(chat_id, log_ws)
            await update.message.reply_text("✅ Proof accepted.")
        else:
            await update.message.reply_text("❌ Valid proof bhejo.")
        return

    # ---------- YES / NO ----------
    if message not in ["YES", "NO"]:
        await update.message.reply_text(
            "❓ Reply with YES / NO\nor type /help"
        )
        return

    # ---------- SAVE LOG ----------
    log_ws.append_row([today, chat_id, "", message, "N", "N"])

    logs = get_last_3_logs(chat_id, log_ws)
    no_count = count_no(logs)

    if message == "YES":
        await update.message.reply_text("👍 Good. Stay disciplined.")
        return

    if no_count >= 3:
        partners = PARTNER_LIST.get(chat_id, [])
        if not partners:
            PARTNER_WAITING.add(chat_id)
            await update.message.reply_text(
                "🚨 Discipline breach.\nAdd partner (@username)."
            )
            return
        PARTNER_INDEX[chat_id] = (PARTNER_INDEX[chat_id] + 1) % len(partners)
        await update.message.reply_text(
            f"🚨 Switching accountability to {get_current_partner(chat_id)}"
        )
        return

    if no_count == 5:
        mark_proof_expected(chat_id, log_ws)
        await update.message.reply_text("⚠️ 5 misses. Proof required.")
        return

    await update.message.reply_text("Logged. Stay disciplined.")

# ================== BOT START ==================

app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

app.job_queue.run_daily(morning_ping, time=time(hour=7))
app.job_queue.run_daily(night_ping, time=time(hour=22))

app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("✅ Discipline Bot is running...")
app.run_polling()

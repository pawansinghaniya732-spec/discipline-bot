from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Bot is working on Vercel 🚀")

app.add_handler(MessageHandler(filters.TEXT, handle))


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['content-length'])
        body = self.rfile.read(length)
        data = json.loads(body)

        update = Update.de_json(data, app.bot)

        asyncio.run(app.process_update(update))

        self.send_response(200)
        self.end_headers()

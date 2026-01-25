import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

# -------- CONNECT GOOGLE SHEETS --------
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
print("Google Sheets Connected Successfully!")

# -------- OPEN EXISTING MASTER SHEET --------
sheet_name = "Discipline Accountability System"
sheet = client.open(sheet_name)
print("Sheet opened successfully:", sheet_name)

# -------- CREATE / OPEN USERS SHEET --------
users_columns = [
    "user_id",
    "name",
    "whatsapp",
    "goal",
    "fixed_time",
    "partner_number",
    "mode"  # soft / strict
]

try:
    users_ws = sheet.worksheet("Users")
    print("Users Sheet Already Present")
except WorksheetNotFound:
    users_ws = sheet.add_worksheet(
        title="Users",
        rows=1000,
        cols=10
    )
    users_ws.append_row(users_columns)
    print("Users Sheet Created")

# -------- CREATE / OPEN DAILY LOG SHEET --------
log_columns = [
    "date",
    "user_id",
    "morning_task",
    "night_reply",
    "proof_requested",
    "partner_alerted"
]

try:
    log_ws = sheet.worksheet("Daily_Log")
    print("Daily Log Already Present")
except WorksheetNotFound:
    log_ws = sheet.add_worksheet(
        title="Daily_Log",
        rows=5000,
        cols=10
    )
    log_ws.append_row(log_columns)
    print("Daily Log Sheet Created")

# -------- CREATE / OPEN PARTNER ROTATION SHEET --------
rotation_columns = [
    "user_id",
    "failure_count",
    "current_partner",
    "rotated_count"
]

try:
    rotation_ws = sheet.worksheet("Partner_Rotation")
    print("Partner Rotation Sheet Already Present")
except WorksheetNotFound:
    rotation_ws = sheet.add_worksheet(
        title="Partner_Rotation",
        rows=1000,
        cols=10
    )
    rotation_ws.append_row(rotation_columns)
    print("Partner Rotation Sheet Created")

print("STEP-1 Completed Successfully!")

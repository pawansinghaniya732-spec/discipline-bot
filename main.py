import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime

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

# -------- OPEN SHEET --------
sheet = client.open("Discipline Accountability System")
users_ws = sheet.worksheet("Users")
log_ws = sheet.worksheet("Daily_Log")

# -------- LOAD USERS INTO DATAFRAME --------
users = pd.DataFrame(users_ws.get_all_records())

print("Users Loaded:", len(users))


from datetime import datetime

# -------- CURRENT TIME (HH:MM format) --------
now = datetime.now().strftime("%H:%M")

print("Current Time:", now)

# -------- MORNING MESSAGE LOGIC --------
if users.empty:
    print("No users found in Users sheet.")
else:
    for _, user in users.iterrows():
        fixed_time = str(user["fixed_time"]).strip()

        if fixed_time == now:
            message = (
                f"Good morning {user['name']} 👋\n"
                f"In your fixed time slot today, what ONE task will you complete for your goal?"
            )
            print("SEND TO:", user["whatsapp"])
            print("MESSAGE:", message)
            print("-" * 50)

# -------- NIGHT MESSAGE LOGIC --------
night_msg = (
    "Daily discipline check 🔒\n"
    "Did you complete the ONE task you committed to today?\n"
    "Reply only: YES / NO."
)

for _, user in users.iterrows():
    print("SEND TO:", user["whatsapp"])
    print("MESSAGE:", night_msg)
    print("-" * 50)

def get_last_3_logs(chat_id, log_ws):
    records = log_ws.get_all_records()
    user_logs = [
        r for r in records
        if str(r.get("user_id", "")) == str(chat_id)
    ]
    return user_logs[-3:]


def count_no(logs):
    return sum(
        1 for r in logs
        if r.get("night_reply") == "NO"
    )


def mark_proof_expected(chat_id, log_ws):
    rows = log_ws.get_all_values()
    for i in range(len(rows) - 1, 0, -1):
        if rows[i][1] == str(chat_id):
            log_ws.update_cell(i + 1, 5, "Y")  # proof_requested
            break


def proof_expected(chat_id, log_ws):
    records = log_ws.get_all_records()
    for r in reversed(records):
        if str(r.get("user_id", "")) == str(chat_id):
            return r.get("proof_requested") == "Y"
    return False


def is_proof(update):
    if update.message is None:
        return False

    msg = update.message
    if msg.photo or msg.document or msg.voice or msg.video:
        return True

    if msg.text and len(msg.text.strip()) >= 15:
        return True

    return False


def mark_proof_received(chat_id, log_ws):
    rows = log_ws.get_all_values()
    for i in range(len(rows) - 1, 0, -1):
        if rows[i][1] == str(chat_id):
            log_ws.update_cell(i + 1, 5, "R")  # proof_received
            break



def partner_needed(chat_id, log_ws):
    rows = log_ws.get_all_values()

    for i in range(len(rows) - 1, 0, -1):
        # ensure row has required columns
        if len(rows[i]) > 6 and rows[i][1] == str(chat_id):
            # partner abhi tak add nahi hua
            return rows[i][6].strip() == ""   # column G: partner_username

    return False




def save_partner(chat_id, username, log_ws):
    rows = log_ws.get_all_values()

    for i in range(len(rows) - 1, 0, -1):
        # ensure row has at least user_id column
        if len(rows[i]) > 1 and rows[i][1] == str(chat_id):
            # column G (7) = partner_username
            # column F (6) = partner_alerted
            log_ws.update_cell(i + 1, 7, username)
            log_ws.update_cell(i + 1, 6, "Y")
            break



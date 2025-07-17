from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
EXCEL_FILE = 'fuel_log.xlsx'

# Create Excel file if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=['Timestamp', 'From', 'Start', 'End'])
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/sms', methods=['POST'])
def sms_reply():
    msg = request.form.get('Body')
    sender = request.form.get('From')
    resp = MessagingResponse()

    try:
        msg = msg.lower().replace(":", "")
        parts = msg.split()
        start = end = None

        for i, p in enumerate(parts):
            if p == "start":
                start = float(parts[i+1])
            elif p == "end":
                end = float(parts[i+1])

        if start is not None and end is not None:
            df = pd.read_excel(EXCEL_FILE)
            new_row = {
                'Timestamp': datetime.now().isoformat(),
                'From': sender,
                'Start': start,
                'End': end
            }
            df = df.append(new_row, ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)

            resp.message(f"Logged to Excel! Start: {start}, End: {end}")
        else:
            resp.message("Format should be: Start: 1000 End: 1200")
    except Exception as e:
        resp.message(f"Error: {str(e)}")

    return str(resp)

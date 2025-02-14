from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import smtplib
import os

from src.config import email_password
from .data_handler import read_json


def notify():
    """Sends an email to the client email address"""
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Port for TLS
    sender_email, receiver_email = read_json("sender_email", "client_email").values()

    # Creating a multipart message and setting headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Bumi Daily Update"

    # Calculating relevant information and formatting message body
    file = os.path.abspath("../reports/trade_records.csv")
    if os.path.getsize(file) > 0:
        df = pd.read_csv(file)
        old_balance = df.iloc[0]["Old_Balance"]
        new_balance = df.iloc[-1]["New_Balance"]
        trades_closed = len(df)
        profit = new_balance - old_balance
        avg_profit = profit / trades_closed
        roi = (profit/old_balance) * 100
        body = f"""
            Old Balance: {old_balance}
            New Balance: {new_balance}
            Number of trades closed: {trades_closed}
            Total profit: ${profit}
            Average Profit per trade: ${round(avg_profit, 2)}
            Daily ROI: {round(roi, 2)}%"""
        message.attach(MIMEText(body, 'plain'))
    else:
        message.attach(MIMEText("No trades closed today", 'plain'))

    # Connecting to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, email_password)
        # server.send_message(message)
        print("Daily email update sent successfully")
    open(file, "w").close()

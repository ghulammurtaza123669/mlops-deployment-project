"""
notify.py - Send pass/fail email notification via SMTP
            Configure via environment variables (stored as Jenkins credentials)
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# SMTP config — set these as Jenkins secret env vars
SMTP_HOST   = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER   = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASS   = os.getenv("SMTP_PASS", "your-app-password")
NOTIFY_TO   = os.getenv("NOTIFY_TO", "team@example.com")

# Pipeline context
PIPELINE    = os.getenv("PIPELINE_NAME", "Unknown Pipeline")
BUILD_URL   = os.getenv("BUILD_URL", "#")
BUILD_NUM   = os.getenv("BUILD_NUMBER", "0")
GIT_BRANCH  = os.getenv("GIT_BRANCH", "unknown")
STATUS      = sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN"   # PASS or FAIL


def send_email():
    is_pass = STATUS.upper() == "PASS"
    emoji   = "✅" if is_pass else "❌"
    subject = f"{emoji} [{PIPELINE}] Build #{BUILD_NUM} — {'SUCCESS' if is_pass else 'FAILURE'}"

    # Read accuracy if available
    accuracy_line = ""
    try:
        with open("test_result.txt") as f:
            lines = f.read().strip().split("\n")
            if len(lines) >= 2:
                accuracy_line = f"<p><b>Model Accuracy:</b> {lines[1]}</p>"
    except FileNotFoundError:
        pass

    body = f"""
    <html><body>
    <h2 style="color:{'#2ecc71' if is_pass else '#e74c3c'}">{emoji} Pipeline {STATUS.upper()}</h2>
    <table style="font-family:monospace;border-collapse:collapse">
      <tr><td style="padding:4px 12px"><b>Pipeline</b></td><td>{PIPELINE}</td></tr>
      <tr><td style="padding:4px 12px"><b>Build</b></td><td>#{BUILD_NUM}</td></tr>
      <tr><td style="padding:4px 12px"><b>Branch</b></td><td>{GIT_BRANCH}</td></tr>
      <tr><td style="padding:4px 12px"><b>Time</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
    </table>
    {accuracy_line}
    <p><a href="{BUILD_URL}">View full build log →</a></p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_USER
    msg["To"]      = NOTIFY_TO
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, NOTIFY_TO, msg.as_string())
        print(f"[notify] Email sent to {NOTIFY_TO} — {STATUS}")
    except Exception as e:
        print(f"[notify] WARNING: Could not send email: {e}")
        # Don't exit 1 — email failure shouldn't break the pipeline


if __name__ == "__main__":
    send_email()

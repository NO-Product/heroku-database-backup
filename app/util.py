import logging
import os
import gzip
import shutil
from urllib.parse import urlparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

def compress_backup(backup_file):
    """
    Compresses a backup file using gzip.
    
    Parameters:
    backup_file (str): The path of the backup file to be compressed.
    
    Returns:
    bool: True if the compression was successful, False otherwise.
    """
    try:
        with open(backup_file, 'rb') as f_in, gzip.open(backup_file + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        return True
    except FileNotFoundError as e:
        logging.error(f"[compress_backup] Error: File {backup_file} not found.")
        return False
    except Exception as e:
        logging.error(f"[compress_backup] Error compressing backup file: {str(e)}")
        return False

def parse_connection_url(ConnectionUrl):
    """
    Parses a database connection URL and returns the database type and connection details.
    
    Parameters:
    ConnectionUrl (str): The database connection URL to be parsed.
    
    Returns:
    dict: A dictionary containing the database type and connection details.
    """
    url = urlparse(ConnectionUrl)
    return {
        'database_type': url.scheme,
        'hostname': url.hostname,
        'port': url.port,
        'username': url.username,
        'password': url.password,
        'database_name': url.path.lstrip('/')  # remove leading slash
    }

# The `SMTP_CREDENTIALS` JSON object should look like this:
# ```json
# {
#     "smtp_server": "smtp.example.com",
#     "smtp_port": 587,
#     "smtp_username": "username@example.com",
#     "smtp_password": "password"
# }
# ```

def send_email_notification(app_config, subject, message):
    try:
        smtp_credentials = json.loads(app_config.get('SMTP_CREDENTIALS', '{}'))
        recipients = app_config.get('NOTIFY_RECIPIENTS', '').split(',')
        if smtp_credentials and recipients:
            server = smtplib.SMTP(smtp_credentials['smtp_server'], smtp_credentials['smtp_port'])
            server.starttls()
            server.login(smtp_credentials['smtp_username'], smtp_credentials['smtp_password'])
            msg = MIMEMultipart()
            msg['From'] = smtp_credentials['smtp_username']
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server.send_message(msg)
            server.quit()
    except Exception as e:
        logging.error(f"[send_email_notification] Error sending email notification: {str(e)}")

from flask import Flask, request, current_app
import os
import sys
import logging
from .util import compress_backup, parse_connection_url, send_email_notification
from .destinations import s3, ftp
from .db_backups import DB_BACKUP_FUNCTIONS
from .config import get_config_vars
import time
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# Fetch the configuration variables
app.config.update(get_config_vars())

# Fetch LOG_LEVEL from config vars
log_level_str = app.config.get(
    "LOG_LEVEL", "INFO"
)  # Default to 'INFO' if LOG_LEVEL is not set

# Map string log levels to logging constants
log_level_dict = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Get the corresponding logging constant
log_level = log_level_dict.get(
    log_level_str, logging.INFO
)  # Default to logging.INFO if the log level string is not recognized

# Set the log level
logging.basicConfig(level=log_level)


def manual_backup(db_var, label=None):
    db_url = os.getenv(db_var)

    if db_url is None:
        logging.error(f"[manual_backup] Invalid environment variable: {db_var}")
        sys.exit(1)
    elif isinstance(db_url, str) and db_url.startswith(
        ("postgres://", "mysql://", "mssql://", "oracle://")
    ):
        logging.debug(f"[manual_backup] Parsing connection URL: {db_url}")
        details = parse_connection_url(db_url)

        if label and not re.match("^[a-zA-Z0-9_-]*$", label):
            logging.error(f"[manual_backup] Invalid label: {label}")
            sys.exit(1)
        label = label.replace(" ", "-").lower() if label else None

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = (
            f"{label}_{details['database_name']}_{timestamp}"
            if label
            else f"{details['database_name']}_{timestamp}"
        )

        backup_file = None
        for attempt in range(3):
            try:
                backup_file = DB_BACKUP_FUNCTIONS[details["database_type"]](
                    db_url, backup_filename
                )
                logging.debug(
                    f"[manual_backup] Backup file created on attempt {attempt+1}: {backup_file}"
                )
                break
            except Exception as e:
                logging.error(
                    f"[manual_backup] Error creating backup on attempt {attempt+1}: {str(e)}"
                )
                if attempt < 2:  # Don't sleep on the last attempt
                    time.sleep(5)
                else:
                    backup_file = None
                    break

        if backup_file is None:
            logging.error("[manual_backup] Backup creation failed")
            sys.exit(1)

        try:
            logging.debug(f"[manual_backup] Compressing backup file: {backup_file}")
            compression_success = compress_backup(backup_file)
            if not compression_success:
                raise Exception("[manual_backup] Compression failed")
        except Exception as e:
            logging.error(f"[manual_backup] Error compressing backup: {str(e)}")
            sys.exit(1)

        compressed_backup_file = backup_file + ".gz"
        logging.debug(
            f"[manual_backup] Backup file compressed successfully: {compressed_backup_file}"
        )

        upload_success = False
        try:
            logging.debug(
                f"[manual_backup] Uploading compressed backup file: {compressed_backup_file}"
            )
            with open(compressed_backup_file, "rb") as file:
                file_content = file.read()
            if current_app.config["UPLOAD_DESTINATION"] == "S3":
                upload_success = s3.upload_to_destination(
                    compressed_backup_file, file_content
                )
            elif current_app.config["UPLOAD_DESTINATION"] == "FTP":
                upload_success = ftp.upload_to_destination(
                    compressed_backup_file, file_content
                )
        except Exception as e:
            logging.error(f"[manual_backup] Error uploading backup: {str(e)}")
            sys.exit(1)

        if upload_success:
            logging.info(
                f"[manual_backup] Backup upload successful: {compressed_backup_file}"
            )
            # Send email notification
            send_email_notification(
                app.config,
                "Backup Successful",
                f"Backup upload successful: {compressed_backup_file}",
            )
            return compressed_backup_file  # return the backup file name
        else:
            logging.error("[manual_backup] Backup upload failed")
            # Send email notification
            send_email_notification(app.config, "Backup Failed", "Backup upload failed")
            sys.exit(1)
    else:
        logging.error("[manual_backup] Invalid database connection URL")
        # Send email notification
        send_email_notification(
            app.config, "Backup Failed", "Invalid database connection URL"
        )
        sys.exit(1)


def trim_backup_history(db_var, days):
    db_url = os.getenv(db_var)

    if db_url is None:
        logging.error(f"[trim_history] Invalid environment variable: {db_var}")
        sys.exit(1)
    elif isinstance(db_url, str) and db_url.startswith(
        ("postgres://", "mysql://", "mssql://", "oracle://")
    ):
        logging.debug(f"[trim_history] Parsing connection URL: {db_url}")
        details = parse_connection_url(db_url)

        days = int(days)
        cutoff_date = datetime.now() - timedelta(days=days)

        file_list = []
        if current_app.config["UPLOAD_DESTINATION"] == "S3":
            file_list = s3.fetch_destination_filelist()
        elif current_app.config["UPLOAD_DESTINATION"] == "FTP":
            file_list = ftp.fetch_destination_filelist()

        files_to_delete = [
            file
            for file in file_list
            if file.startswith(details["database_name"])
            and datetime.strptime(file.split("_")[-1], "%Y%m%d%H%M%S") < cutoff_date
        ]

        deleted_files = []
        failed_deletes = []
        for file in files_to_delete:
            creation_date = datetime.strptime(file.split("_")[-1], "%Y%m%d%H%M%S")
            days_old = (datetime.now() - creation_date).days
            logging.debug(
                f"# Filename: {file}\nCreated at: {creation_date}\nDays old: {days_old}\n=="
            )
            try:
                if current_app.config["UPLOAD_DESTINATION"] == "S3":
                    s3.delete_file_from_destination(file)
                elif current_app.config["UPLOAD_DESTINATION"] == "FTP":
                    ftp.delete_file_from_destination(file)
                logging.info(f"[trim_history] File deleted successfully: {file}")
                deleted_files.append(file)
            except Exception as e:
                logging.error(
                    f"[trim_history] Error deleting file: {file}, Error: {str(e)}"
                )
                failed_deletes.append(file)

        # Send email notification
        if failed_deletes:
            send_email_notification(
                app.config,
                "Trim History Completed with Errors",
                f"Trim history completed. Deleted files: {deleted_files}, Failed deletes: {failed_deletes}",
            )
        else:
            send_email_notification(
                app.config,
                "Trim History Completed Successfully",
                f"Trim history completed. Deleted files: {deleted_files}",
            )

        return deleted_files, failed_deletes


@app.route("/tasks/manual_backup", methods=["GET"])
def manual_backup_route():
    secret_key = request.args.get("secretKey")
    if not secret_key:
        return "No secret key provided", 403
    if secret_key != os.getenv("SECRET_KEY"):
        return "Invalid secret key", 401
    config_var = request.args.get("configVar")
    label = request.args.get("label")
    backup_file = manual_backup(config_var, label)
    return f"Manual backup completed. Label: {label}, Database: {config_var}, Backup file: {backup_file}"


@app.route("/tasks/trim_history", methods=["GET"])
def trim_history_route():
    secret_key = request.args.get("secretKey")
    if not secret_key:
        return "No secret key provided", 403
    if secret_key != os.getenv("SECRET_KEY"):
        return "Invalid secret key", 401
    config_var = request.args.get("configVar")
    days = request.args.get("days")
    deleted_files, failed_deletes = trim_backup_history(config_var, days)
    return f"Trim history completed. Deleted files: {deleted_files}, Failed deletes: {failed_deletes}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual_backup":
            manual_backup(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        elif sys.argv[1] == "trim_history":
            trim_backup_history(sys.argv[2], sys.argv[3])
        else:
            print(
                "Usage: python app/backup_manager.py [manual_backup|trim_history] [CONFIG_VAR] [LABEL|DAYS]"
            )
            sys.exit(1)
    else:
        app.run(host="0.0.0.0", port=5000)

import os
import logging


def get_config_vars():
    """
    This function fetches all the configuration variables from the Heroku app.
    It reads the environment variables and stores them in a dictionary.
    Returns:
        dict: A dictionary containing all the configuration variables.
    """
    try:
        config_vars = {
            "UPLOAD_DESTINATION": os.getenv("UPLOAD_DESTINATION"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL"),
            "SMTP_CREDENTIALS": os.getenv("SMTP_CREDENTIALS"),
            "NOTIFY_RECIPIENTS": os.getenv("NOTIFY_RECIPIENTS"),
            "FTP_USER": os.getenv("FTP_USER"),
            "FTP_PASS": os.getenv("FTP_PASS"),
            "FTP_HOSTNAME": os.getenv("FTP_HOSTNAME"),
            "FTP_PORT": int(os.getenv("FTP_PORT"))
            if os.getenv("FTP_PORT")
            else 21,  # Default FTP port is 21, convert to integer if FTP_PORT is set
            "FTP_PATH": os.getenv("FTP_PATH"),
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_S3_BUCKET": os.getenv("AWS_S3_BUCKET"),
            "AWS_S3_REGION": os.getenv("AWS_S3_REGION"),
        }
    except Exception as e:
        logging.error(
            f"[get_config_vars] Error fetching configuration variables: {str(e)}"
        )
        return None

    return config_vars

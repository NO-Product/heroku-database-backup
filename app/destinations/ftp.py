import logging
from ftplib import FTP
from flask import current_app



def download_from_destination(file_name):
    """
    This function downloads a file from an FTP server.
    Parameters:
    file_name (str): The name of the file to be downloaded.
    Returns:
    bool: True if file download is successful, False otherwise.
    """
    ftp = FTP(current_app.config["FTP_HOSTNAME"])
    ftp.login(
        user=current_app.config["FTP_USER"], passwd=current_app.config["FTP_PASS"]
    )
    try:
        with open(file_name, "wb") as file:
            ftp.retrbinary("RETR " + file_name, file.write)
        ftp.quit()
        return True
    except Exception as e:
        # Log the error message for debugging purposes
        logging.error(
            f"[download_from_destination] Error downloading file from FTP: {str(e)}"
        )
        return False
    finally:
        if ftp:
            ftp.close()


def upload_to_destination(file_name, file_content):
    """
    This function uploads a file to an FTP server.
    Parameters:
    file_name (str): The name of the file to be uploaded.
    file_content (bytes): The content of the file to be uploaded.
    Returns:
    bool: True if file upload is successful, False otherwise.
    """
    ftp = FTP(current_app.config["FTP_HOSTNAME"])
    ftp.login(
        user=current_app.config["FTP_USER"], passwd=current_app.config["FTP_PASS"]
    )
    try:
        with open(file_name, "rb") as file:
            ftp.storbinary("STOR " + file_name, file)
        ftp.quit()
        return True
    except Exception as e:
        # Log the error message for debugging purposes
        logging.error(f"[upload_to_destination] Error uploading file to FTP: {str(e)}")
        return False
    finally:
        if ftp:
            ftp.close()


def fetch_destination_filelist():
    """
    This function fetches a list of all files from an FTP server.
    Returns:
    list: A list of all file names.
    """
    ftp = FTP(current_app.config["FTP_HOSTNAME"])
    ftp.login(
        user=current_app.config["FTP_USER"], passwd=current_app.config["FTP_PASS"]
    )
    try:
        return ftp.nlst()
    except Exception as e:
        logging.error(
            f"[fetch_destination_filelist] Error fetching file list from FTP: {str(e)}"
        )
        return []
    finally:
        if ftp:
            ftp.close()


def delete_file_from_destination(file_name):
    """
    This function deletes a file from an FTP server.
    Parameters:
    file_name (str): The name of the file to be deleted.
    """
    ftp = FTP(current_app.config["FTP_HOSTNAME"])
    ftp.login(
        user=current_app.config["FTP_USER"], passwd=current_app.config["FTP_PASS"]
    )
    try:
        ftp.delete(file_name)
    except Exception as e:
        logging.error(
            f"[delete_file_from_destination] Error deleting file from FTP: {str(e)}"
        )
    finally:
        if ftp:
            ftp.close()

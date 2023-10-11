import boto3
from botocore.exceptions import NoCredentialsError
from flask import current_app
import logging


def download_from_destination(file_name):
    """
    This function downloads a file from S3.
    Parameters:
    file_name (str): The name of the file to be downloaded.
    Returns:
    bool: True if file download is successful, False otherwise.
    """
    s3 = boto3.client("s3", region_name=current_app.config["AWS_S3_REGION"])
    try:
        s3.download_file(current_app.config["AWS_S3_BUCKET"], file_name, file_name)
        return True
    except NoCredentialsError:
        logging.error(
            "[download_from_destination] No AWS credentials found. Unable to download the file."
        )
        return False
    except Exception as e:
        logging.error(
            f"[download_from_destination] An error occurred while downloading the file: {str(e)}"
        )
        return False


def upload_to_destination(file_name, file_content):
    """
    This function uploads a file to S3.
    Parameters:
    file_name (str): The name of the file to be uploaded.
    file_content (str): The content of the file to be uploaded.
    Returns:
    bool: True if file upload is successful, False otherwise.
    """
    s3 = boto3.client("s3", region_name=current_app.config["AWS_S3_REGION"])
    try:
        s3.put_object(
            Body=file_content, Bucket=current_app.config["AWS_S3_BUCKET"], Key=file_name
        )
        return True
    except NoCredentialsError:
        logging.error(
            "[upload_to_destination] No AWS credentials found. Unable to upload the file."
        )
        return False
    except Exception as e:
        logging.error(f"[upload_to_destination] An error occurred while uploading the file: {str(e)}")
        return False
    
def fetch_destination_filelist():
    """
    This function fetches a list of all files from S3.
    
    Returns:
    list: A list of all file names.
    """
    s3 = boto3.client('s3', region_name=current_app.config['AWS_S3_REGION'])
    try:
        return [obj['Key'] for obj in s3.list_objects(Bucket=current_app.config['AWS_S3_BUCKET'])['Contents']]
    except Exception as e:
        logging.error(f"[fetch_destination_filelist] An error occurred while fetching the file list: {str(e)}")
        return []

def delete_file_from_destination(file_name):
    """
    This function deletes a file from S3.
    
    Parameters:
    file_name (str): The name of the file to be deleted.
    """
    s3 = boto3.client('s3', region_name=current_app.config['AWS_S3_REGION'])
    try:
        s3.delete_object(Bucket=current_app.config['AWS_S3_BUCKET'], Key=file_name)
    except Exception as e:
        logging.error(f"[delete_file_from_destination] An error occurred while deleting the file: {str(e)}")

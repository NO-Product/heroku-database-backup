import subprocess
import os
from datetime import datetime
from ..util import parse_connection_url
import logging

def create_backup_mysql(ConnectionUrl, backup_filename):
    """
    This function creates a backup of a MySQL database.
    
    Parameters:
    ConnectionUrl (str): The connection URL of the MySQL database.
    backup_filename (str): The filename to use for the backup file.
    
    Returns:
    str: The name of the backup file if the backup is successful, False otherwise.
    """
    # Parse the connection URL to get the username, password, host, and database name
    connection_details = parse_connection_url(ConnectionUrl)
    username = connection_details['username']
    password = connection_details['password']
    host = connection_details['hostname']
    dbname = connection_details['database_name']

    # Define the name of the backup file
    backup_file = backup_filename
    # Create a copy of the current environment variables
    env = os.environ.copy()

    # Add the password to the environment variables for the subprocess
    # This is done to avoid exposing the password in the process list
    # The name of the environment variable is constructed based on the database name to avoid conflicts
    env[f'MYSQL_PWD_{dbname.upper()}'] = password

    # Construct the mysqldump command to create a backup of the database
    command = f"mysqldump -u {username} -h {host} {dbname} > {backup_file}"

    # Execute the command
    try:
        result = subprocess.run(command, shell=True, check=False, env=env)
        if result.returncode != 0:
            logging.error(f"[create_backup_mysql] Command failed with return code: {result.returncode}")
            return False
    except subprocess.CalledProcessError as e:
        # Log the error message if the backup creation fails
        logging.error(f"[create_backup_mysql] Error creating backup: {str(e)}")
        return False
    except Exception as e:
        # Log the error message if any other exception occurs
        logging.error(f"[create_backup_mysql] Unexpected error during backup: {str(e)}")
        return False

    # Check if the backup file exists
    if not os.path.isfile(backup_file):
        # Log an error message if the backup file does not exist
        logging.error(f"[create_backup_mysql] Backup file {backup_file} does not exist.")
        return False

    # Return the name of the backup file if the backup is successful
    return backup_file

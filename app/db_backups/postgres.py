import os
import subprocess
from datetime import datetime
from ..util import parse_connection_url
import logging


def create_backup_postgres(ConnectionUrl, backup_filename):
    """
    This function creates a backup of a PostgreSQL database using the `pg_dump` command-line utility.
    The backup file is saved in the current directory with the provided filename.

    Parameters:
    ConnectionUrl (str): The connection URL of the PostgreSQL database.
    backup_filename (str): The filename to use for the backup file.

    Returns:
    str: The name of the backup file if the backup is successful, False otherwise.
    """
    # Parse the connection URL to get the username, password, host, and database name
    connection_details = parse_connection_url(ConnectionUrl)
    database_name = connection_details["database_name"]

    # Use the provided filename for the backup file
    backup_file_name = backup_filename

    # Create a copy of the current environment variables
    env = os.environ.copy()

    # Add the password to the environment variables
    # This is done to avoid exposing the password in the process list
    env["PGPASSWORD"] = connection_details["password"]

    try:
        # Create the backup using `pg_dump`
        result = subprocess.run(
            [
                "pg_dump",
                "-h",
                connection_details["hostname"],
                "-U",
                connection_details["username"],
                "-f",
                backup_file_name,
                "-d",
                database_name,
            ],
            check=False,
            env=env,
        )
        if result.returncode != 0:
            logging.error(
                f"[create_backup_postgres] Error creating backup: {result.stderr}"
            )
            return False
    except Exception as e:
        # Log the error message if any other exception occurs
        logging.error(
            f"[create_backup_postgres] Unexpected error during backup: {str(e)}"
        )
        return False

    # Check if the backup file exists
    if not os.path.isfile(backup_file_name):
        # Log an error message if the backup file does not exist
        logging.error(
            f"[create_backup_postgres] Backup file {backup_file_name} does not exist."
        )
        return False

    # Return the name of the backup file if the backup is successful
    return backup_file_name

# Import the database backup functions from the respective files
from .postgres import create_backup_postgres
from .mysql import create_backup_mysql

# Create a dictionary to map the database system to the respective backup function
DB_BACKUP_FUNCTIONS = {
    'postgres': create_backup_postgres,
    'mysql': create_backup_mysql
}

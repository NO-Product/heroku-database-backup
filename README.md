# Heroku Database Backup Manager

The Heroku Database Backup Manager is a handy tool designed to automate database backups for your Heroku apps. It's a simple Flask app that can be quickly deployed to Heroku and set up to manage backups of any databases attached to your Heroku dynos. 

The primary benefit of using this app is to overcome the limitations of the free and basic tiers of most PostgreSQL and MySQL databases offered via the Heroku marketplace, which do not offer any type of automated backup scheduling. With the Heroku Database Backup Manager, you can schedule regular backups of your databases, ensuring that your data is always safe and recoverable.

## Deployment

1. Click on the `Deploy to Heroku` button in the repository.
2. Fill in the required configuration variables (explained below).
3. Click on `Deploy App`.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/no-product/heroku-database-backup)

## Configuration Variables

- `LOG_LEVEL`: Sets the log level for the application. Possible values are 'DEBUG', 'INFO', 'WARNING', 'ERROR', and 'CRITICAL'. Default is 'INFO'.
- `SECRET_KEY`: A secret key used to validate tasks run via GET requests. The 'secretKey' URL parameter must be set and match this value.
- `UPLOAD_DESTINATION`: Specifies the destination for the backup files. Possible values are 'S3' and 'FTP'.
- `SMTP_CREDENTIALS`: A JSON object containing the SMTP server details for sending email notifications. The object should include 'smtp_server', 'smtp_port', 'smtp_username', and 'smtp_password'.
- `NOTIFY_RECIPIENTS`: A comma-separated list of email addresses to receive backup notifications.
- `FTP_USER`, `FTP_PASS`, `FTP_HOSTNAME`, `FTP_PORT`, `FTP_PATH`: FTP details if 'FTP' is chosen as the `UPLOAD_DESTINATION`.
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, `AWS_S3_REGION`: AWS S3 details if 'S3' is chosen as the `UPLOAD_DESTINATION`.

**The `SMTP_CREDENTIALS` JSON object should look like this:**
```json
{
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "smtp_username": "username@example.com",
    "smtp_password": "password"
}
```

## Usage

The Heroku Database Backup Manager can be used in three different scenarios:

1. **Running from the CLI**: This is useful for ad-hoc backups or when you want to run the tasks manually. You can run the `manual_backup` or `trim_history` commands directly from the command line. The `manual_backup` command requires the `configVar` and an optional `label`. The `trim_history` command requires the `configVar` and the number of `days` to keep backups for.

2. **Running from an external cron-manager**: If you have an external cron manager, you can schedule the tasks to run at specific intervals. The cron manager would make a GET request to the `/tasks/manual_backup` or `/tasks/trim_history` endpoints with the necessary parameters.

3. **Running from Heroku Scheduler**: Heroku Scheduler is a Heroku add-on that allows you to schedule tasks to run at specified intervals. You can set it up to run the `manual_backup` or `trim_history` tasks at your preferred frequency.

### Running from the CLI

For `manual_backup`, use the following command:

```
python app/backup_manager.py manual_backup <configVar> <label>
```

For `trim_history`, use the following command:

```
python app/backup_manager.py trim_history <configVar> <days>
```

Replace `<configVar>` with the environment variable that holds the connection URL for your database. Replace `<label>` with a label of your choice (only for `manual_backup`). Replace `<days>` with the number of days to keep backups for (only for `trim_history`).

### Running from an external cron-manager

To trigger a `manual_backup`, make a GET request to the `/tasks/manual_backup` endpoint with the following parameters:

- `secretKey`: This should match the `SECRET_KEY` environment variable set in your Heroku app settings.
- `configVar`: The environment variable that holds the connection URL for your database.
- `label`: A label that will be prepended to the backup file name (optional).

Example request:

```
https://your-app-name.herokuapp.com/tasks/manual_backup?secretKey=your-secret-key&configVar=DATABASE_URL&label=your-label
```

To trigger a `trim_history`, make a GET request to the `/tasks/trim_history` endpoint with the following parameters:

- `secretKey`: This should match the `SECRET_KEY` environment variable set in your Heroku app settings.
- `configVar`: The environment variable that holds the connection URL for your database.
- `days`: The number of days to keep backups for.

Example request:

```
https://your-app-name.herokuapp.com/tasks/trim_history?secretKey=your-secret-key&configVar=DATABASE_URL&days=30
```

### Running from Heroku Scheduler

1. Navigate to your Heroku Dashboard and select the app you've deployed for the Database Backup Manager.
2. In the `Overview` tab, click on `Configure Add-ons`.
3. In the `Add-ons` search box, type `Scheduler` and select `Heroku Scheduler`.
4. Once the Scheduler has been added, click on it to open the dashboard.
5. Click on `Create Job`.
6. In the `Run Command` field, enter the command for the task you want to run. For example, to run a manual backup, you would enter `/app/tasks/manual_backup?configVar=DATABASE_URL&label=your-label`. Replace `DATABASE_URL` with the config var for your database and `your-label` with a label of your choice.
7. Select the frequency (`Every 10 minutes`, `Hourly`, or `Daily`) and the next run time.
8. Click on `Save Job`.

The job will now run at the specified frequency. You can create multiple jobs to backup different databases or to run backups at different times.


## Frequently Asked Questions

1. **What is the cost associated with using this app?**
   The Heroku Database Backup Manager itself is free to use. However, depending on the resources you use on Heroku (like the dyno size or add-ons like Heroku Scheduler), there may be associated costs. Please refer to Heroku's pricing details for more information.

2. **Is it easy to deploy this app to Heroku?**
   Yes, deploying this app to Heroku is straightforward. We've provided a step-by-step guide in the README to help you through the process. If you're already familiar with Heroku, you should find the process quite simple.

3. **Can I schedule backups for multiple databases with this tool?**
   Yes, you can schedule backups for multiple databases. You just need to set up separate tasks for each database using the Heroku Scheduler.

4. **What types of databases can I generate backups for?**
   Currently, the Heroku Database Backup Manager supports backups for PostgreSQL and MySQL databases. We're open to contributions that add support for other types of databases.

5. **Where can I store the database backups?**
   The app currently supports storing backups in AWS S3 buckets or on an FTP server. You can specify the destination in the configuration variables when you deploy the app.

6. **Is this application secure?**
   Yes, the application uses secure methods for handling sensitive information like database connection details and SMTP credentials. However, as with any application, you should ensure that you follow best practices for security, such as using secure passwords and regularly rotating your credentials.

7. **Can I trigger the tasks using an API request?**
   Yes, the backup tasks are exposed as endpoints in a Flask app, so you can trigger them using an API request. Please refer to the README for more information on the available endpoints and how to use them.

## Contributing

Contributions from other developers are welcome. The codebase is structured as follows:

- `app/config.py`: Fetches configuration variables from the Heroku app.
- `app/util.py`: Contains utility functions for compressing backups, parsing database connection URLs, and sending email notifications.
- `app/destinations/`: Contains modules for handling file uploads and downloads to/from S3 and FTP.
- `app/db_backups/`: Contains modules for creating backups of PostgreSQL and MySQL databases.
- `app/backup_manager.py`: The main Flask app. Handles the backup tasks and routes.

Before contributing, please ensure that you have a good understanding of the functionality and structure of the app. If you have any questions or need further clarification, please feel free to raise an issue in the repository.
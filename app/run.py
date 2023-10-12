from .backup_manager import manual_backup, trim_backup_history
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual_backup":
            manual_backup(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
        elif sys.argv[1] == "trim_history":
            trim_backup_history(sys.argv[2], sys.argv[3])
        else:
            print(
                "Usage: python -m app.run [manual_backup|trim_history] [CONFIG_VAR] [LABEL|DAYS]"
            )
            sys.exit(1)
    else:
        print(
            "Usage: python -m app.run [manual_backup|trim_history] [CONFIG_VAR] [LABEL|DAYS]"
        )
        sys.exit(1)
import subprocess
from datetime import datetime, timedelta
import sys

def run_git_command(date):
    try:
        cmd = ["./git.sh", "-y", str(date.year), "-m", str(date.month).zfill(2), "-d", str(date.day).zfill(2)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        with open("log.txt", "a") as log:
            log.write(f"\n{date.strftime('%Y-%m-%d')} - Status: {'Success' if result.returncode == 0 else 'Failed'}\n")
            if result.stderr:
                log.write(f"Error: {result.stderr}\n")
    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"\n{date.strftime('%Y-%m-%d')} - Error: {str(e)}\n")

def main():
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    current_date = start_date

    while current_date <= end_date:
        run_git_command(current_date)
        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()

import subprocess
from datetime import datetime, timedelta
import os
from git import Repo
import time
from random import randint

def commit_with_date(repo, date):
    try:
        # Check if there are changes to commit
        if not repo.is_dirty(untracked_files=True):
            print("No changes to commit")
            return

        # Format the date string in ISO 8601 format
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add all changes
        repo.git.add('.')
        
        # Set environment variables for the commit
        env = {
            'GIT_AUTHOR_DATE': date_str,
            'GIT_COMMITTER_DATE': date_str
        }
        
        # Commit with the formatted date
        repo.git.commit('-m', f"Update: {date.strftime('%b %d %Y')}", env=env)
        
        # Push changes
        origin = repo.remote(name='origin')
        origin.push()

        # Log the success
        with open("log.txt", "a") as log:
            log.write(f"\n{date.strftime('%Y-%m-%d')} - Status: Success\n")
            
    except Exception as e:
        # Log any errors
        with open("log.txt", "a") as log:
            log.write(f"\n{date.strftime('%Y-%m-%d')} - Error: {str(e)}\n")

def main():
    try:
        repo = Repo('.')
        start_date = datetime(2024, 10, 27)
        end_date = datetime(2024, 11, 30)
        current_date = start_date

        while current_date <= end_date:
            commit_with_date(repo, current_date)
            current_date += timedelta(days=randint(1, 3))
            time.sleep(5)  # 5 second delay between commits

    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"\nScript Error: {str(e)}\n")

if __name__ == "__main__":
    main()

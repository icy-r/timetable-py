from datetime import datetime, timedelta
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
        start_date = datetime(2025, 2, 12)
        end_date = datetime(2025, 3, 1)
        current_date = start_date

        while current_date <= end_date:
            # Random number of commits per day (10-20)
            num_commits = randint(10, 20)
            
            for _ in range(num_commits):
                # Add random hours and minutes to spread commits throughout the day
                commit_time = current_date + timedelta(
                    hours=randint(9, 17),  # Business hours
                    minutes=randint(0, 59)
                )
                commit_with_date(repo, commit_time)
                time.sleep(10)  # 10 second delay between commits
            
            current_date += timedelta(days=randint(1, 3))

    except Exception as e:
        with open("log.txt", "a") as log:
            log.write(f"\nScript Error: {str(e)}\n")

if __name__ == "__main__":
    main()

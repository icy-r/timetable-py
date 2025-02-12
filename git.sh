#!/bin/bash

# Prompt the user for the custom date
read -p "Enter the year (YYYY): " year
read -p "Enter the month (first 3 letters, e.g., Jan, Feb, Mar): " month
read -p "Enter the date (DD): " date

# Construct the custom date
custom_date="$month $date $year 12:00:00"

# Add all files to the staging area
git add .

# Commit the changes with the custom date
GIT_COMMITTER_DATE="$custom_date" git commit --date="$custom_date" -m "Commit with custom date: $custom_date"

# Push the changes to the repository
git push

echo "Changes have been committed and pushed with the custom date: $custom_date"
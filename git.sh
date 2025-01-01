#!/bin/bash

# Initialize variables
year=""
month=""
date=""

# Get command line arguments
while getopts "y:m:d:" flag; do
    case "${flag}" in
        y) year=${OPTARG};;
        m) month=${OPTARG};;
        d) date=${OPTARG};;
    esac
done

# Validate inputs
if [[ -z "$year" || -z "$month" || -z "$date" ]]; then
    echo "Error: All arguments (year, month, date) are required" >&2
    exit 1
fi

# Convert numeric month to month name
month_name=$(date -d "$year-$month-01" +%b 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "Error: Invalid date format" >&2
    exit 1
fi

# Construct the custom date
custom_date="$month_name $date $year 12:00:00"

# Validate if the date is valid
if ! date -d "$custom_date" >/dev/null 2>&1; then
    echo "Error: Invalid date combination" >&2
    exit 1
fi

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit"
    exit 0
fi

# Add and commit changes
if git add . && \
   GIT_COMMITTER_DATE="$custom_date" git commit --date="$custom_date" -m "Update: $custom_date" && \
   git push; then
    echo "Changes committed and pushed successfully for date: $custom_date"
else
    echo "Error: Failed to commit and push changes" >&2
    exit 1
fi
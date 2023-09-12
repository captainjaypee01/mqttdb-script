#!/bin/bash

# Define the target directory where you want to search for old files.
target_directory="/home/azureuser/supervisor_log/"

# Define the threshold date (1 month ago) using the `date` command.
threshold_date=$(date -d "30 days ago" +%Y%m%d)

# Define the name for the zip file.
zip_file="supervisor_backup_files_$(date +%Y%m%d%H%M%S).zip"
zip_folder="/home/azureuser/bak/"

zip_whole_path="$zip_folder$zip_file" 

# Use the `find` command to locate files older than one month.
# -type f: Only search for regular files.
# -ctime +30: Find files with a change time (metadata change) older than 30 days.
# -exec: Execute a command for each found file.
# {} +: Indicates the end of the -exec command.
sudo find "$target_directory" -type f -ctime +30 -name '*.log' -exec zip -r "$zip_whole_path" {} +

#echo "$threshold_date"

# Check if any files were added to the zip file.
if [ -e "$zip_whole_path" ]; then
    echo "Files zipped successfully." 

    # Remove the old files.
    sudo find "$target_directory" -type f -ctime +30 -name '*.log' -exec rm -f {} +

    echo "Old files deleted."
else
    echo "No files found to zip and delete."
fi

import csv
import json
import shutil
import os
from statistics import mean

# Student Information
SEED_DIGIT = 0

# Assigned Parameters
TARGET_OS = "Android"
TARGET_BEHAVIOR_CLASS = (SEED_DIGIT % 5) + 1

print("Target Operating System:", TARGET_OS)
print("Target Behavior Class:", TARGET_BEHAVIOR_CLASS)
# Read Dataset
with open(os.path.join(os.path.dirname(__file__), "..", "user_behavior_dataset.csv"), "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    print("\nDataset Columns:")
    print(reader.fieldnames)

    print("\nFirst 5 Records:")
    for row in list(reader)[:5]:
        print(row)
 # Filter Target Users
with open(os.path.join(os.path.dirname(__file__), "..", "user_behavior_dataset.csv"), "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    filtered_rows = [
        row for row in reader
        if row["Operating System"] == TARGET_OS
        and int(row["User Behavior Class"]) == TARGET_BEHAVIOR_CLASS
    ]

print("\nFiltered Android Users - Behavior Class 1:")
print("Total Matching Users:", len(filtered_rows))

for row in filtered_rows[:5]:
    print(row)  
# Save Filtered Data
if filtered_rows:
    output_file = os.path.join(os.path.dirname(__file__), "filtered_android_users.csv")

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=filtered_rows[0].keys())
        writer.writeheader()
        writer.writerows(filtered_rows)

    print("\nFiltered data saved successfully!")
    print("File:", output_file) 
# Calculate Average
if filtered_rows:
    average_battery = mean(
        float(row["Battery Drain (mAh/day)"])
        for row in filtered_rows
    )

    average_data = mean(
        float(row["Data Usage (MB/day)"])
        for row in filtered_rows
    )

    print("\nAVERAGE RESULTS")
    print("Average Battery Drain:", round(average_battery, 2), "mAh/day")
    print("Average Data Usage:", round(average_data, 2), "MB/day")
# Create Backup
base_dir = os.path.dirname(os.path.abspath(__file__))

backup_folder = os.path.join(base_dir, "backup")
os.makedirs(backup_folder, exist_ok=True)

# Define source files
csv_file = os.path.join(base_dir, "filtered_android_users.csv")
json_file = os.path.join(base_dir, "summary.json")

# Copy files to backup folder
shutil.copy2(
    csv_file,
    os.path.join(backup_folder, "filtered_android_users.csv")
)

shutil.copy2(
    json_file,
    os.path.join(backup_folder, "summary.json")
)

print("\nBackup created successfully!")
print("Backup location:", backup_folder)
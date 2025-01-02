from datetime import datetime, timedelta
import random

# Set base data
base_date = datetime.strptime("2024-08-01", "%Y-%m-%d")
habit_id = 5
number_of_tasks = 1
task_description = "Take an intentional nap in the afternoon"
status = "done"
repeat_type = "daily" # Options: daily, weekly

# Calculate days to add based on repeat type
days_to_add = 7 if repeat_type == "weekly" else 1
total_entries = 5 if repeat_type == "weekly" else 30

print("INSERT INTO task (habit_id, task_number, task_description, created, due_date, status)")
print("VALUES")

for day in range(total_entries):
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    random_time = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    
    current_date = base_date + timedelta(days=day * days_to_add)
    current_with_time = datetime.strptime(
        "{} {}".format(current_date.strftime('%Y-%m-%d'), random_time),
        "%Y-%m-%d %H:%M:%S"
    )
    
    created = current_with_time.strftime('%Y-%m-%d %H:%M:%S')
    due_date = (current_date + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
    
    for task_num in range(1, number_of_tasks + 1):
        is_last = (day == total_entries - 1 and task_num == number_of_tasks)
        ending = ";" if is_last else ","
        print("({}, {}, '{}', '{}', '{}', '{}'){}".format(
            habit_id,
            task_num,
            task_description,
            created, 
            due_date,
            status,
            ending
        ))
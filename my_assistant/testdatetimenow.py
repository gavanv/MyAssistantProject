from datetime import datetime, timedelta

now = datetime.now()

print(f"datetime now object: {now}")

now_str = now.strftime("%d/%m/%y %H:%M")

print(f"datetime now as str: {now_str}")

reminder_time_str = "03/01/2024 9:20"

reminder_time_object = datetime.strptime(reminder_time_str, "%d/%m/%Y %H:%M")

reminder_time = reminder_time_object.strftime("%d/%m/%y %H:%M")

if now_str == reminder_time:
    print("True")

print(f"reminder time object converted to str: {reminder_time}")

print(f"converted str to datetome object: {reminder_time_object}")


next_reminder_time = reminder_time_object + timedelta(days=1)

next_reminder_time_str = next_reminder_time.strftime("%d/%m/%y %H:%M")

print(f"next reminder time: {next_reminder_time}")

print(f"next reminder as str: {next_reminder_time_str}")

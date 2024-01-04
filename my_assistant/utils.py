from datetime import datetime, timedelta
from telegram import InlineKeyboardButton

# functions for arrange the buttons in pairs


def group_buttons(buttons_list):
    result = []
    current_group = []

    for button in buttons_list:
        current_group.extend(button)

        if len(current_group) == 2:
            result.append(current_group)
            current_group = []

    if current_group:
        result.append(current_group)

    return result


def create_keyboard(buttons_list: list) -> list:

    keyboard = [[InlineKeyboardButton(button, callback_data=button)]
                for button in buttons_list]

    return group_buttons(keyboard)


def check_if_time_already_occurred(time_str):

    now = datetime.now()

    now_str = now.strftime("%d/%m/%y %H:%M")

    current_time = datetime.strptime(now_str, "%d/%m/%y %H:%M")

    # Combine the current date with the specified time
    combined_datetime_str = f"{now.strftime('%d/%m/%y')} {time_str}"

    # Convert the combined string to a datetime object
    target_time = datetime.strptime(combined_datetime_str, "%d/%m/%y %H:%M")

    # Check if the target time has already occurred today
    if current_time >= target_time:
        return True
    else:
        return False

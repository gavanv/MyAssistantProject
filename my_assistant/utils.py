from telegram import InlineKeyboardButton

# function for arrange the buttons in pairs


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

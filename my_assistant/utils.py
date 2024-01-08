from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from functools import wraps
from consts import ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD

from exceptions import ClientAlreadyExists, DebtToDeleteIsNegative, IndexIsOutOfRange

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


async def cancel(update, context, keyboard):

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END


def callback_query_errors_handler_decorator(logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)

            except Exception as e:
                logger.exception(f"An error occurred in {func.__name__}: {str(e)}")
                await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי לבצע את הפעולה שרצית.")
                return ConversationHandler.END

        return wrapper
    return decorator


def message_errors_handler_decorator(logger, conversation_state):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)

            except ClientAlreadyExists as e:
                reply_markup = InlineKeyboardMarkup(
                    ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD)
                await update.message.reply_text(text=str(e), reply_markup=reply_markup, parse_mode="markdown")
                return ConversationHandler.END

            except ValueError as e:
                logger.exception(
                    "user send input that cannot be converted to the needed type")
                await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
                return conversation_state

            except IndexIsOutOfRange as e:
                logger.exception(
                    "user send number that is not in the given list.")
                await update.message.reply_text(str(e))
                return conversation_state

            except DebtToDeleteIsNegative as e:
                logger.exception(
                    "the user send negative number of debt to delete")
                await update.message.reply_text(str(e))
                return conversation_state

            except Exception as e:
                logger.exception(f"An error occurred in {func.__name__}: {str(e)}")
                await update.message.reply_text("משהו השתבש😕 לא הצלחתי לבצע את הפעולה שרצית.")
                return ConversationHandler.END

        return wrapper
    return decorator

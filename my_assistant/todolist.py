from logger import setup_logger
import time
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from commands import start
from utils import arrange_text_in_lines, create_keyboard, check_if_time_already_occurred, callback_query_errors_handler_decorator, message_errors_handler_decorator
from db_connection import (db_lock_for_threading, add_task_to_db, delete_reminder_from_db, get_user_all_tasks_from_db,
                           delete_task_from_db, add_reminder_to_db, get_all_reminders, update_reminder_time)
from exceptions import IndexIsOutOfRange
from datetime import datetime, timedelta
from consts import (
    TOKEN,
    TO_DO_LIST_MENU_KEYBOARD,
    TASKS_CATEGORIES,
    ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD,
    DELETE_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD,
    RETURN_TO_TODOLIST_MENU_KEYBOARD,
    FREQUENCIES_FOR_REMINDERS_KEYBOARD,
    ADD_REMINDER_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD,
    WRITE_TASK,
    CHOOSE_LEVEL,
    ADD_TASK,
    CHOOSE_TASK_TO_DELETE,
    DELETE_TASK,
    ASK_FREQUENCY,
    ASK_TIME,
    SET_REMINDER
)
todolist_logger = setup_logger("todolist_logger")

# global dict to store the user_date for adding task
user_data_add_task = {}

# global dict to store the user_date for deleting task
user_data_delete_task = {}

# global dict to store the user_data for seting a reminder
user_data_set_reminder = {}


async def todolist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    reply_markup = InlineKeyboardMarkup(TO_DO_LIST_MENU_KEYBOARD)

    await update.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END


async def return_to_todolist(update, context):

    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(TO_DO_LIST_MENU_KEYBOARD)

    await update.callback_query.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')


# functions for add task conversation
async def add_task_callback(update, context):

    global user_data_add_task

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_data_add_task["user_id"] = user_id

    keyboard = create_keyboard(TASKS_CATEGORIES)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*לאיזה קטגוריה להוסיף משימה?*\n או לחץ /cancel כדי לבטל", 
                                                   reply_markup=reply_markup, parse_mode="markdown")
    return WRITE_TASK


async def write_task(update, context):

    global user_data_add_task

    user_data_add_task["category"] = update.callback_query.data

    await update.callback_query.message.reply_text(text=f"הקלד את המשימה שתרצה להוסיף לקטגוריה: *{user_data_add_task['category']}*\n או לחץ /cancel כדי לבטל",
                                                   parse_mode="markdown")
    return CHOOSE_LEVEL


async def choose_level(update, context):

    global user_data_add_task

    user_details = update.message.from_user
    username = user_details.first_name + " " + user_details.last_name

    user_data_add_task["username"] = username

    user_data_add_task["task"] = update.message.text

    # to prevent telegram error in markdown mode
    if "*" in user_data_add_task["task"]:
        user_data_add_task["task"] = user_data_add_task["task"].replace("*", "")

    keyBoard = [[InlineKeyboardButton("A - משימה דחופה", callback_data="A")],
                [InlineKeyboardButton(
                    "B - משימה חשובה", callback_data="B")],
                [InlineKeyboardButton("C - משימה לא חשובה", callback_data="C")]]

    reply_markup = InlineKeyboardMarkup(keyBoard)

    await update.message.reply_text(text="*מהי רמת הדחיפות של המשימה?*\n או לחץ /cancel כדי לבטל", 
                                    reply_markup=reply_markup, parse_mode="markdown")
    return ADD_TASK


@callback_query_errors_handler_decorator(todolist_logger)
async def add_task(update, context):

    global user_data_add_task

    user_data_add_task["level"] = update.callback_query.data
    
    add_task_to_db(user_data_add_task)

    reply_markup = InlineKeyboardMarkup(
        ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

    await update.callback_query.message.reply_text(text=f"המשימה: *{user_data_add_task['task']}* נוספה בהצלחה לקטגוריה: *{user_data_add_task['category']}*", 
                                                    reply_markup=reply_markup, parse_mode='markdown')
    return ConversationHandler.END


# functions for show all tasks button

@callback_query_errors_handler_decorator(todolist_logger)
async def show_all_tasks_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    tasks_list = get_user_all_tasks_from_db(user_id)

    if len(tasks_list) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text="*לא קיימות משימות ברשימה.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")

    else:

        tasks_list_text = create_tasks_list_text(
            tasks_list, TASKS_CATEGORIES)

        tasks_list_text += "🔚"
        
        lines_list = arrange_text_in_lines(tasks_list_text)

        for i, lines in enumerate(lines_list):
            text = "\n".join(lines)
            if i < len(lines_list) - 1:
                text += "\n*המשך⬇️*\n"
            await update.callback_query.message.reply_text(text=text, parse_mode="markdown")

    return ConversationHandler.END


def create_tasks_list_text(tasks_list, categories):

    result_text = ""

    for category in categories:

        tasks_in_category = list(filter(lambda x: x.get("category") == category, tasks_list))

        if len(tasks_in_category) > 0:

            result_text = result_text + f"*{category}:*\n" + "\n".join([f"{index + 1}. {task.get('task')} ({task.get('level')})" for index, task in enumerate(tasks_in_category)])
            result_text += "\n\n"

    return result_text


# functions for show A,B,C tasks buttons
async def show_level_tasks_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "A_tasks":
        await show_level_tasks(update, context, "A", user_id)

    elif query.data == "B_tasks":
        await show_level_tasks(update, context, "B", user_id)

    else:
        await show_level_tasks(update, context, "C", user_id)


@callback_query_errors_handler_decorator(todolist_logger)
async def show_level_tasks(update, context, level, user_id):

    tasks_list = get_user_all_tasks_from_db(user_id)

    level_tasks_list = list(filter(lambda x: x.get("level") == level, tasks_list))

    if len(level_tasks_list) == 0:

        reply_markup = InlineKeyboardMarkup(ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

        await update.callback_query.message.reply_text(text=f"*לא קיימות משימות {level} ברשימה.*",
                                                        reply_markup=reply_markup,
                                                        parse_mode="markdown")

    else:

        level_tasks_list_text = create_tasks_list_text(tasks_list=level_tasks_list, categories=TASKS_CATEGORIES)

        level_tasks_list_text += "🔚"

        await update.callback_query.message.reply_text(text=level_tasks_list_text,
                                                        parse_mode="markdown")
    return ConversationHandler.END


# functions for delete task conversation
async def delete_task_callback(update,
                               context):

    query = update.callback_query
    await query.answer()

    user_data_delete_task["user_id"] = update.effective_user.id

    keyboard = create_keyboard(TASKS_CATEGORIES)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*מאיזו קטגוריה למחוק משימה?* \nאו לחץ /cancel לביטול.",
                                                   reply_markup=reply_markup,
                                                   parse_mode="markdown")
    return CHOOSE_TASK_TO_DELETE


@callback_query_errors_handler_decorator(todolist_logger)
async def choose_task_to_delete(update, context):

    global user_data_delete_task

    query = update.callback_query
    await query.answer()

    user_data_delete_task["category"] = query.data

    tasks_list = get_user_all_tasks_from_db(user_data_delete_task.get("user_id"))

    category_tasks_list_text = create_tasks_list_text(tasks_list, [user_data_delete_task["category"]])

    category_tasks_list_text += "🔚"

    user_data_delete_task["category_tasks_list"] = list(filter(
        lambda x: x.get("category") == user_data_delete_task["category"], tasks_list))

    if len(user_data_delete_task["category_tasks_list"]) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text=f"*לא קיימות משימות בקטגוריה: {user_data_delete_task['category']}.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")
        return ConversationHandler.END

    else:
        await update.callback_query.message.reply_text(text=f"*הקלד את מספר המשימה שתרצה למחוק:*\n או לחץ /cancel לביטול\n{category_tasks_list_text}", parse_mode="markdown")
        return DELETE_TASK


@message_errors_handler_decorator(todolist_logger, DELETE_TASK)
async def delete_task(update, context):

    global user_data_delete_task

    task_number = int(update.message.text) - 1

    if task_number + 1 > len(user_data_delete_task["category_tasks_list"]) or task_number < 0:
        raise IndexIsOutOfRange()

    task_id_to_delete = (user_data_delete_task["category_tasks_list"][task_number])["id"]

    task_name = (user_data_delete_task["category_tasks_list"][task_number])["task"]

    delete_task_from_db(user_id=user_data_delete_task["user_id"], task_id=task_id_to_delete)

    reply_markup = InlineKeyboardMarkup(DELETE_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

    await update.message.reply_text(text=f"המשימה: *{task_name}* נמחקה בהצלחה.", reply_markup=reply_markup, parse_mode="markdown")

    return ConversationHandler.END


# functions for set reminder conversation

async def set_reminder_callback(update, context):

    query = update.callback_query
    await query.answer()

    await update.callback_query.message.reply_text(text="*הקלד את המשימה שתרצה לקבל עליה תזכורת* \nאו לחץ /cancel לביטול.", 
                                                   parse_mode="markdown")
    return ASK_FREQUENCY


async def ask_frequency(update, context):

    global user_data_set_reminder

    user_details = update.message.from_user
    username = user_details.first_name + " " + user_details.last_name

    user_data_set_reminder["chat_id"] = update.message.chat_id

    user_data_set_reminder["username"] = username

    user_data_set_reminder["user_id"] = user_details.id

    user_data_set_reminder["reminder_text"] = update.message.text

    reply_markup = InlineKeyboardMarkup(FREQUENCIES_FOR_REMINDERS_KEYBOARD)

    await update.message.reply_text(text="*מהי התדירות שתרצה לקבל בה את התזכורת?* \nאו לחץ /cancel לביטול.",
                                    reply_markup=reply_markup,
                                    parse_mode="markdown")
    return ASK_TIME


async def ask_time(update, context):

    global user_data_set_reminder

    query = update.callback_query
    await query.answer()

    user_data_set_reminder["reminder_frequency"] = query.data

    await update.callback_query.message.reply_text(text="*באיזה שעה תרצה לקבל את התזכורת?*\n*בפורמט: XX:YY* \nאו לחץ /cancel לביטול.",
                                                   parse_mode="markdown")
    return SET_REMINDER


@message_errors_handler_decorator(todolist_logger, SET_REMINDER)
async def set_reminder(update, context):

    global user_data_set_reminder

    reminder_time_from_user = update.message.text

    # parse the input as a time with the corrct format, will raise ValueError if the input isn't valid
    parsed_time = datetime.strptime(reminder_time_from_user, "%H:%M")

    now = datetime.now()

    if check_if_time_already_occurred(reminder_time_from_user):

        todolist_logger.debug("the user chose time that was already pass today.")

        timedelta_from_next_reminder = int(user_data_set_reminder.get("reminder_frequency"))

    else:
        timedelta_from_next_reminder = 0

    combined_datetime_str = f"{now.strftime('%d/%m/%y')} {reminder_time_from_user}"

    combined_datetime = datetime.strptime(
        combined_datetime_str, "%d/%m/%y %H:%M")

    next_reminder_time = combined_datetime + timedelta(days=timedelta_from_next_reminder)

    user_data_set_reminder["reminder_time"] = next_reminder_time

    todolist_logger.debug(f"the user set time: {reminder_time_from_user} and the next reminder is on: {user_data_set_reminder['reminder_time']}")

    add_reminder_to_db(user_data_set_reminder)

    reply_markup = InlineKeyboardMarkup(ADD_REMINDER_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

    await update.message.reply_text(text=f"התזכורת: *{user_data_set_reminder['reminder_text']}* נוספה בהצלחה.",
                                    reply_markup=reply_markup,
                                    parse_mode="markdown")
    return ConversationHandler.END


async def reminder_bot_message():

    while True:

        # get all of the reminders from the db
        reminders_list = get_all_reminders()
        now = datetime.now()

        for reminder in reminders_list:
            reminder_data = {}
            reminder_data["user_id"] = reminder.get("user_id")
            reminder_data["task"] = reminder.get("reminder_text")
            reminder_data["frequency"] = reminder.get("reminder_frequency")
            reminder_data["time"] = reminder.get("reminder_time")
            reminder_data["chat_id"] = reminder.get("chat_id")

            reminder_time_str = str(reminder_data["time"])

            # Format current date and time as DD/MM/YY HH:MM:SS
            current_datetime_str = now.strftime("%d/%m/%y %H:%M")

            reminder_time_str = reminder_data["time"].strftime(
                "%d/%m/%y %H:%M")

            # todolist_logger.debug(f"current time: {current_datetime_str}")
            # todolist_logger.debug(f"reminder time: {reminder_time_str}")

            # Check if it's time to send a reminder
            if current_datetime_str == reminder_time_str:
                todolist_logger.debug("the time for reminder is now")
                # Send reminder to the user
                bot = Bot(token=TOKEN)

                TASK_DONE_OR_KEEP_REMINDER_KEYBOARD = [
                    [
                        InlineKeyboardButton("המשימה בוצעה✅ - עצירת תזכורת",
                                             callback_data="task_is_done:" + reminder_data["task"])
                    ],
                    [InlineKeyboardButton("המשימה לא בוצעה❌ - המשך להזכיר לי",
                                          callback_data="task_is_not_done:" + reminder_data["task"])
                     ]
                ]

                reply_markup = InlineKeyboardMarkup(
                    TASK_DONE_OR_KEEP_REMINDER_KEYBOARD)

                await bot.send_message(chat_id=reminder_data["chat_id"], text=f"*תזכורת:* {reminder_data['task']}",
                                       reply_markup=reply_markup, parse_mode="markdown")

                # Update reminder for the next occurrence based on frequency
                if reminder_data["frequency"] == "1":
                    next_reminder_time = now + timedelta(days=1)

                elif reminder_data["frequency"] == "7":
                    next_reminder_time = now + timedelta(days=7)
                elif reminder_data["frequency"] == "30":
                    """approximation for simplicity - the purpose of the bot is not
                    to give a specific reminder in date and time, but a general one.
                    """
                    next_reminder_time = now + timedelta(days=30)

                reminder_data["time"] = next_reminder_time

                update_reminder_time(reminder_data)

        time.sleep(5)

@callback_query_errors_handler_decorator(todolist_logger)
async def reply_to_reminder_message(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # the callback data is: "task_is_done:" + task as str or: "task_is_not_done" + task as str
    callback_data_parts = (query.data).split(":")

    task_reminder = callback_data_parts[1]

    if "task_is_not_done" in callback_data_parts:

        reply_markup = InlineKeyboardMarkup(RETURN_TO_TODOLIST_MENU_KEYBOARD)

        await update.callback_query.message.reply_text(text=f"אמשיך להזכיר לך את המשימה: *{task_reminder}*.", reply_markup=reply_markup, parse_mode="markdown")

    else:

        reply_markup = InlineKeyboardMarkup(RETURN_TO_TODOLIST_MENU_KEYBOARD)

        delete_reminder_from_db(user_id, task_reminder)

        await update.callback_query.message.reply_text(text=f"המשימה: *{task_reminder}* בוצעה✅ התזכורת למשימה זו נמחקה.", 
                                                        reply_markup=reply_markup, parse_mode="markdown")


# cancel function for to do list menu
async def cancel_for_todolist_conv(update, context):

    reply_markup = InlineKeyboardMarkup(RETURN_TO_TODOLIST_MENU_KEYBOARD)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END


# conversation handler for add task button
add_task_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_task_callback, pattern='^add_task$')],
    states={
        WRITE_TASK: [CallbackQueryHandler(write_task)],
        CHOOSE_LEVEL: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, choose_level)],
        ADD_TASK: [CallbackQueryHandler(add_task)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_todolist_conv)],
    allow_reentry=True)

# call back handler for show all tasks button
show_all_tasks_handler = CallbackQueryHandler(
    show_all_tasks_callback, pattern='^show_todo_list$')

# call back handler for show A/B/C tasks buttons
show_level_tasks_handler = CallbackQueryHandler(
    show_level_tasks_callback, pattern='^(A|B|C)_tasks$')

# conversation handler for delete task button
delete_task_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_task_callback, pattern='^delete_task$')],
    states={
        CHOOSE_TASK_TO_DELETE: [CallbackQueryHandler(choose_task_to_delete)],
        DELETE_TASK: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, delete_task)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_todolist_conv)],
    allow_reentry=True)

# set reminder conv handler
set_reminder_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(set_reminder_callback, pattern='^set_reminder$')],
    states={
        ASK_FREQUENCY: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, ask_frequency)],
        ASK_TIME: [CallbackQueryHandler(ask_time)],
        SET_REMINDER: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, set_reminder)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_todolist_conv)],
    allow_reentry=True)

return_to_todolist_handler = CallbackQueryHandler(
    return_to_todolist, pattern="^return_to_todolist$")

reply_to_reminder_message_handler = CallbackQueryHandler(
    reply_to_reminder_message, pattern="^task_is")


todolist_features_handlers = [CommandHandler("todolist", todolist_command), MessageHandler(
    filters.Regex("ניהול משימות"), todolist_command), add_task_conv_handler,
    return_to_todolist_handler, show_all_tasks_handler, show_level_tasks_handler,
    delete_task_conv_handler, set_reminder_conv_handler, reply_to_reminder_message_handler]

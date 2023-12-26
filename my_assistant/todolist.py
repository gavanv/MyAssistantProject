from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from commands import start
from utils import create_keyboard
from db_connection import add_task_to_db, get_user_all_tasks_from_db, delete_task_from_db, add_reminder_to_db
from exceptions import IndexIsOutOfRange
from consts import (
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

    await update.callback_query.message.reply_text(text="*לאיזה קטגוריה להוסיף משימה?*\n או לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode="markdown")
    return WRITE_TASK


async def write_task(update, context):

    global user_data_add_task

    user_data_add_task["category"] = update.callback_query.data

    await update.callback_query.message.reply_text(text=f"הקלד את המשימה שתרצה להוסיף לקטגוריה: *{user_data_add_task["category"]}*\n או לחץ /cancel כדי לבטל",
                                                   parse_mode="markdown")
    return CHOOSE_LEVEL


async def choose_level(update, context):

    global user_data_add_task

    user_details = update.message.from_user
    username = user_details.first_name + " " + user_details.last_name

    user_data_add_task["username"] = username

    user_data_add_task["task"] = update.message.text

    keyBoard = [[InlineKeyboardButton("A - משימה דחופה", callback_data="A")],
                [InlineKeyboardButton(
                    "B - משימה חשובה", callback_data="B")],
                [InlineKeyboardButton("C - משימה לא חשובה", callback_data="C")]]

    reply_markup = InlineKeyboardMarkup(keyBoard)

    await update.message.reply_text(text="*מהי רמת הדחיפות של המשימה?*\n או לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode="markdown")
    return ADD_TASK


async def add_task(update, context):

    global user_data_add_task

    user_data_add_task["level"] = update.callback_query.data

    try:
        add_task_to_db(user_data_add_task)

        reply_markup = InlineKeyboardMarkup(
            ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

        await update.callback_query.message.reply_text(text=f"המשימה: <b>{user_data_add_task["task"]}</b> נוספה בהצלחה לקטגוריה: <b>{user_data_add_task["category"]}</b>", reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        todolist_logger.exception(str(e))
        await update.callback_query.message.reply_text(text="משהו השתבש😕 לא הצלחתי להוסיף את המשימה שלך לרשימת המשימות.")

    finally:
        return ConversationHandler.END


# functions for show all tasks button
async def show_all_tasks_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        tasks_list = get_user_all_tasks_from_db(user_id)

        if len(tasks_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="*לא קיימות משימות ברשימה.*", reply_markup=reply_markup, parse_mode="markdown")

        else:

            tasks_list_text = create_tasks_list_text(
                tasks_list, TASKS_CATEGORIES)

            tasks_list_text += "🔚"

            await update.callback_query.message.reply_text(text=tasks_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת המשימות שלך")

    finally:
        return ConversationHandler.END


def create_tasks_list_text(tasks_list, categories):

    result_text = ""

    for category in categories:

        tasks_in_category = list(
            filter(lambda x: x.get("category") == category, tasks_list))

        if len(tasks_in_category) > 0:

            result_text = result_text + f"*{category}:*\n" + "\n".join([f"{index + 1}. {
                                                                       task.get("task")} ({task.get("level")})" for index, task in enumerate(tasks_in_category)])
            result_text += "\n\n"

    return result_text


# functions for show A,B,C tasks buttons
async def show_A_tasks_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        tasks_list = get_user_all_tasks_from_db(user_id)

        A_tasks_list = list(
            filter(lambda x: x.get("level") == "A", tasks_list))

        if len(A_tasks_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="*לא קיימות משימות A ברשימה.*", reply_markup=reply_markup, parse_mode="markdown")

        else:

            A_tasks_list_text = create_tasks_list_text(
                A_tasks_list, TASKS_CATEGORIES)

            A_tasks_list_text += "🔚"

            await update.callback_query.message.reply_text(text=A_tasks_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת המשימות ברמה A שלך.")

    finally:
        return ConversationHandler.END


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


async def show_level_tasks(update,
                           context,
                           level,
                           user_id):

    try:
        tasks_list = get_user_all_tasks_from_db(user_id)

        level_tasks_list = list(
            filter(lambda x: x.get("level") == level, tasks_list))

        if len(level_tasks_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text=f"*לא קיימות משימות {level} ברשימה.*",
                                                           reply_markup=reply_markup,
                                                           parse_mode="markdown")

        else:

            level_tasks_list_text = create_tasks_list_text(
                level_tasks_list, TASKS_CATEGORIES)

            level_tasks_list_text += "🔚"

            await update.callback_query.message.reply_text(text=level_tasks_list_text,
                                                           parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text(f"משהו השתבש😕 לא הצלחתי למצוא את רשימת המשימות ברמה {level} שלך.")

    finally:
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


async def choose_task_to_delete(update, context):

    global user_data_delete_task

    query = update.callback_query
    await query.answer()

    user_data_delete_task["category"] = query.data

    try:
        tasks_list = get_user_all_tasks_from_db(
            user_data_delete_task.get("user_id"))
        category_tasks_list_text = create_tasks_list_text(
            tasks_list, [user_data_delete_task["category"]])

        category_tasks_list_text += "🔚"

        user_data_delete_task["category_tasks_list"] = list(filter(
            lambda x: x.get("category") == user_data_delete_task["category"], tasks_list))

        if len(user_data_delete_task["category_tasks_list"]) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text=f"*לא קיימות משימות בקטגוריה: {user_data_delete_task["category"]}.*", reply_markup=reply_markup, parse_mode="markdown")
            return ConversationHandler.END

        else:
            await update.callback_query.message.reply_text(text=f"*הקלד את מספר המשימה שתרצה למחוק:*\n או לחץ /cancel לביטול\n{category_tasks_list_text}", parse_mode="markdown")
            return DELETE_TASK

    except Exception as e:
        todolist_logger.exception(
            "unable to show the list of tasks in the chosen category.")
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי להציג את המשימות בקטגוריה שבחרת.")
        return ConversationHandler.END


async def delete_task(update, context):

    global user_data_delete_task

    try:
        task_number = int(update.message.text) - 1

        if task_number + 1 > len(user_data_delete_task["category_tasks_list"]) or task_number < 0:
            raise IndexIsOutOfRange()

        task_id_to_delete = (
            user_data_delete_task["category_tasks_list"][task_number])["id"]

        task_name = (user_data_delete_task["category_tasks_list"][task_number])[
            "task"]

        delete_task_from_db(
            user_id=user_data_delete_task["user_id"], task_id=task_id_to_delete)

        reply_markup = InlineKeyboardMarkup(
            DELETE_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
        await update.message.reply_text(text=f"המשימה: *{task_name}* נמחקה בהצלחה.", reply_markup=reply_markup, parse_mode="markdown")
        return ConversationHandler.END

    except ValueError as e:
        todolist_logger.exception(
            "user send task number to delete that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return DELETE_TASK

    except IndexIsOutOfRange as e:
        todolist_logger.exception(
            "user send number that is not in the list of tasks")
        await update.message.reply_text(str(e))
        return DELETE_TASK

    except Exception as e:
        todolist_logger.exception(
            "unable to delete task from the chosen category.")
        await update.message.reply_text("משהו השתבש😕 לא הצלחתי למחוק את המשימה שבחרת.")
        return ConversationHandler.END


# functions for set reminder conversation
async def set_reminder_callback(update, context):

    query = update.callback_query
    await query.answer()

    await update.callback_query.message.reply_text(text="*הקלד את המשימה שתרצה לקבל עליה תזכורת* \nאו לחץ /cancel לביטול.", parse_mode="markdown")
    return ASK_FREQUENCY


async def ask_frequency(update, context):

    global user_data_set_reminder

    user_details = update.message.from_user
    username = user_details.first_name + " " + user_details.last_name

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


async def set_reminder(update, context):

    global user_data_set_reminder

    try:

        user_data_set_reminder["reminder_time"] = update.message.text

        add_reminder_to_db(user_data_set_reminder)

        reply_markup = InlineKeyboardMarkup(
            ADD_REMINDER_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)

        await update.message.reply_text(text=f"התזכורת: *{user_data_set_reminder["reminder_text"]}* נוספה בהצלחה.", reply_markup=reply_markup, parse_mode="markdown")

    except Exception as e:
        todolist_logger.exception(str(e))
        await update.message.reply_text("משהו השתבש😕 לא הצלחתי להוסיף את התזכורת.")

    finally:
        return ConversationHandler.END


# cancel function for to do list menu
async def cancel(update, context):

    reply_markup = InlineKeyboardMarkup(RETURN_TO_TODOLIST_MENU_KEYBOARD)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END


# conversation handler for add task button
add_task_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        add_task_callback, pattern='^add_task$')],
    states={
        WRITE_TASK: [CallbackQueryHandler(write_task)],
        CHOOSE_LEVEL: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, choose_level)],
        ADD_TASK: [CallbackQueryHandler(add_task)]
    },
    fallbacks=[CommandHandler("start", start),
               CommandHandler("cancel", cancel)],
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
    fallbacks=[CommandHandler("start", start),
               CommandHandler("cancel", cancel)],
    allow_reentry=True)


# set reminder conv handler
set_reminder_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        set_reminder_callback, pattern='^set_reminder$')],
    states={
        ASK_FREQUENCY: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, ask_frequency)],
        ASK_TIME: [CallbackQueryHandler(ask_time)],
        SET_REMINDER: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, set_reminder)]
    },
    fallbacks=[CommandHandler("start", start),
               CommandHandler("cancel", cancel)],
    allow_reentry=True)


return_to_todolist_handler = CallbackQueryHandler(
    return_to_todolist, pattern="^return_to_todolist$")


todolist_features_handlers = [CommandHandler("todolist", todolist_command), MessageHandler(
    filters.Regex("ניהול משימות"), todolist_command), add_task_conv_handler,
    return_to_todolist_handler, show_all_tasks_handler, show_level_tasks_handler,
    delete_task_conv_handler, set_reminder_conv_handler]

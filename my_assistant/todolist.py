from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from commands import start
from utils import create_keyboard
from db_connection import add_task_to_db, get_user_all_tasks_from_db
from consts import (
    TO_DO_LIST_MENU_KEYBOARD,
    TASKS_CATEGORIES,
    ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD,
    RETURN_TO_TODOLIST_MENU_KEYBOARD,
    WRITE_TASK,
    CHOOSE_LEVEL,
    ADD_TASK
)
todolist_logger = setup_logger("todolist_logger")

# global dict to store the user_date for adding task
user_data_add_task = {}

# global dict to store the user_date for deleting task
user_data_delete_task = {}


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

            tasks_list_text = create_tasks_list_text(tasks_list, TASKS_CATEGORIES)

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


# function for delete task conversation
async def delete_task_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_data_delete_task["user_id"] = update.effective_user.id

    keyboard = create_keyboard(TASKS_CATEGORIES)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*מאיזו קטגוריה למחוק משימה?*", reply_markup=reply_markup, parse_mode="markdown")
    return CHOOSE_TASK_TO_DELETE


async def choose_task_to_delete(update, context):

    query = update.callback_query
    await query.answer()

    user_data_delete_task["category"] = query.data

    try:
        tasks_list = get_user_all_tasks_from_db(user_data_delete_task.get("user_id"))

        if len(tasks_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="*לא קיימות משימות ברשימה.*", reply_markup=reply_markup, parse_mode="markdown")

        else:
            category_tasks_list_text = create_tasks_list_text(tasks_list, [user_data_delete_task["category"]])
            await update.callback_query.message.reply_text(text=f"*הקלד את מספר המשימה שתרצה למחוק:*\n או לחץ /cancel לביטול\n{category_tasks_list_text}")
    
    except Exception as e:
        


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

# conversation handler for delete task button
delete_task_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_task_callback, pattern='^delete_task$')],
    states={
        CHOOSE_TASK_TO_DELETE: [CallbackQueryHandler(write_task)],
        DELETE_TASK: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, choose_level)],
        ADD_TASK: [CallbackQueryHandler(add_task)]
    },
    fallbacks=[CommandHandler("start", start),
               CommandHandler("cancel", cancel)],
    allow_reentry=True)

return_to_todolist_handler = CallbackQueryHandler(
    return_to_todolist, pattern="^return_to_todolist$")


todolist_features_handlers = [CommandHandler("todolist", todolist_command), MessageHandler(
    filters.Regex("ניהול משימות"), todolist_command), add_task_conv_handler, return_to_todolist_handler, show_all_tasks_handler, delete_task_conv_handler]

from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from db_connection import add_client_to_database, get_user_clients_from_database, get_ten_clients_from_database, delete_client_from_database
from consts import (
    ADD_CLIENT_FULL_NAME,
    ADD_CLIENT_ADDRESS,
    ADD_ANOTHER_CLIENT,
    ASK_IF_DELETE,
    CLIENTS_PER_PAGE,
    DELETE_OR_NOT_CLIENT,
    DELETE_ANOTHER_CLIENT
)
from commands import start

clients_logger = setup_logger("clients_logger")

# dict to store the user_data
user_data = {}


async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
            InlineKeyboardButton(
                "מחיקת לקוח", callback_data="delete_client"),
            InlineKeyboardButton("הוספת לקוח", callback_data="add_client"),
        ],
        [InlineKeyboardButton("add debt", callback_data="add debt"),
         InlineKeyboardButton("delete debt", callback_data="delete debt"),
         InlineKeyboardButton("show all debts", callback_data="show all debts")],
        [InlineKeyboardButton("רשימת לקוחות",
                              callback_data="show_clients_list")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END

# functions for add client conversation


async def add_client_callback(update: Update, context: CallbackContext) -> int:

    query = update.callback_query

    await query.answer()
    await update.callback_query.message.reply_text(text="*מה השם המלא של הלקוח/ה?*\nלביטול הפעולה לחץ /cancel",
                                                   parse_mode="markdown", reply_markup=ReplyKeyboardRemove())
    return ADD_CLIENT_FULL_NAME


async def add_client_full_name(update: Update, context: CallbackContext) -> int:

    global user_data

    user_details = update.message.from_user
    user_id = user_details.id
    username = user_details.first_name + " " + user_details.last_name
    full_name = update.message.text

    user_data["user_id"] = user_id
    user_data["username"] = username
    user_data["full_name"] = full_name

    await update.message.reply_text(text="*מה הכתובת של הלקוח/ה?*\nלביטול הפעולה לחץ /cancel", parse_mode="markdown")
    return ADD_CLIENT_ADDRESS


async def add_client_address(update: Update, context: CallbackContext) -> int:

    global user_data

    address = update.message.text
    user_data["address"] = address

    keyboard = [["כן", "לא"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    try:
        add_client_to_database(user_data)
        # Ask if the user wants to add another client
        await update.message.reply_text(f'לקוח נוסף בהצלחה🥳 האם תרצה להוסיף עוד לקוח?', reply_markup=reply_markup, parse_mode='HTML')
        return ADD_ANOTHER_CLIENT

    except KeyError as e:
        await update.message.reply_text(text=f"{str(e)} לחזרה לתפריט לחץ /clients")
        return ADD_CLIENT_FULL_NAME

    except Exception as e:
        await update.message.reply_text(text=f"{str(e)} לחזרה לתפריט לחץ /clients")
        return ConversationHandler.END


async def add_another_client(update: Update, context: CallbackContext) -> int:
    global user_data
    user_choice = update.message.text.lower()

    if user_choice == "כן":
        # User wants to add another client, reset data and go back to full name state
        clients_logger.debug(user_data)
        user_data = {}
        await update.message.reply_text(
            "*הוספת לקוח חדש:* מה השם המלא של הלקוח?", parse_mode="markdown")
        return ADD_CLIENT_FULL_NAME

    else:
        # User does not want to add another client, end the conversation
        await update.message.reply_text("לחזרה לתפריט הלקוחות לחץ /clients או לחץ /start כדי להתחיל מחדש")
        return ConversationHandler.END


# callback for the "show clients list" button in the clients menu
async def show_clients_callback(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()
    # get the user id
    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_database(user_id)

        if len(clients_list) == 0:
            keyboard = [[InlineKeyboardButton(
                "הוספת לקוח", callback_data="add_client")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.message.reply_text(text="אין לך לקוחות קיימים ברשימה. לחזרה לתפריט לקוחות לחץ /clients או הוסף לקוח חדש", reply_markup=reply_markup, parse_mode='HTML')

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client['full_name']} - {
                                          client['address']}" for index, client in enumerate(clients_list)])
            clients_list_text += "\n🔚"
            await update.callback_query.message.reply_text(text="*רשימת לקוחות:*\n" + clients_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך")

    finally:
        return ConversationHandler.END


def create_clients_buttons(clients_list, page):
    clients_buttons = []
    for client in clients_list:
        clients_buttons.append([InlineKeyboardButton(
            client["full_name"], callback_data="clientId:"+str(client["id"])+":clientName:" + client["full_name"])])

    if CLIENTS_PER_PAGE <= len(clients_buttons):
        clients_buttons.append([InlineKeyboardButton(
            "next", callback_data="nextPage:" + str(page+1))])

    return clients_buttons


async def delete_client_callback(update, context):

    query = update.callback_query
    await query.answer()

    # get the user id
    user_id = update.effective_user.id

    try:
        clients_list = get_ten_clients_from_database(user_id, offset=0)
        keyboard = create_clients_buttons(clients_list, page=0)

        # clients_logger.debug(keyboard)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text("*איזה לקוח/ה למחוק?*\nאו לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode='Markdown')

    except Exception:
        clients_logger.exception(
            "can't show buttons with names of client to delete")
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך.")

    return ASK_IF_DELETE


async def ask_if_delete(update, context):

    query = update.callback_query
    await query.answer()

    # get the client Id
    client_id = (query.data.split(":"))[1]

    # get the client name
    client_name = (query.data.split(":"))[3]

    keyboard = [[
        InlineKeyboardButton("כן", callback_data="yes_clientId:" +
                             client_id + ":yes_clientName:" + client_name),
        InlineKeyboardButton(
                "לא", callback_data="no_clientId:" + client_id + ":no_clientName:" + client_name),
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text=f"*האם אתה בטוח שברצונך למחוק את הלקוח/ה: {client_name}?*", reply_markup=reply_markup, parse_mode='markdown')

    return DELETE_OR_NOT_CLIENT


async def delete_or_not_client(update, context):

    query = update.callback_query
    await query.answer()

    # get the user id
    user_id = update.effective_user.id

    # get the client Id
    client_id = (query.data.split(":"))[1]

    # get the client name
    client_name = (query.data.split(":"))[3]

    keyboard = [["כן", "לא"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if "yes" in query.data:
        try:
            delete_client_from_database(user_id, client_id)
            await update.callback_query.message.reply_text(text=f"הלקוח/ה {client_name} נמחקה/ה בהצלחה. האם למחוק עוד לקוח?", reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            await update.callback_query.message.reply_text(".משהו השתבש😕 לא הצלחתי למחוק את הלקוח שבחרת", parse_mode='Markdown')
            return ConversationHandler.END

    else:
        await update.callback_query.message.reply_text(text=f"הלקוח/ה {client_name} לא נמחק/ה. האם למחוק לקוח אחר?")

    return DELETE_ANOTHER_CLIENT


async def delete_another_client(update, context):

    user_id = update.message.from_user.id
    user_choice = update.message.text

    if user_choice == "כן":

        user_id = update.message.from_user.id

        try:
            clients_list = get_ten_clients_from_database(user_id, offset=0)
            keyboard = create_clients_buttons(clients_list, page=0)

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text("*איזה לקוח/ה למחוק?*\nאו לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode='Markdown')
            return ASK_IF_DELETE

        except Exception:
            clients_logger.exception(
                "can't show buttons with names of client to delete")
            await update.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך.")
            return ConversationHandler.END

    else:
        # User does not want to delete another client, end the conversation
        await update.message.reply_text("לחזרה לתפריט הלקוחות לחץ /clients או לחץ /start כדי להתחיל מחדש")
        return ConversationHandler.END


async def next_page(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # get the page number according to the call back button next
    page = int((query.data.split(":"))[1])

    try:
        clients_list = get_ten_clients_from_database(
            user_id=user_id, offset=CLIENTS_PER_PAGE*page)
        keyboard = create_clients_buttons(clients_list, page=page)

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.message.reply_text("*איזה לקוח/ה למחוק?*\nאו לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode='Markdown')

    except Exception:
        clients_logger.exception(
            "can't show buttons with names of client to delete")
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך.")
        return ConversationHandler.END

    return ASK_IF_DELETE


# Define the cancel command to end the conversation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(text="*הפעולה בוטלה.* לחץ /start אם תצטרך את עזרתי במשהו נוסף 🙂", parse_mode="markdown")
    return ConversationHandler.END


# Conversation handler for adding a client to the db
add_client_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        add_client_callback, pattern='^add_client$')],
    states={
        ADD_CLIENT_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_full_name)],
        ADD_CLIENT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_client_address)],
        ADD_ANOTHER_CLIENT: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, add_another_client)]
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start),
               CommandHandler("clients", clients_command)])

# handler for pressing the show clients list button in the clients menu
show_clients_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        show_clients_callback, pattern='^show_clients_list$')],
    states={},
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command)])


# Conversation handler for deleting client from the db
delete_client_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_client_callback, pattern='^delete_client$')],
    states={
        ASK_IF_DELETE: [CallbackQueryHandler(ask_if_delete, pattern='^clientId:')],
        DELETE_OR_NOT_CLIENT: [CallbackQueryHandler(
            delete_or_not_client, pattern='^(yes|no)')],
        DELETE_ANOTHER_CLIENT: [MessageHandler(
            filters.Regex("^(כן|לא)"), delete_another_client)]
    },
    fallbacks=[CallbackQueryHandler(next_page, pattern='^nextPage:'), CommandHandler('cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command)])

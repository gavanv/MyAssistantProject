from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from db_connection import add_client_to_db, get_user_clients_from_db, get_ten_clients_from_db, delete_client_from_db, add_debt_to_db, delete_debt_from_db
from consts import (
    CLIENTS_MENU_KEYBOARD,
    ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD,
    ADD_DEBT_OR_RETURN_TO_CLIENTS_MENU_KEYBOARD,
    RETURN_TO_CLIENTS_MENU_KEYBOARD,
    ADD_CLIENT_FULL_NAME,
    ADD_CLIENT_ADDRESS,
    ADD_ANOTHER_CLIENT,
    ASK_IF_DELETE,
    CLIENTS_PER_PAGE,
    DELETE_OR_NOT_CLIENT,
    DEBT_AMOUNT_TO_ADD,
    ADD_DEBT,
    ASK_AMOUNT_TO_DELETE,
    DELETE_ALL_DEBT,
    DELETE_PART_DEBT,
    SEND_LINK
)
from commands import start
from urllib.parse import quote
from exceptions import ClientAlreadyExists, IndexOfClientIsTooBig

clients_logger = setup_logger("clients_logger")

# global dict to store the user data for add client conversation
user_data = {}

# global variabels for add debt conversation
client_number_to_add_debt = 0
clients_list_len_in_add_debt = 0

# global dict to store the data for delete debt conversation
delete_debt_data = {}


async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    reply_markup = InlineKeyboardMarkup(CLIENTS_MENU_KEYBOARD)

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
        add_client_to_db(user_data)
        await update.message.reply_text(f'לקוח נוסף בהצלחה🥳 האם תרצה להוסיף עוד לקוח?', reply_markup=reply_markup)
        return ADD_ANOTHER_CLIENT

    except KeyError as e:
        await update.message.reply_text(text=str(e).replace("'", "") + "\n לחזרה לתפריט לחץ /clients")
        return ConversationHandler.END

    except ClientAlreadyExists as e:
        await update.message.reply_text(text=f"{str(e)}\n לחזרה לתפריט לחץ /clients")

    except Exception as e:
        await update.message.reply_text(text=f"{str(e)}\n לחזרה לתפריט לחץ /clients")
        return ConversationHandler.END


async def add_another_client(update: Update, context: CallbackContext) -> int:
    global user_data
    user_choice = update.message.text.lower()

    if user_choice == "כן":
        # User wants to add another client, reset data and go back to full name state
        user_data = {}
        await update.message.reply_text(
            "*הוספת לקוח חדש:* מה השם המלא של הלקוח?\nלביטול הפעולה לחץ /cancel", parse_mode="markdown")
        return ADD_CLIENT_FULL_NAME

    else:
        # User does not want to add another client, end the conversation
        await update.message.reply_text("לחזרה לתפריט הלקוחות לחץ /clients או לחץ /start כדי להתחיל מחדש")
        return ConversationHandler.END


# callback for the "show clients list" button in the clients menu
async def show_clients_callback(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_db(user_id)

        if len(clients_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="אין לך לקוחות קיימים ברשימה.", reply_markup=reply_markup)

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client['full_name']} - {
                                          client['address']}" for index, client in enumerate(clients_list)])
            clients_list_text += "\n🔚"
            await update.callback_query.message.reply_text(text="*רשימת לקוחות:*\n" + clients_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך")

    finally:
        return ConversationHandler.END


# callback for the "show debts" button in the clients menu
async def show_debts_callback(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_db(user_id)

        clients_with_debt_list = [
            client for client in clients_list if client["debt"] != 0]

        if len(clients_with_debt_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_DEBT_OR_RETURN_TO_CLIENTS_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="*לא קיימים לקוחות עם חוב.*", reply_markup=reply_markup, parse_mode="markdown")

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client["full_name"]} - {
                                          client["debt"]}₪" for index, client in enumerate(clients_with_debt_list)])
            clients_list_text += "\n🔚"
            await update.callback_query.message.reply_text(text="*רשימת לקוחות עם חוב:*\n" + clients_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך")

    finally:
        return ConversationHandler.END


# create buttons with the name of the clients
def create_clients_buttons(clients_list, page):
    clients_buttons = []
    for client in clients_list:
        clients_buttons.append([InlineKeyboardButton(
            client["full_name"], callback_data="clientId:"+str(client["id"])+":clientName:" + client["full_name"])])

    if CLIENTS_PER_PAGE <= len(clients_buttons):
        clients_buttons.append([InlineKeyboardButton(
            "next", callback_data="nextPage:" + str(page+1))])

    return clients_buttons


# function for arrange the clients buttons in pairs
def group_buttons(clients_buttons):
    result = []
    current_group = []

    for button in clients_buttons:
        current_group.extend(button)

        if len(current_group) == 2:
            result.append(current_group)
            current_group = []

    if current_group:
        result.append(current_group)

    return result


# functions for "delete client" button in clients menu
async def delete_client_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        clients_list = get_ten_clients_from_db(user_id, offset=0)
        keyboard = create_clients_buttons(clients_list, page=0)
        arranged_keyboard = group_buttons(keyboard)

        reply_markup = InlineKeyboardMarkup(arranged_keyboard)

        await update.callback_query.message.reply_text("*איזה לקוח/ה למחוק?*\nאו לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode='Markdown')
        return ASK_IF_DELETE

    except Exception:
        clients_logger.exception(
            "can't show buttons with names of client to delete")
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך.")
        return ConversationHandler.END


async def ask_if_delete(update, context):

    query = update.callback_query
    await query.answer()

    # call back data is in the format - clientId:client_id:clientName:client_name
    client_id = (query.data.split(":"))[1]
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

    user_id = update.effective_user.id

    # call back data is in the format - yes_clientId:client_id:yes_clientName:client_name
    client_id = (query.data.split(":"))[1]
    client_name = (query.data.split(":"))[3]

    reply_markup = InlineKeyboardMarkup(RETURN_TO_CLIENTS_MENU_KEYBOARD)

    if "yes" in query.data:
        try:
            delete_client_from_db(user_id, client_id)
            await update.callback_query.message.reply_text(text=f"*הלקוח/ה {client_name} נמחק/ה בהצלחה.* למחיקת לקוח נוסף לחץ על שם הלקוח שתרצה למחוק.", reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            await update.callback_query.message.reply_text(".משהו השתבש😕 לא הצלחתי למחוק את הלקוח שבחרת", reply_markup=reply_markup)

        finally:
            return ConversationHandler.END

    else:
        await update.callback_query.message.reply_text(text=f"*הלקוח/ה {client_name} לא נמחק/ה.* למחיקת לקוח אחר לחץ על שם הלקוח שתרצה למחוק.", reply_markup=reply_markup, parse_mode='Markdown')
        return ConversationHandler.END


async def next_page(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # get the page number according to the call back button next in the format - nextPage:next_page
    page = int((query.data.split(":"))[1])

    try:
        clients_list = get_ten_clients_from_db(
            user_id=user_id, offset=CLIENTS_PER_PAGE*page)

        keyboard = create_clients_buttons(clients_list, page=page)
        arranged_keyboard = group_buttons(keyboard)
        reply_markup = InlineKeyboardMarkup(arranged_keyboard)

        await update.callback_query.message.reply_text("*איזה לקוח/ה למחוק?*\nאו לחץ /cancel כדי לבטל", reply_markup=reply_markup, parse_mode='Markdown')
        return ASK_IF_DELETE

    except Exception:
        clients_logger.exception(
            "can't show buttons with names of client to delete in the next page")
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות הבאה שלך.")
        return ConversationHandler.END


# functions for "add debt" button in clients menu
async def add_debt_callback(update, context):

    global clients_list_len_in_add_debt

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_db(user_id)

        clients_list_len_in_add_debt = len(clients_list)

        if clients_list_len_in_add_debt == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="אין לך לקוחות קיימים ברשימה.", reply_markup=reply_markup)
            return ConversationHandler.END

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client['full_name']} - {
                                          client['debt']}₪" for index, client in enumerate(clients_list)])
            clients_list_text += "\n🔚"
            await update.callback_query.message.reply_text(text="*הקש את מספר הלקוח שתרצה להוסיף לו חוב:*\nלביטול הפעולה לחץ /cancel\n" + clients_list_text, parse_mode="markdown")
            return DEBT_AMOUNT_TO_ADD

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך")
        return ConversationHandler.END


async def debt_amount_to_add(update, context):

    global client_number_to_add_debt
    global clients_list_len_in_add_debt

    try:
        client_number_to_add_debt = int(update.message.text) - 1

        if client_number_to_add_debt + 1 > clients_list_len_in_add_debt:
            raise IndexOfClientIsTooBig()

        await update.message.reply_text(f'מהו סכום החוב שתרצה להוסיף ללקוח?\n לביטול הפעולה לחץ /cancel')
        return ADD_DEBT

    except IndexOfClientIsTooBig as e:
        clients_logger.exception(
            "user send number that is bigger than the clients list length")
        await update.message.reply_text(str(e))
        return DEBT_AMOUNT_TO_ADD

    except ValueError as e:
        clients_logger.exception(
            "user send client number to ass debt that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return DEBT_AMOUNT_TO_ADD


async def add_debt(update, context):

    global client_number_to_add_debt

    user_id = update.message.from_user.id

    try:

        debt = int(update.message.text)

        # fetch the clients list again because the list is the same as it was in the previous stages
        clients_list = get_user_clients_from_db(user_id)

        client_id = (clients_list[client_number_to_add_debt])["id"]

        client_name = clients_list[client_number_to_add_debt]["full_name"]

        add_debt_to_db(client_id=client_id, user_id=user_id, debt_to_add=debt)

        reply_markup = InlineKeyboardMarkup(
            ADD_DEBT_OR_RETURN_TO_CLIENTS_MENU_KEYBOARD)

        await update.message.reply_text(text=f"*חוב של {debt}₪ נוסף בהצלחה ללקוח/ה: {client_name}*", reply_markup=reply_markup, parse_mode='Markdown')
        return ConversationHandler.END

    except ValueError as e:
        clients_logger.exception(
            "user send client number to ass debt that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return ADD_DEBT

    except Exception as e:
        clients_logger.exception(str(e))
        await update.message.reply_text("משהו השתבש😕 לא הצלחתי להוסיף חוב ללקוח שלך")
        return ConversationHandler.END


# functions for "delete debt" button in clients menu
async def delete_debt_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_db(user_id)

        clients_with_debt_list = [
            client for client in clients_list if client["debt"] != 0]

        if len(clients_with_debt_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_DEBT_OR_RETURN_TO_CLIENTS_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="*לא קיימים לקוחות עם חוב.*", reply_markup=reply_markup, parse_mode="markdown")

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client["full_name"]} - {
                                          client["debt"]}₪" for index, client in enumerate(clients_with_debt_list)])
            clients_list_text += "\n🔚"

            await update.callback_query.message.reply_text(text="*הקש את מספר הלקוח שתרצה למחוק לו חוב:*\nלביטול הפעולה לחץ /cancel\n" + clients_list_text, parse_mode="markdown")

            return ASK_AMOUNT_TO_DELETE

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות עם חוב שלך")
        return ConversationHandler.END


async def ask_amount_to_delete(update, context):

    global delete_debt_data

    user_id = update.effective_user.id

    try:
        client_number = int(update.message.text) - 1

        delete_debt_data["client_number"] = client_number

        clients_list = get_user_clients_from_db(user_id)

        clients_with_debt_list = [
            client for client in clients_list if client["debt"] != 0]

        if client_number + 1 > len(clients_with_debt_list):
            raise IndexOfClientIsTooBig()

        delete_debt_data["client_id"] = (
            clients_with_debt_list[client_number])["id"]

        delete_debt_data["client_name"] = (
            clients_with_debt_list[client_number])["full_name"]

        delete_debt_data["client_debt"] = (
            clients_with_debt_list[client_number])["debt"]

        keyboard = [[
            InlineKeyboardButton(
                    "מחיקת כל החוב", callback_data="deleteDebt:all")],
                    [InlineKeyboardButton(
                        "מחיקת חלק מהחוב", callback_data="deleteDebt:part")]
                    ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f'*ללקוח/ה {delete_debt_data["client_name"]} יש חוב של {delete_debt_data["client_debt"]}.*\n בחר את הפעולה הרצוייה או לחץ /cancel לביטול',
                                        reply_markup=reply_markup, parse_mode="markdown")

        return DELETE_ALL_DEBT

    except ValueError as e:
        clients_logger.exception(
            "user send client number to ass debt that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return ASK_AMOUNT_TO_DELETE

    except IndexOfClientIsTooBig as e:
        clients_logger.exception(
            "user send number that is bigger than the clients list length")
        await update.message.reply_text(str(e))
        return ASK_AMOUNT_TO_DELETE

    except Exception as e:
        await update.message.reply_text("משהו השתבש😕 לא הצלחתי למחוק חוב ללקוח שלך")
        return ConversationHandler.END


async def delete_all_debt(update, context):

    global delete_debt_data

    query = update.callback_query
    await query.answer()

    # get the user id
    user_id = update.effective_user.id

    parts_of_callback = query.data.split(":")

    type_of_delete = parts_of_callback[1]

    if type_of_delete == "all":

        try:

            delete_debt_from_db(
                user_id=user_id, client_id=delete_debt_data["client_id"], debt_to_delete=delete_debt_data["client_debt"])

            keyboard = [
                [InlineKeyboardButton(
                    "למחיקת חוב נוסף", callback_data="delete_debt")],
                [InlineKeyboardButton(
                    "לחזרה לתפריט לקוחות", callback_data="return_to_clients")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.callback_query.message.reply_text(text=f"*ללקוח/ה {delete_debt_data["client_name"]} נמחק בהצלחה כל החוב.*", reply_markup=reply_markup, parse_mode="markdown")

        except Exception as e:
            await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למחוק את החוב ללקוח שלך")

        finally:
            return ConversationHandler.END

    # if the user wants to delete part of the debt
    else:
        await update.callback_query.message.reply_text(text=f"ללקוח/ה {delete_debt_data["client_name"]} יש חוב של {delete_debt_data["client_debt"]}₪.\n *כמה תרצה להוריד מהחוב?*",
                                                       parse_mode="markdown")
        return DELETE_PART_DEBT


async def delete_part_debt(update, context):

    global delete_debt_data

    user_id = update.message.from_user.id

    try:
        debt_to_delete = int(update.message.text)

        delete_debt_from_db(
            user_id=user_id, client_id=delete_debt_data["client_id"], debt_to_delete=debt_to_delete)

        keyboard = [
            [InlineKeyboardButton(
                "למחיקת חוב נוסף", callback_data="delete_debt")],
            [InlineKeyboardButton(
                "לחזרה לתפריט לקוחות", callback_data="return_to_clients")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text=f"*ללקוח/ה {delete_debt_data["client_name"]} נמחקו {debt_to_delete}₪ מהחוב.*", reply_markup=reply_markup, parse_mode="markdown")
        return ConversationHandler.END

    except ValueError as e:
        clients_logger.exception(
            "the user send something that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return DELETE_PART_DEBT

    except Exception as e:
        clients_logger.exception(str(e))
        await update.message.reply_text("משהו השתבש😕 לא הצלחתי למחוק את החוב ללקוח שלך")
        return ConversationHandler.END


# functions for "send waze link" button
async def waze_link_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_db(user_id)

        if len(clients_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD)
            await update.callback_query.message.reply_text(text="אין לך לקוחות קיימים ברשימה.", reply_markup=reply_markup)
            return ConversationHandler.END

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client['full_name']} - {
                                          client['address']}" for index, client in enumerate(clients_list)])
            clients_list_text += "\n🔚"
            await update.callback_query.message.reply_text(text="*הקש את מספר הלקוח שתרצה לנוט לכתובת שלו:*\nלביטול הפעולה לחץ /cancel\n" + clients_list_text, parse_mode="markdown")
            return SEND_LINK

    except Exception as e:
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא את רשימת הלקוחות שלך")
        return ConversationHandler.END


async def send_link(update, context):

    user_id = update.message.from_user.id

    try:

        client_number = int(update.message.text) - 1

        clients_list = get_user_clients_from_db(user_id)

        if client_number + 1 > len(clients_list):
            raise IndexOfClientIsTooBig()

        address = (clients_list[client_number])["address"]

        url_encoded_address = quote(address)

        await update.message.reply_text(text=f"https://waze.com/ul?q={url_encoded_address}")

    except ValueError as e:
        clients_logger.exception(
            "user send client number to ass debt that cannot be converted to int")
        await update.message.reply_text("לא הבנתי מה שכתבת, אנא הקלד מספר תקין.")
        return SEND_LINK

    except IndexOfClientIsTooBig as e:
        clients_logger.exception(
            "user send number that is bigger than the clients list length")
        await update.message.reply_text(str(e))
        return SEND_LINK

    except Exception as e:
        clients_logger.exception(str(e))
        await update.callback_query.message.reply_text("משהו השתבש😕 לא הצלחתי למצוא קישור לכתובת של הלקוח שלך")
        return ConversationHandler.END


# define the cancel command to end the conversation
async def cancel(update, context):

    reply_markup = InlineKeyboardMarkup(RETURN_TO_CLIENTS_MENU_KEYBOARD)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END


# call back function for the Inline button "return to clients menu"
async def return_to_clients(update, context):

    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(CLIENTS_MENU_KEYBOARD)

    await update.callback_query.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')


# call back handler for the return to clients menu button
return_to_clients_handler = CallbackQueryHandler(
    return_to_clients, pattern="^return_to_clients$")

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
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command), return_to_clients_handler])


# handler for pressing the show debts button in the clients menu
show_debts_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        show_debts_callback, pattern='^show_debts$')],
    states={},
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command), return_to_clients_handler])


# Conversation handler for deleting client from the db
delete_client_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_client_callback, pattern='^delete_client$'), CallbackQueryHandler(ask_if_delete, pattern='^clientId:'),
        CallbackQueryHandler(next_page, pattern='^nextPage:')],
    states={
        ASK_IF_DELETE: [CallbackQueryHandler(ask_if_delete, pattern='^clientId:')],
        DELETE_OR_NOT_CLIENT: [CallbackQueryHandler(
            delete_or_not_client, pattern='^(yes|no)')]
    },
    fallbacks=[CallbackQueryHandler(next_page, pattern='^nextPage:'), CommandHandler(
        'cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command),  CallbackQueryHandler(ask_if_delete, pattern='^clientId:'), return_to_clients_handler])


# conversation handler for add debt to a client
add_debt_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        add_debt_callback, pattern='^add_debt$')],
    states={
        DEBT_AMOUNT_TO_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, debt_amount_to_add)],
        ADD_DEBT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_debt)],
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start),
               CommandHandler("clients", clients_command),
               MessageHandler(filters.TEXT & ~filters.COMMAND,
                              debt_amount_to_add),
               MessageHandler(filters.TEXT & ~filters.COMMAND, add_debt), return_to_clients_handler])


# conversation handler for add debt to a client
delete_debt_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_debt_callback, pattern='^delete_debt$')],
    states={
        ASK_AMOUNT_TO_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount_to_delete)],
        DELETE_ALL_DEBT: [CallbackQueryHandler(delete_all_debt, pattern='^deleteDebt')],
        DELETE_PART_DEBT:  [MessageHandler(
            filters.TEXT & ~filters.COMMAND, delete_part_debt)]
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start),
               CommandHandler("clients", clients_command), MessageHandler(
                   filters.TEXT & ~filters.COMMAND, ask_amount_to_delete),
               MessageHandler(filters.TEXT & ~filters.COMMAND, delete_part_debt), return_to_clients_handler])


# conversation handler for send waze link
waze_link_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        waze_link_callback, pattern='^waze_link$')],
    states={
        SEND_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_link)]
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start),
               CommandHandler("clients", clients_command),
               MessageHandler(filters.TEXT & ~filters.COMMAND, send_link)])

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext, ConversationHandler
import mysql.connector

# Define states
ADD_CLIENT_FULL_NAME, ADD_CLIENT_ADDRESS, ADD_ANOTHER_CLIENT = range(3)


async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
            InlineKeyboardButton("add client", callback_data="add_client"),
            InlineKeyboardButton(
                "delete client", callback_data="delete client"),
        ],
        [InlineKeyboardButton("add debt", callback_data="add debt"),
         InlineKeyboardButton("delete debt", callback_data="delete debt"),
         InlineKeyboardButton("show all debts", callback_data="show all debts")],
        [InlineKeyboardButton("show clients details",
                              callback_data="show clients details")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("*Please choose:*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END


async def add_client_callback(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    await query.answer()
    await update.callback_query.message.reply_text(text="*please send the client full name:*\n or press /cancel to cancel action",
                                                   parse_mode="markdown", reply_markup=ReplyKeyboardRemove())
    return ADD_CLIENT_FULL_NAME


async def add_client_full_name(update: Update, context: CallbackContext) -> int:

    global user_data

    user_details = update.message.from_user
    user_id = user_details.id
    username = user_details.first_name + user_details.last_name
    full_name = update.message.text

    user_data["user_id"] = user_id
    user_data["username"] = username
    user_data["full_name"] = full_name

    await update.message.reply_text(text="*please send the client address:* \n or press /cancel to cancel action", parse_mode="markdown")
    return ADD_CLIENT_ADDRESS


async def add_client_address(update: Update, context: CallbackContext) -> int:

    global user_data

    address = update.message.text
    user_data["address"] = address

    keyboard = [["Yes", "No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    try:
        add_client_to_database(user_data)
        # Ask if the user wants to add another client
        await update.message.reply_text(f'Client added successfully! Do you want to add another client?', reply_markup=reply_markup)
        return ADD_ANOTHER_CLIENT

    except Exception as e:
        await update.message.reply_text(text=f"{str(e)} press /clients to start again")
        return ConversationHandler.END


async def add_another_client(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_choice = update.message.text.lower()

    if user_choice == "yes":
        # User wants to add another client, reset data and go back to full name state
        user_data[user_id] = {}
        await update.message.reply_text(
            "*add another client:* send the client full name:", parse_mode="markdown")
        return ADD_CLIENT_FULL_NAME

    else:
        # User does not want to add another client, end the conversation
        await update.message.reply_text("back to /clients or /start over")
        return ConversationHandler.END


def add_client_to_database(user_data: dict) -> bool:

    if user_data["full_name"] is None or user_data["address"] is None or user_data["user_id"] is None:
        raise KeyError("clients details not full!")

    try:
        # Check if the client already exists in the table
        sql_check_if_exists = "SELECT * FROM clients WHERE full_name = %s AND address = %s AND user_id = %s"
        db_cursor.execute(
            sql_check_if_exists, (user_data["full_name"], user_data["address"], user_data["user_id"]))
        existing_client = db_cursor.fetchone()

        if existing_client:
            # Client already exists, respond according
            raise Exception("Client already exists in the list.")
            # await update.message.reply_text("Client already exists in the list.")
        else:
            # Client does not exist, proceed to add to the table
            sql_insert_client = "INSERT INTO clients (user_id, username, full_name, address) VALUES (%s, %s, %s, %s)"
            values = (user_data["user_id"], user_data.get("username"),
                      user_data["full_name"], user_data["address"])
            db_cursor.execute(sql_insert_client, values)
            db_connection.commit()
            return True

    except Exception as e:
        # Handle any errors
        print(f"Error: {e}")
        raise

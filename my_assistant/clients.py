from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from db_connection import add_client_to_database, get_user_clients_from_database
from consts import (
    ADD_CLIENT_FULL_NAME,
    ADD_CLIENT_ADDRESS,
    ADD_ANOTHER_CLIENT
)
from commands import start

clients_logger = setup_logger("clients_logger")

# dict to store the user_data
user_data = {}


async def clients_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
            InlineKeyboardButton("add client", callback_data="add_client"),
            InlineKeyboardButton(
                "delete client", callback_data="delete client"),
        ],
        [InlineKeyboardButton("add debt", callback_data="add debt"),
         InlineKeyboardButton("delete debt", callback_data="delete debt"),
         InlineKeyboardButton("show all debts", callback_data="show all debts")],
        [InlineKeyboardButton("show clients list",
                              callback_data="show_clients_list")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("*Please choose:*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END

# functions for add client conversation


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
    username = user_details.first_name + " " + user_details.last_name
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


# callback for the "show clients list" button in the clients menu
async def show_clients_callback(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    await query.answer()
    # get the user id
    user_id = update.effective_user.id

    try:
        clients_list = get_user_clients_from_database(user_id)

        if len(clients_list) == 0:
            await update.callback_query.message.reply_text("you don't have any clients.")

        else:
            clients_list_text = "\n".join([f"{index + 1}. {client['full_name']} - {
                                          client['address']}" for index, client in enumerate(clients_list)])
            await update.callback_query.message.reply_text(text="*here is your clients list:*\n" + clients_list_text, parse_mode="markdown")

    except Exception as e:
        await update.callback_query.message.reply_text("Something went wrong 😕 I was unable show your clients list.")

# Define the cancel command to end the conversation


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(text="*the action was cancelled.* press /start if you'll need my help 🙂", parse_mode="markdown")
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
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler("start", start), CommandHandler("clients", clients_command)])

# handler for pressing the show clients list button in the clients menu
show_clients_handler = CallbackQueryHandler(
    show_clients_callback, pattern='^show_clients_list$')

from logger import setup_logger

from consts import (
    TOKEN
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext, ConversationHandler
from clients import clients_features_handlers
from todolist import todolist_features_handlers
from commands import start, shopping
from db_connection import connect_to_db

main_logger = setup_logger("main_logger")


async def todolist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton("add task", callback_data="add task"),
            InlineKeyboardButton("delete task", callback_data="delete task")

        ],
        [
            InlineKeyboardButton("show A tasks", callback_data="show A tasks"),
            InlineKeyboardButton("show B tasks", callback_data="show B tasks"),
            InlineKeyboardButton("show C tasks", callback_data="show C tasks")
        ],
        [
            InlineKeyboardButton(
                "show To Do List", callback_data="show to do list")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def wellness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton(
                "update weight", callback_data="update weight"),
            InlineKeyboardButton("update blood test",
                                 callback_data="update blood tests")

        ],
        [
            InlineKeyboardButton("show progress of weight",
                                 callback_data="show progress of weight"),
            InlineKeyboardButton("show progress of blood test",
                                 callback_data="show progress of blood test"),
        ],
        [
            InlineKeyboardButton("show summary of health condition",
                                 callback_data="show summary of health condition")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


def main():

    main_logger.info("Bot started! Connecting to DB...")
    try:
        connect_to_db()

    except Exception as e:
        main_logger.exception(
            "An error occurred - Unable to connect to the database")

    main_logger.info("Connected to DB")

    # Create the Application and pass it your bot's token.
    app = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram

    app.add_handlers(clients_features_handlers)
    app.add_handlers(todolist_features_handlers)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shopping", shopping))
    app.add_handler(CommandHandler("wellness", todolist))
    app.add_handler(MessageHandler(filters.Regex("shopping"), shopping))
    app.add_handler(MessageHandler(filters.Regex("wellness"), wellness))
    # app.add_handler(MessageHandler(filters.TEXT, generalMsgHandler))

    # Start the Bot
    app.run_polling()

    print("bot finished")


if __name__ == '__main__':
    main()

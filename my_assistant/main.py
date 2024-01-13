import threading
import asyncio
from logger import setup_logger

from consts import (
    TOKEN
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext, ConversationHandler
from clients import clients_features_handlers
from todolist import todolist_features_handlers, reminder_bot_message
from shopping import shopping_features_handlers
from resturants import resturants_features_handlers
from commands import start

main_logger = setup_logger("main_logger")


def wrap_async_func():

    reminder_bot_message_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(reminder_bot_message_loop)
    reminder_bot_message_loop.run_until_complete(reminder_bot_message())
    reminder_bot_message_loop.close()


def main():

    main_logger.info("Bot started! Connecting to DB...")
    # try:
    #     connect_to_db()

    # except Exception as e:
    #     main_logger.exception(
    #         "An error occurred - Unable to connect to the database")

    main_logger.info("Connected to DB")

    # Create the Application and pass it your bot's token.
    app = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    app.add_handlers(clients_features_handlers)
    app.add_handlers(todolist_features_handlers)
    app.add_handlers(shopping_features_handlers)
    app.add_handlers(resturants_features_handlers)

    app.add_handler(CommandHandler("start", start))

    tasks_reminders_thread = threading.Thread(
        target=wrap_async_func, daemon=True)

    tasks_reminders_thread.start()

    app.run_polling()

    print("bot finished")


if __name__ == '__main__':
    main()

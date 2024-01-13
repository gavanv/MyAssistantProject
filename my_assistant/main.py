import threading
import asyncio
import os
from dotenv import load_dotenv
from logger import setup_logger
from consts import (
    START_MENU_KEYBOARD,
    TOKEN
)
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ConversationHandler
from clients import clients_features_handlers
from todolist import todolist_features_handlers, reminder_bot_message
from shopping import shopping_features_handlers
from resturants import resturants_features_handlers

main_logger = setup_logger("main_logger")


async def start(update, context):

    user_details = update.message.from_user
    private_name = user_details.first_name

    reply_markup = ReplyKeyboardMarkup(START_MENU_KEYBOARD)

    await update.message.reply_text(text=f"היי {private_name}🙂 במה אוכל לעזור לך היום?", reply_markup=reply_markup)
    return ConversationHandler.END


def wrap_async_func():

    reminder_bot_message_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(reminder_bot_message_loop)
    reminder_bot_message_loop.run_until_complete(reminder_bot_message())
    reminder_bot_message_loop.close()


def main():

    main_logger.info("Bot started!")

    # Create the Application and pass it the bot token.
    app = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    app.add_handlers(clients_features_handlers)
    app.add_handlers(todolist_features_handlers)
    app.add_handlers(shopping_features_handlers)
    app.add_handlers(resturants_features_handlers)
    app.add_handler(CommandHandler("start", start))

    tasks_reminders_thread = threading.Thread(target=wrap_async_func, 
                                              daemon=True)

    tasks_reminders_thread.start()

    app.run_polling()

    main_logger.info("Bot finished!")


if __name__ == '__main__':
    main()

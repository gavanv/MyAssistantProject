from typing import Final
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN: Final = "6468413070:AAH2MqghzbnZiBG4Dx-l7DpqD6qBTEExuEw"
USER_NAME: Final = "@GavanAssistant_bot"

# Dictionary to store the user's to-do list
todo_lists = {}


# Command handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            KeyboardButton("clients"),
            KeyboardButton("shopping"),
        ],
        [KeyboardButton("To Do List"),
         KeyboardButton("wellness")],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text("Hi SIS, I'm your AsSIStant. \nHow can I help you?", reply_markup=reply_markup)


async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton("add client", callback_data="add client"),
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

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def shopping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [
            InlineKeyboardButton("add item", callback_data="add item"),
            InlineKeyboardButton("delete items", callback_data="delete items")

        ],
        [InlineKeyboardButton("show shopping list",
                              callback_data="show shopping list")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


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


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


def main():

    print("bot started!")

    # Create the Application and pass it your bot's token.
    app = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clients", clients))
    app.add_handler(CommandHandler("shopping", shopping))
    app.add_handler(CommandHandler("todolist", todolist))
    app.add_handler(CommandHandler("wellness", todolist))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.Regex("clients"), clients))
    app.add_handler(MessageHandler(filters.Regex("shopping"), shopping))
    app.add_handler(MessageHandler(filters.Regex("To Do List"), todolist))
    app.add_handler(MessageHandler(filters.Regex("wellness"), wellness))

    # Start the Bot
    app.run_polling()

    print("bot finished")


if __name__ == '__main__':
    main()

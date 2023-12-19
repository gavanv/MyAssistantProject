from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext, ConversationHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
            KeyboardButton("לקוחות"),
            KeyboardButton("shopping"),
        ],
        [KeyboardButton("To Do List"),
         KeyboardButton("wellness")
         ]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(text="היי, במה אוכל לעזור?", reply_markup=reply_markup)
    return ConversationHandler.END


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

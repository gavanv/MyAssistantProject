from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext, ConversationHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    keyboard = [
        [
            KeyboardButton("לקוחות"),
            KeyboardButton("קניות"),
        ],
        [KeyboardButton("ניהול משימות"),
         KeyboardButton("מסעדות וטיולים")
         ]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text(text="היי, במה אוכל לעזור?", reply_markup=reply_markup)
    return ConversationHandler.END



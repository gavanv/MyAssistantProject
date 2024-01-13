from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from db_connection import add_item_to_db, add_resturant_to_db, delete_resturant_from_db, get_area_resturants_from_db, get_user_all_resturants_from_db
from exceptions import IndexIsOutOfRange
from utils import arrange_text_in_lines, create_keyboard, callback_query_errors_handler_decorator, message_errors_handler_decorator
from commands import start
from consts import (
  ADD_RESTURANT,
  CHOOSE_RESTURANT_TO_DELETE,
  DELETE_RESTURANT,
  DELETE_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD,
  GAVAN_USER_ID,
  RESTURANTS_MENU_KEYBOARD,
  RESTURANTS_AREAS,
  ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD,
  RETURN_TO_RESTURANTS_MENU_KEYBOARD,
  SHOW_AREA_RESTURANTS,
  WRITE_RESTURANT
)

resturants_logger = setup_logger("resturants_logger")

# global dict to store the user data for add resturant conversation
user_data_add_resturant = {}

# global dict to store the user data for delete resturant conversation
user_data_delete_resturant = {}


async def resturants_command(update, context):

    reply_markup = InlineKeyboardMarkup(RESTURANTS_MENU_KEYBOARD)

    await update.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END
    

# functions for add resturant conversation
async def add_resturant_callback(update, context):

    global user_data_add_resturant

    query = update.callback_query
    await query.answer()

    user_data_add_resturant["user_id"] = update.effective_user.id

    keyboard = create_keyboard(RESTURANTS_AREAS)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*לאיזה אזור להוסיף את המקום?*\n או לחץ /cancel כדי לבטל", 
                                                   reply_markup=reply_markup, parse_mode="markdown")
    return WRITE_RESTURANT


async def write_resturant(update, context):

    query = update.callback_query
    await query.answer()

    global user_data_add_resturant

    user_data_add_resturant["area"] = update.callback_query.data

    await update.callback_query.message.reply_text(text=f"הקלד את שם המקום שתרצה להוסיף לאזור: *{user_data_add_resturant['area']}* ואת הכתובת של המקום.\n או לחץ /cancel כדי לבטל",
                                                   parse_mode="markdown")
    return ADD_RESTURANT


@message_errors_handler_decorator(resturants_logger, ConversationHandler.END)
async def add_resturant(update, context):

    global user_data_add_resturant

    user_details = update.message.from_user
    username = user_details.first_name + " " + user_details.last_name

    user_data_add_resturant["username"] = username

    user_data_add_resturant["resturant"] = update.message.text

      # to prevent telegram error in markdown mode
    if "*" in user_data_add_resturant["resturant"]:
        user_data_add_resturant["resturant"] = user_data_add_resturant["resturant"].replace("*", "")
    
    add_resturant_to_db(user_data_add_resturant)

    reply_markup = InlineKeyboardMarkup(
        ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)

    await update.message.reply_text(text=f"המקום: *{user_data_add_resturant['resturant']}* באזור: *{user_data_add_resturant['area']}* נוסף בהצלחה לרשימה.", 
                                                    reply_markup=reply_markup, parse_mode='markdown')
    return ConversationHandler.END

#functions for show resturants list conversation

def create_resturants_list_text(resturants_list, areas):

    result_text = ""

    for area in areas:

        resturants_in_area = list(filter(lambda x: x.get("area") == area, resturants_list))

        if len(resturants_in_area) > 0:

            result_text = result_text + f"*{area}:*\n" + "\n".join([f"{index + 1}. {resturant.get('resturant')}" for index, resturant in enumerate(resturants_in_area)])
            result_text += "\n\n"

    return result_text

@callback_query_errors_handler_decorator(resturants_logger)
async def show_my_resturants_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    resturants_list = get_user_all_resturants_from_db(user_id)

    if len(resturants_list) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text="*לא קיימות מסעדות ברשימה.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")

    else:

        resturants_list_text = create_resturants_list_text(resturants_list, RESTURANTS_AREAS)
        resturants_list_text += "🔚"
        
        lines_list = arrange_text_in_lines(resturants_list_text)

        for i, lines in enumerate(lines_list):
            text = "\n".join(lines)
            if i < len(lines_list) - 1:
                text += "\n*המשך⬇️*\n"
            await update.callback_query.message.reply_text(text=text, parse_mode="markdown")

    return ConversationHandler.END


# functions for show resturants in specific area conversation
async def show_area_resturants_callback(update, context):

    query = update.callback_query
    await query.answer()

    keyboard = create_keyboard(RESTURANTS_AREAS)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*באיזה אזור להציג את המקומות?*\n או לחץ /cancel כדי לבטל", 
                                                   reply_markup=reply_markup, parse_mode="markdown")
    return SHOW_AREA_RESTURANTS


@callback_query_errors_handler_decorator(resturants_logger)
async def show_area_resturants(update, context):

    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id


    area = update.callback_query.data

    resturants_list = get_area_resturants_from_db(user_id, area)

    if len(resturants_list) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text="*לא קיימות מסעדות באזור שבחרת.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")

    else:

        resturants_list_text = create_resturants_list_text(resturants_list, [area])

        resturants_list_text += "🔚"

        lines_list = arrange_text_in_lines(resturants_list_text)

        for i, lines in enumerate(lines_list):
            text = "\n".join(lines)
            if i < len(lines_list) - 1:
                text += "\n*המשך⬇️*\n"
            await update.callback_query.message.reply_text(text=text, parse_mode="markdown")

    return ConversationHandler.END

@callback_query_errors_handler_decorator(resturants_logger)
async def show_gavan_resturants_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_id = GAVAN_USER_ID

    resturants_list = get_user_all_resturants_from_db(user_id)

    if len(resturants_list) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text="*לא קיימות מסעדות ברשימה של גוון.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")

    else:

        resturants_list_text = create_resturants_list_text(resturants_list, RESTURANTS_AREAS)

        resturants_list_text += "🔚"

        lines_list = arrange_text_in_lines(resturants_list_text)

        for i, lines in enumerate(lines_list):
            text = "\n".join(lines)
            if i < len(lines_list) - 1:
                text += "\n*המשך⬇️*\n"
            await update.callback_query.message.reply_text(text=text, parse_mode="markdown")

    return ConversationHandler.END

# functions for delete resturants conversation
async def delete_resturant_callback(update, context):

    global user_data_delete_resturant

    query = update.callback_query
    await query.answer()

    user_data_delete_resturant["user_id"] = update.effective_user.id

    keyboard = create_keyboard(RESTURANTS_AREAS)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(text="*מאיזה אזור למחוק מקום?* \nאו לחץ /cancel לביטול.",
                                                   reply_markup=reply_markup,
                                                   parse_mode="markdown")
    return CHOOSE_RESTURANT_TO_DELETE


@callback_query_errors_handler_decorator(resturants_logger)
async def choose_resturant_to_delete(update, context):

    global user_data_delete_resturant

    query = update.callback_query
    await query.answer()

    user_data_delete_resturant["area"] = query.data

    resturants_list = get_user_all_resturants_from_db(user_data_delete_resturant.get("user_id"))

    area_resturants_list_text = create_resturants_list_text(resturants_list, [user_data_delete_resturant["area"]])

    area_resturants_list_text += "🔚"

    user_data_delete_resturant["area_resturants_list"] = list(filter(
        lambda x: x.get("area") == user_data_delete_resturant["area"], resturants_list))

    if len(user_data_delete_resturant["area_resturants_list"]) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text=f"*לא קיימים מקומות באזור: {user_data_delete_resturant["area"]}.*", 
                                                       reply_markup=reply_markup, parse_mode="markdown")
        return ConversationHandler.END

    else:
        await update.callback_query.message.reply_text(text=f"*הקלד את מספר המקום שתרצה למחוק:*\n או לחץ /cancel לביטול\n{area_resturants_list_text}", parse_mode="markdown")
        return DELETE_RESTURANT


@message_errors_handler_decorator(resturants_logger, DELETE_RESTURANT)
async def delete_resturant(update, context):

    global user_data_delete_resturant

    resturant_number = int(update.message.text) - 1

    if resturant_number + 1 > len(user_data_delete_resturant["area_resturants_list"]) or resturant_number < 0:
        raise IndexIsOutOfRange()

    resturant_id = (user_data_delete_resturant["area_resturants_list"][resturant_number])["id"]

    resturant_name = (user_data_delete_resturant["area_resturants_list"][resturant_number])["resturant"]

    delete_resturant_from_db(user_data_delete_resturant["user_id"], resturant_id)

    reply_markup = InlineKeyboardMarkup(DELETE_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD)

    await update.message.reply_text(text=f"המקום: *{resturant_name}* נמחק בהצלחה.", reply_markup=reply_markup, parse_mode="markdown")

    return ConversationHandler.END

# cancel function for resturants menu
async def cancel_for_resturants_conv(update, context):

    reply_markup = InlineKeyboardMarkup(RETURN_TO_RESTURANTS_MENU_KEYBOARD)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END


async def return_to_resturnats(update, context):

    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(RESTURANTS_MENU_KEYBOARD)

    await update.callback_query.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')


# conversation handler for add resturant button
add_resturant_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_resturant_callback, pattern='^add_resturant$')],
    states={
        WRITE_RESTURANT: [CallbackQueryHandler(write_resturant)],
        ADD_RESTURANT: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, add_resturant)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_resturants_conv)],
    allow_reentry=True)


# conversation handler for delete resturant button
delete_resturant_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        delete_resturant_callback, pattern='^delete_resturant$')],
    states={
        CHOOSE_RESTURANT_TO_DELETE: [CallbackQueryHandler(choose_resturant_to_delete)],
        DELETE_RESTURANT: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, delete_resturant)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_resturants_conv)],
    allow_reentry=True)

# conversation handler for add resturant button
show_area_resturants_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(show_area_resturants_callback, pattern='^area_resturants_list$'), 
                  CallbackQueryHandler(show_area_resturants)],
    states={
        SHOW_AREA_RESTURANTS: [CallbackQueryHandler(show_area_resturants)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_resturants_conv)],
    allow_reentry=True)


# call back handler for show all my resturants button
show_my_resturants_handler = CallbackQueryHandler(
    show_my_resturants_callback, pattern='^my_resturants_list$')

# call back handler for show all gavan resturants button
show_gavan_resturants_handler = CallbackQueryHandler(
    show_gavan_resturants_callback, pattern='^gavan_resturants_list$')

return_to_resturants_handler = CallbackQueryHandler(
    return_to_resturnats, pattern="^return_to_resturants$")

resturants_command_handler = CommandHandler("resturants", resturants_command)

resturants_text_handler = MessageHandler(filters.Regex("מסעדות וטיולים"), resturants_command)

resturants_features_handlers = [resturants_command_handler, resturants_text_handler, 
                                add_resturant_conv_handler, return_to_resturants_handler, 
                                show_my_resturants_handler, delete_resturant_conv_handler,
                                show_gavan_resturants_handler, show_area_resturants_conv_handler]
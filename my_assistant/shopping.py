from logger import setup_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (ConversationHandler, CallbackQueryHandler, 
                          MessageHandler, CommandHandler, filters)
from db_connection import (add_item_to_db, delete_item_from_db, 
                           get_limit_items_from_db, get_shopping_list_from_db)
from utils import (group_buttons, callback_query_errors_handler_decorator, 
                   message_errors_handler_decorator)
from consts import (
    DELETE_ITEM,
    ITEMS_PER_PAGE,
    SHOPPING_MENU_KEYBOARD,
    RETURN_TO_SHOPPING_MENU_KEYBOARD,
    ADD_ITEM_OR_RETURN_TO_SHOPPING_MENU_KEYBOARD,
    ADD_ITEM_TO_LIST
)

shopping_logger = setup_logger("shopping_logger")

# global dict to store the user data for delete item conversation
user_data_delete_item = {}

async def shopping_command(update, context):

    reply_markup = InlineKeyboardMarkup(SHOPPING_MENU_KEYBOARD)

    await update.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup, parse_mode='Markdown')
    return ConversationHandler.END


# functions for add item conversation
async def add_item_callback(update, context):

    query = update.callback_query
    await query.answer()
    await update.callback_query.message.reply_text(text="*איזה פריט להוסיף לרשימת הקניות?*\nלביטול הפעולה לחץ /cancel",
                                                   parse_mode="markdown", reply_markup=ReplyKeyboardRemove())
    return ADD_ITEM_TO_LIST


@message_errors_handler_decorator(shopping_logger, ConversationHandler.END)
async def add_item_to_list(update, context):

    user_data_add_item = {}

    user_details = update.message.from_user
    user_data_add_item["user_id"] = user_details.id
    user_data_add_item["username"] = user_details.first_name + " " + user_details.last_name
    user_data_add_item["item"] = update.message.text

    # to prevent telegram error in markdown mode
    if "*" in user_data_add_item["item"]:
        user_data_add_item["item"] = user_data_add_item["item"].replace("*", "")

    add_item_to_db(user_data_add_item)

    reply_markup = InlineKeyboardMarkup(ADD_ITEM_OR_RETURN_TO_SHOPPING_MENU_KEYBOARD)
    await update.message.reply_text(text=f"הפריט: *{user_data_add_item['item']}* נוסף בהצלחה🥳", 
                                    reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END

# function for show shopping list button
@callback_query_errors_handler_decorator(shopping_logger)
async def show_shopping_list_callback(update, context):

    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    # get the shopping list from db based on the user id
    shopping_list = get_shopping_list_from_db(user_id)

    if len(shopping_list) == 0:

        reply_markup = InlineKeyboardMarkup(
            ADD_ITEM_OR_RETURN_TO_SHOPPING_MENU_KEYBOARD)
        await update.callback_query.message.reply_text(text="אין לך פריטים קיימים ברשימה.",
                                                       reply_markup=reply_markup)

    else:
        shopping_list_text = "\n".join([f"{index + 1}. {item['item']}" for index, item in enumerate(shopping_list)])
        shopping_list_text += "\n🔚"
        await update.callback_query.message.reply_text(text="*רשימת קניות:*\n" + shopping_list_text,
                                                       parse_mode="markdown")


# functions for delete item conversation
        
# create buttons with the names of the items
def create_items_buttons(items_list, page):
    items_buttons = []
    for item in items_list:
        # create a button for every item in the list
        # the callback data of each button contains the item id and name
        items_buttons.append([InlineKeyboardButton(
            item.get("item"), 
            callback_data="itemId:"+str(item.get("id"))+":ItemName:" + item.get("item"))])
        
    # if we have more items then the limit in one page, add "next" button
    # the callback data of the next button contain the number of the next page
    if ITEMS_PER_PAGE <= len(items_buttons):
        items_buttons.append([InlineKeyboardButton(
            "next", callback_data="shopping_nextPage:" + str(page+1))])

    return items_buttons

@callback_query_errors_handler_decorator(shopping_logger)
async def delete_item_callback(update, context):

    query = update.callback_query
    await query.answer()

    user_data_delete_item["user_id"] = update.effective_user.id

    items_list = get_limit_items_from_db(user_data_delete_item["user_id"], offset=0)
    keyboard = create_items_buttons(items_list, page=0)

    # arrange the buttons in pairs and add one button if the number of items is odd
    arranged_keyboard = group_buttons(keyboard)

    reply_markup = InlineKeyboardMarkup(arranged_keyboard)

    await update.callback_query.message.reply_text("*איזה פריט למחוק?*\nאו לחץ /cancel כדי לבטל", 
                                                   reply_markup=reply_markup, parse_mode='Markdown')
    return DELETE_ITEM


@callback_query_errors_handler_decorator(shopping_logger)
async def delete_item(update, context):

    query = update.callback_query
    await query.answer()

    # call back data is in the format - itemId:item_id:itemName:item_name
    user_data_delete_item["item_id"] = (query.data.split(":"))[1]
    user_data_delete_item["item_name"] = (query.data.split(":"))[3]

    reply_markup = InlineKeyboardMarkup(RETURN_TO_SHOPPING_MENU_KEYBOARD)

    delete_item_from_db(user_data_delete_item)

    await update.callback_query.message.reply_text(text=f"*הפריט {user_data_delete_item.get('item_name')} נמחק בהצלחה.* למחיקת פריט נוסף לחץ על שם הפריט שתרצה למחוק.", 
                                                           reply_markup=reply_markup, parse_mode='Markdown')
    

@callback_query_errors_handler_decorator(shopping_logger)
async def next_page_of_items_callback(update, context):

    query = update.callback_query
    await query.answer()

    # get the page number according to the call back button next in the format - shopping_nextPage:next_page
    page = int((query.data.split(":"))[1])

    items_list = get_limit_items_from_db(user_id=user_data_delete_item.get("user_id"), offset=ITEMS_PER_PAGE*page)

    keyboard = create_items_buttons(items_list, page=page)
    arranged_keyboard = group_buttons(keyboard)
    reply_markup = InlineKeyboardMarkup(arranged_keyboard)

    await update.callback_query.message.reply_text("*איזה פריט למחוק?*\nאו לחץ /cancel כדי לבטל", 
                                                   reply_markup=reply_markup, parse_mode='Markdown')
    return DELETE_ITEM




# call back function for the Inline button "return to shopping menu"
async def return_to_shopping(update, context):

    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(SHOPPING_MENU_KEYBOARD)

    await update.callback_query.message.reply_text("*איזה פעולה לבצע?*", reply_markup=reply_markup,
                                                   parse_mode='Markdown')


# define the cancel command to end the conversation
async def cancel_for_shopping_conv(update, context):

    reply_markup = InlineKeyboardMarkup(RETURN_TO_SHOPPING_MENU_KEYBOARD)
    await update.message.reply_text(text="*הפעולה בוטלה בהצלחה.*", 
                                    reply_markup=reply_markup, parse_mode="markdown")
    return ConversationHandler.END

# call back handler for the return to shopping menu button
return_to_shopping_handler = CallbackQueryHandler(
    return_to_shopping, pattern="^return_to_shopping$")

# call back handler for the show shopping list button
show_shopping_list_handler = CallbackQueryHandler(
    show_shopping_list_callback, pattern="^show_shopping_list$")

# conversation handler for add item button
add_item_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_item_callback, pattern='^add_item$')],
    states={
        ADD_ITEM_TO_LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_item_to_list)]
    },
    fallbacks=[CommandHandler("cancel", cancel_for_shopping_conv)],
    allow_reentry=True)


# Conversation handler for deleting item from the db
delete_item_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(delete_item_callback, pattern='^delete_item$')],
    states={
        DELETE_ITEM: [CallbackQueryHandler(delete_item, pattern='^itemId:')]},
    fallbacks=[CommandHandler('cancel', cancel_for_shopping_conv), 
               CallbackQueryHandler(next_page_of_items_callback, pattern='^shopping_nextPage:')],
    allow_reentry=True)

shopping_command_handler = CommandHandler("shopping", shopping_command)

shopping_text_handler = MessageHandler(filters.Regex("קניות"), shopping_command)

shopping_features_handlers = [shopping_command_handler, shopping_text_handler, 
                              return_to_shopping_handler,add_item_conv_handler, 
                              show_shopping_list_handler, delete_item_conv_handler]
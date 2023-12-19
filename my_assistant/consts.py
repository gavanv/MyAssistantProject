from telegram import InlineKeyboardButton

TOKEN = "6468413070:AAH2MqghzbnZiBG4Dx-l7DpqD6qBTEExuEw"
BOT_USER_NAME = "@GavanAssistant_bot"

DB_HOST = '44.214.99.189'
DB_USER = 'gavan'
DB_PASSWORD = 'gavan1121g'
DB_NAME = 'myAssistantBotDB'
PORT = 3306

CLIENTS_MENU_KEYBOARD = [
    [
        InlineKeyboardButton(
            "מחיקת לקוח", callback_data="delete_client"),
        InlineKeyboardButton("הוספת לקוח", callback_data="add_client"),
    ],
    [InlineKeyboardButton("הוספת חוב", callback_data="add_debt"),
     InlineKeyboardButton(
        "מחיקת חוב", callback_data="delete_debt"),
     InlineKeyboardButton("כל החובות", callback_data="show_debts")],
    [InlineKeyboardButton("רשימת לקוחות",
                          callback_data="show_clients_list"),
     InlineKeyboardButton("קישור ל-waze",
                          callback_data="waze_link")]

]

# constants keyboards
ADD_CLIENT_OR_RETURN_TO_MENU_KEYBOARD = [[InlineKeyboardButton(
    "הוספת לקוח", callback_data="add_client")],
    [InlineKeyboardButton(
        "לחזרה לתפריט לקוחות", callback_data="return_to_clients")]]

ADD_DEBT_OR_RETURN_TO_CLIENTS_MENU_KEYBOARD = [[InlineKeyboardButton(
    "הוספת חוב ללקוח", callback_data="add_debt")],
    [InlineKeyboardButton(
        "לחזרה לתפריט לקוחות", callback_data="return_to_clients")]]

RETURN_TO_CLIENTS_MENU_KEYBOARD = [
    [InlineKeyboardButton(
        "לחזרה לתפריט לקוחות", callback_data="return_to_clients")]
]

# Define states for add_client conversation
ADD_CLIENT_FULL_NAME, ADD_CLIENT_ADDRESS, ADD_ANOTHER_CLIENT = range(3)

# Define states for delete_client conversation
ASK_IF_DELETE, DELETE_OR_NOT_CLIENT = range(2)

# Define states for add_debt conversation
DEBT_AMOUNT_TO_ADD, ADD_DEBT = range(2)

# Define states for delete_debt conversation
ASK_AMOUNT_TO_DELETE, DELETE_ALL_DEBT, DELETE_PART_DEBT = range(3)

# Define states for waze_link conversation
SEND_LINK = 0

# limit for clients per page
CLIENTS_PER_PAGE = 10

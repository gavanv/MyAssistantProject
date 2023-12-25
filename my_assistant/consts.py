from telegram import InlineKeyboardButton

TOKEN = "6468413070:AAH2MqghzbnZiBG4Dx-l7DpqD6qBTEExuEw"
BOT_USER_NAME = "@GavanAssistant_bot"

DB_HOST = '44.214.99.189'
DB_USER = 'gavan'
DB_PASSWORD = 'gavan1121g'
DB_NAME = 'myAssistantBotDB'
PORT = 3306

# constans for clients part
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


# constants for to do list part
TO_DO_LIST_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("מחיקת משימה", callback_data="delete_task"),
        InlineKeyboardButton("הוספת משימה", callback_data="add_task")

    ],
    [
        InlineKeyboardButton("משימות C", callback_data="C_tasks"),
        InlineKeyboardButton("משימות B", callback_data="B_tasks"),
        InlineKeyboardButton("משימות A", callback_data="A_tasks")
    ],
    [
        InlineKeyboardButton(
            "כל המשימות", callback_data="show_todo_list")
    ],
    [
        InlineKeyboardButton(
            "הוספת תזכורת", callback_data="set_reminder")
    ]
]

ADD_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("הוספת משימה נוספת", callback_data="add_task")
    ],
    [InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                          callback_data="return_to_todolist")
     ]
]

DELETE_TASK_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("מחיקה משימה נוספת", callback_data="delete_task")
    ],
    [InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                          callback_data="return_to_todolist")
     ]
]

RETURN_TO_TODOLIST_MENU_KEYBOARD = [[
    InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                         callback_data="return_to_todolist")
]]

TASKS_CATEGORIES = ["בית", "בריאות וכושר", "לימודים", "עבודה", "אישי", "שונות"]

# Define states for add_task conversation
WRITE_TASK, CHOOSE_LEVEL, ADD_TASK = range(3)

# Define states gor delete_task conversation
CHOOSE_TASK_TO_DELETE, DELETE_TASK = range(2)

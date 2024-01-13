from telegram import InlineKeyboardButton, KeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()

# connection to db details
DB_HOST = os.environ.get("MY_SQL_HOST")
DB_USER = os.environ.get("MY_SQL_USER")
DB_PASSWORD = os.environ.get("MY_SQL_PASSWORD")
DB_NAME = os.environ.get("MY_SQL_DB_NAME")
PORT = os.environ.get("MY_SQL_PORT")

# bot's token
TOKEN = os.environ.get("TOKEN")

# gavan's user is to fetch gavan's resturants list
GAVAN_USER_ID = os.environ.get("GAVAN_USER_ID")

#start command keyboard
START_MENU_KEYBOARD = [
        [
        KeyboardButton("לקוחות"),
        KeyboardButton("קניות"),
        ],
        [
        KeyboardButton("ניהול משימות"),
        KeyboardButton("מסעדות וטיולים")
        ]
]


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
CLIENTS_PER_PAGE = 12


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
        InlineKeyboardButton("מחיקת משימה נוספת", callback_data="delete_task")
    ],
    [InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                          callback_data="return_to_todolist")
     ]
]

RETURN_TO_TODOLIST_MENU_KEYBOARD = [[
    InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                         callback_data="return_to_todolist")
]]

FREQUENCIES_FOR_REMINDERS_KEYBOARD = [
    [
        InlineKeyboardButton("כל יום", callback_data="1")
    ],
    [InlineKeyboardButton("כל שבוע",
                          callback_data="7")
     ],
    [InlineKeyboardButton("כל חודש",
                          callback_data="30")
     ]
]

ADD_REMINDER_OR_RETURN_TO_TODOLIST_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("הוספת תזכורת נוספת",
                             callback_data="set_reminder")
    ],
    [InlineKeyboardButton("חזרה לתפריט ניהול משימות",
                          callback_data="return_to_todolist")
     ]
]

TASKS_CATEGORIES = ["בית", "בריאות וכושר", "לימודים", "עבודה", "אישי", "שונות"]

# Define states for add_task conversation
WRITE_TASK, CHOOSE_LEVEL, ADD_TASK = range(3)

# Define states for delete_task conversation
CHOOSE_TASK_TO_DELETE, DELETE_TASK = range(2)

# Define states for set_reminder conversation
ASK_FREQUENCY, ASK_TIME, SET_REMINDER = range(3)


# constants for shopping part
SHOPPING_MENU_KEYBOARD = [
        [
            InlineKeyboardButton("מחיקת פריט", callback_data="delete_item"),
            InlineKeyboardButton("הוספת פריט", callback_data="add_item")

        ],
        [InlineKeyboardButton("רשימת קניות",
                              callback_data="show_shopping_list")]
    ]

RETURN_TO_SHOPPING_MENU_KEYBOARD = [
    [InlineKeyboardButton("חזרה לתפריט קניות",
                          callback_data="return_to_shopping")
     ]
]

ADD_ITEM_OR_RETURN_TO_SHOPPING_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("הוספת פריט", callback_data="add_item")
    ],
    [InlineKeyboardButton("חזרה לתפריט קניות",
                          callback_data="return_to_shopping")
     ]
]

# Define states for add item conversation
ADD_ITEM_TO_LIST = 0

# Define states for delete item conversation
DELETE_ITEM = 0

# limit for items per page
ITEMS_PER_PAGE = 16

# constants for resturants part
RESTURANTS_MENU_KEYBOARD = [
        [
             InlineKeyboardButton("מחיקת מקום", 
                                 callback_data="delete_resturant"),
            InlineKeyboardButton("הוספת מקום", 
                                 callback_data="add_resturant")
        ],
        [
             InlineKeyboardButton("רשימת כל המקומות",
                                 callback_data="my_resturants_list"),
            InlineKeyboardButton("רשימת מקומות לפי אזור",
                                 callback_data="area_resturants_list")
        ],
        [
             InlineKeyboardButton("רשימת המקומות של גוון",
                                 callback_data="gavan_resturants_list")
        ]
]

RESTURANTS_AREAS= ["גוש דן", "השרון", "שפלה והרי ירושלים", "כרמל ועמק יזרעאל", "רמת הגולן", "גליל עליון ותחתון", "נגב ואילת"]

ADD_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("הוספת מקום", callback_data="add_resturant")
    ],
    [InlineKeyboardButton("חזרה לתפריט מסעדות וטיולים",
                          callback_data="return_to_resturants")
     ]
]

DELETE_RESTURANT_OR_RETURN_TO_RESTURANTS_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("מחיקת מקום", callback_data="delete_resturant")
    ],
    [InlineKeyboardButton("חזרה לתפריט מסעדות וטיולים",
                          callback_data="return_to_resturants")
     ]
]

RETURN_TO_RESTURANTS_MENU_KEYBOARD = [
    [InlineKeyboardButton("חזרה לתפריט מסעדות וטיולים",
                          callback_data="return_to_resturants")
     ]
]


# Define states for add resturant conversation
WRITE_RESTURANT, ADD_RESTURANT = range(2)

# Define states for delete resturant conversation
CHOOSE_RESTURANT_TO_DELETE, DELETE_RESTURANT = range(2)

# Define states for show area resturants conversation
SHOW_AREA_RESTURANTS = 0

MAX_LINES_PER_MESSAGE = 151
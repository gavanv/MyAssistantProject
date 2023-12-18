

TOKEN = "6468413070:AAH2MqghzbnZiBG4Dx-l7DpqD6qBTEExuEw"
BOT_USER_NAME = "@GavanAssistant_bot"

DB_HOST = '44.214.99.189'
DB_USER = 'gavan'
DB_PASSWORD = 'gavan1121g'
DB_NAME = 'myAssistantBotDB'

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

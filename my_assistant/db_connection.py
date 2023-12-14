import mysql.connector
from consts import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)

db_cursor = None
db_connector = None


def connect_to_db():
    global db_cursor, db_connector

    db_connector = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306
    )

    db_cursor = db_connector.cursor(dictionary=True)


def add_client_to_database(user_data: dict) -> bool:
    global db_cursor, db_connector

    if user_data["full_name"] is None or user_data["address"] is None or user_data["user_id"] is None:
        raise KeyError("clients details not full!")

    try:
        # Check if the client already exists in the table
        sql_check_if_exists = "SELECT * FROM clients WHERE full_name = %s AND address = %s AND user_id = %s"
        db_cursor.execute(
            sql_check_if_exists, (user_data["full_name"], user_data["address"], user_data["user_id"]))
        existing_client = db_cursor.fetchone()

        if existing_client:
            # Client already exists, respond according
            raise Exception("Client already exists in the list.")
            # await update.message.reply_text("Client already exists in the list.")
        else:
            # Client does not exist, proceed to add to the table
            sql_insert_client = "INSERT INTO clients (user_id, username, full_name, address) VALUES (%s, %s, %s, %s)"
            values = (user_data["user_id"], user_data.get("username"),
                      user_data["full_name"], user_data["address"])
            db_cursor.execute(sql_insert_client, values)
            db_connector.commit()
            return True

    except Exception as e:
        # Handle any errors
        print(f"Error: {e}")
        raise

from logger import setup_logger
import mysql.connector
from consts import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    CLIENTS_PER_PAGE
)

db_connection_logger = setup_logger("db_connection_logger")

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


def add_client_to_db(user_data: dict) -> bool:
    global db_cursor, db_connector

    if user_data["full_name"] is None or user_data["address"] is None or user_data["user_id"] is None:
        db_connection_logger.error("clients details not full!")
        raise KeyError("לא כל פרטי הלקוח מלאים, נא השלם את הפרטים החסרים.")

    try:
        # Check if the client already exists in the table
        sql_check_if_exists = "SELECT * FROM clients WHERE full_name = %s AND address = %s AND user_id = %s"
        db_cursor.execute(
            sql_check_if_exists, (user_data["full_name"], user_data["address"], user_data["user_id"]))
        existing_client = db_cursor.fetchone()

        if existing_client:
            # Client already exists, respond accordingly
            db_connection_logger.info(
                "user tried to add client that is already in the list")
            raise Exception("הלקוח כבר קיים ברשימת הלקוחות שלך")

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
        db_connection_logger.error("unable to add client to data base")
        raise


def get_user_clients_from_db(user_id):
    global db_cursor

    try:
        # Fetch clients from the database based on the user_id
        sql_get_clients = "SELECT * FROM clients WHERE user_id = %s ORDER BY full_name"
        db_cursor.execute(sql_get_clients, (user_id,))
        clients_list = db_cursor.fetchall()
        return clients_list

    except Exception as e:
        db_connection_logger.exception(
            "unable to get clients list from the data base")
        raise


def get_ten_clients_from_db(user_id, offset):
    global db_cursor

    try:
        # Fetch 10 clients from the database based on the user_id
        sql_get_clients = "SELECT * FROM clients WHERE user_id = %s ORDER BY full_name LIMIT %s OFFSET %s"
        db_cursor.execute(sql_get_clients, (user_id, CLIENTS_PER_PAGE, offset))
        clients_list = db_cursor.fetchall()
        return clients_list

    except Exception as e:
        db_connection_logger.exception(
            "unable to get the 10 clients list from the data base")
        raise


def delete_client_from_db(user_id, client_id):
    global db_cursor, db_connector

    try:
        sql_delete_client = "DELETE FROM clients WHERE id = %s AND user_id = %s"
        db_cursor.execute(sql_delete_client, (client_id, user_id))
        db_connector.commit()
        return True

    except Exception as e:
        # Handle any errors
        db_connection_logger.error("unable to delete client from data base")
        raise


def add_debt_to_db(user_id, client_id, debt_to_add):
    global db_cursor, db_connector

    try:
        sql_add_debt = "UPDATE clients SET debt = debt + %s WHERE id = %s AND user_id = %s"
        db_cursor.execute(sql_add_debt, (debt_to_add, client_id, user_id))
        db_connector.commit()
        return True

    except Exception as e:
        # Handle any errors
        db_connection_logger.error(
            "unable to add debt to the client in the data base")
        raise


def delete_debt_from_db(user_id, client_id, debt_to_delete):
    global db_cursor, db_connector

    try:
        sql_delete_debt = "UPDATE clients SET debt = debt - %s WHERE id = %s AND user_id = %s"
        db_cursor.execute(
            sql_delete_debt, (debt_to_delete, client_id, user_id))
        db_connector.commit()
        return True

    except Exception as e:
        # Handle any errors
        db_connection_logger.error(
            "unable to delete debt to the client in the data base")
        raise

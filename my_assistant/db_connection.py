from logger import setup_logger
import mysql.connector
import threading
from consts import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    PORT,
    CLIENTS_PER_PAGE
)

from exceptions import ClientAlreadyExists

db_connection_logger = setup_logger("db_connection_logger")

# Define a lock for synchronizing database access
db_lock_for_threading = threading.Lock()

db_cursor = None
db_connector = None

# db_cursor_tasks_thread = None
# db_connector_tasks_thread = None


def connect_to_db():
    global db_cursor, db_connector

    db_connector = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=PORT
    )

    db_cursor = db_connector.cursor(dictionary=True)


# def connect_to_db_tasks_thread():
#     global db_cursor_tasks_thread, db_connector_tasks_thread

#     db_connector_tasks_thread = mysql.connector.connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME,
#         port=PORT
#     )

    # db_cursor_tasks_thread = db_connector_tasks_thread.cursor(dictionary=True)


# functions for clients
def add_client_to_db(user_data: dict) -> bool:
    global db_cursor, db_connector

    if user_data.get("full_name") is None or user_data.get("address") is None or user_data.get("user_id") is None:
        db_connection_logger.info("clients details are not full.")
        raise KeyError("לא כל פרטי הלקוח מלאים, נא השלם את הפרטים החסרים.")

    try:
        with db_lock_for_threading:
            # Check if the client already exists in the table
            sql_check_if_exists = "SELECT * FROM clients WHERE full_name = %s AND address = %s AND user_id = %s"
            db_cursor.execute(
                sql_check_if_exists, (user_data["full_name"], user_data["address"], user_data["user_id"]))
            existing_client = db_cursor.fetchone()

            if existing_client:
                # Client already exists, respond accordingly
                raise ClientAlreadyExists(user_data["full_name"])

            else:
                # Client does not exist, proceed to add to the table
                sql_insert_client = "INSERT INTO clients (user_id, username, full_name, address) VALUES (%s, %s, %s, %s)"
                values = (user_data["user_id"], user_data.get("username"),
                          user_data["full_name"], user_data["address"])
                db_cursor.execute(sql_insert_client, values)
                db_connector.commit()
                return True

    except ClientAlreadyExists as e:
        db_connection_logger.info(
            "the user tried to add client that is already exists")
        raise

    except Exception as e:
        db_connection_logger.exception("unable to add client to data base")
        raise


def get_user_clients_from_db(user_id):
    global db_cursor

    try:
        with db_lock_for_threading:
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
        with db_lock_for_threading:
            # Fetch 10 clients from the database based on the user_id
            sql_get_clients = "SELECT * FROM clients WHERE user_id = %s ORDER BY full_name LIMIT %s OFFSET %s"
            db_cursor.execute(
                sql_get_clients, (user_id, CLIENTS_PER_PAGE, offset))
            clients_list = db_cursor.fetchall()
            return clients_list

    except Exception as e:
        db_connection_logger.exception(
            "unable to get the 10 clients list from the data base")
        raise


def delete_client_from_db(user_id, client_id):
    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_delete_client = "DELETE FROM clients WHERE id = %s AND user_id = %s"
            db_cursor.execute(sql_delete_client, (client_id, user_id))
            db_connector.commit()
            return True

    except Exception as e:
        db_connection_logger.error("unable to delete client from data base")
        raise


def add_debt_to_db(user_id, client_id, debt_to_add):
    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_add_debt = "UPDATE clients SET debt = debt + %s WHERE id = %s AND user_id = %s"
            db_cursor.execute(sql_add_debt, (debt_to_add, client_id, user_id))
            db_connector.commit()
            return True

    except Exception as e:
        # Handle any errors
        db_connection_logger.exception(
            "unable to add debt to the client in the data base")
        raise


def delete_debt_from_db(user_id, client_id, debt_to_delete):
    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_delete_debt = "UPDATE clients SET debt = debt - %s WHERE id = %s AND user_id = %s"
            db_cursor.execute(
                sql_delete_debt, (debt_to_delete, client_id, user_id))
            db_connector.commit()
            return True

    except Exception as e:
        # Handle any errors
        db_connection_logger.exception(
            "unable to delete debt to the client in the data base")
        raise


# functions for to do list

def add_task_to_db(user_data: dict) -> bool:
    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_insert_task = "INSERT INTO to_do_list (user_id, username, task, category, level) VALUES (%s, %s, %s, %s, %s)"
            values = (user_data.get("user_id"), user_data.get("username"),
                      user_data.get("task"), user_data.get("category"), user_data.get("level"))
            db_cursor.execute(sql_insert_task, values)
            db_connector.commit()
            return True

    except Exception as e:
        db_connection_logger.error("unable to add task to db")
        raise


def get_user_all_tasks_from_db(user_id):
    global db_cursor

    try:
        with db_lock_for_threading:
            # Fetch all tasks from the database based on the user_id
            sql_get_all_tasks = "SELECT * FROM to_do_list WHERE user_id = %s ORDER BY level"
            db_cursor.execute(sql_get_all_tasks, (user_id,))
            user_tasks = db_cursor.fetchall()
            return user_tasks

    except Exception as e:
        db_connection_logger.exception(
            "unable to get all tasks from the db")
        raise


def delete_task_from_db(user_id, task_id):
    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_delete_client = "DELETE FROM to_do_list WHERE id = %s AND user_id = %s"
            db_cursor.execute(sql_delete_client, (task_id, user_id))
            db_connector.commit()
            return True

    except Exception as e:
        db_connection_logger.error("unable to delete object from db.")
        raise


def add_reminder_to_db(user_data):

    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_insert_reminder = "INSERT INTO tasks_reminders (user_id, username, reminder_text, reminder_frequency, reminder_time, chat_id) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (user_data.get("user_id"), user_data.get("username"),
                      user_data.get("reminder_text"), user_data.get(
                "reminder_frequency"),
                user_data.get("reminder_time"), user_data.get("chat_id"))
            db_cursor.execute(sql_insert_reminder, values)
            db_connector.commit()
            return True

    except Exception as e:
        db_connection_logger.exception("unable to add reminder to db")
        raise


def get_all_reminders():

    global db_cursor,  db_connector
    try:
        with db_lock_for_threading:
            sql_select_reminders = "SELECT * FROM tasks_reminders"
            db_cursor.execute(sql_select_reminders)
            reminders_list = db_cursor.fetchall()
            return reminders_list

    except Exception as e:
        db_connection_logger.exception("unable to get all reminders from db")
        raise


def update_reminder_time(reminder_data):

    global db_cursor, db_connector

    try:
        with db_lock_for_threading:
            sql_update_time = "UPDATE tasks_reminders SET reminder_time = %s WHERE user_id = %s AND reminder_text = %s AND chat_id = %s"
            values = (reminder_data.get("time"), reminder_data.get("user_id"),
                      reminder_data.get("task"), reminder_data.get("chat_id"))
            db_cursor.execute(sql_update_time, values)
            db_connector.commit()

    except Exception as e:
        db_connection_logger.exception("unable to Supdate reminder time in db")
        raise

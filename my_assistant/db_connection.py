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


def db_connection_decorator(error_message="unable to perform database operation"):
    def decorator(query_func):
        def wrapper(*args, **kwargs):
            global db_cursor, db_connector
            try:
                with db_lock_for_threading:
                    if db_connector is None:
                        db_connector = mysql.connector.connect(
                            host=DB_HOST,
                            user=DB_USER,
                            password=DB_PASSWORD,
                            database=DB_NAME,
                            port=PORT
                        )
                        db_cursor = db_connector.cursor(dictionary=True)

                    result = query_func(*args, **kwargs)
                    return result

            except Exception as e:
                db_connection_logger.exception(error_message)
                raise
        return wrapper
    return decorator


# def connect_to_db():
#     global db_cursor, db_connector

#     db_connector = mysql.connector.connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME,
#         port=PORT
#     )

#     db_cursor = db_connector.cursor(dictionary=True)


# functions for clients management menu
@db_connection_decorator(error_message="unable to add client to db.")
def add_client_to_db(user_data):

    # Check if the client already exists in the table
    sql_check_if_exists = "SELECT * FROM clients WHERE full_name = %s AND address = %s AND user_id = %s"
    db_cursor.execute(
        sql_check_if_exists, (user_data.get("full_name"), user_data.get("address"), user_data.get("user_id")))
    existing_client = db_cursor.fetchone()

    if existing_client:
        # Client already exists, respond accordingly
        raise ClientAlreadyExists(user_data.get(
            "full_name"), user_data.get("address"))

    else:
        # Client doesn't exist, proceed to add to db
        sql_insert_client = "INSERT INTO clients (user_id, username, full_name, address) VALUES (%s, %s, %s, %s)"
        values = (user_data.get("user_id"), user_data.get("username"),
                  user_data.get("full_name"), user_data.get("address"))
        db_cursor.execute(sql_insert_client, values)
        db_connector.commit()
        return True


@db_connection_decorator(error_message="unable to get user clients from db.")
def get_user_clients_from_db(user_id):

    # Fetch all clients from the db based on the user_id
    sql_get_clients = "SELECT * FROM clients WHERE user_id = %s ORDER BY full_name"
    db_cursor.execute(sql_get_clients, (user_id,))
    clients_list = db_cursor.fetchall()
    return clients_list


@db_connection_decorator(error_message="unable to get 10 clients from db.")
def get_ten_clients_from_db(user_id, offset):

    # Fetch 10 clients from the database based on the user_id
    sql_get_clients = "SELECT * FROM clients WHERE user_id = %s ORDER BY full_name LIMIT %s OFFSET %s"
    db_cursor.execute(
        sql_get_clients, (user_id, CLIENTS_PER_PAGE, offset))
    ten_clients_list = db_cursor.fetchall()
    return ten_clients_list


@db_connection_decorator(error_message="unable to delete client from db.")
def delete_client_from_db(user_id, client_id):

    sql_delete_client = "DELETE FROM clients WHERE id = %s AND user_id = %s"
    db_cursor.execute(sql_delete_client, (client_id, user_id))
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to add debt to db.")
def add_debt_to_db(user_id, client_id, debt_to_add):

    sql_add_debt = "UPDATE clients SET debt = debt + %s WHERE id = %s AND user_id = %s"
    db_cursor.execute(sql_add_debt, (debt_to_add, client_id, user_id))
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to delete debt from db.")
def delete_debt_from_db(user_id, client_id, debt_to_delete):

    sql_delete_debt = "UPDATE clients SET debt = debt - %s WHERE id = %s AND user_id = %s"
    db_cursor.execute(
        sql_delete_debt, (debt_to_delete, client_id, user_id))
    db_connector.commit()
    return True


# functions for task management menu
@db_connection_decorator(error_message="unable to add task to db.")
def add_task_to_db(user_data):

    sql_add_task = "INSERT INTO to_do_list (user_id, username, task, category, level) VALUES (%s, %s, %s, %s, %s)"
    values = (user_data.get("user_id"), user_data.get("username"),
              user_data.get("task"), user_data.get("category"), user_data.get("level"))
    db_cursor.execute(sql_add_task, values)
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to get all tasks from db.")
def get_user_all_tasks_from_db(user_id):

    sql_get_all_tasks = "SELECT * FROM to_do_list WHERE user_id = %s ORDER BY level"
    db_cursor.execute(sql_get_all_tasks, (user_id,))
    user_tasks = db_cursor.fetchall()
    return user_tasks


@db_connection_decorator(error_message="unable to delete task from db.")
def delete_task_from_db(user_id, task_id):

    sql_delete_task = "DELETE FROM to_do_list WHERE id = %s AND user_id = %s"
    db_cursor.execute(sql_delete_task, (task_id, user_id))
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to add reminder to db.")
def add_reminder_to_db(user_data):

    sql_insert_reminder = "INSERT INTO tasks_reminders (user_id, username, reminder_text, reminder_frequency, reminder_time, chat_id) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (user_data.get("user_id"), user_data.get("username"),
              user_data.get("reminder_text"), user_data.get(
        "reminder_frequency"),
        user_data.get("reminder_time"), user_data.get("chat_id"))
    db_cursor.execute(sql_insert_reminder, values)
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to get all reminders from db.")
def get_all_reminders():

    sql_get_all_reminders = "SELECT * FROM tasks_reminders"
    db_cursor.execute(sql_get_all_reminders)
    reminders_list = db_cursor.fetchall()
    return reminders_list


@db_connection_decorator(error_message="unable to update reminder time in db.")
def update_reminder_time(reminder_data):

    sql_update_reminder_time = "UPDATE tasks_reminders SET reminder_time = %s WHERE user_id = %s AND reminder_text = %s AND chat_id = %s"
    values = (reminder_data.get("time"), reminder_data.get("user_id"),
              reminder_data.get("task"), reminder_data.get("chat_id"))
    db_cursor.execute(sql_update_reminder_time, values)
    db_connector.commit()
    return True


@db_connection_decorator(error_message="unable to delete reminder from db.")
def delete_reminder_from_db(user_id, task_reminder):

    sql_delete_reminder = "DELETE FROM tasks_reminders WHERE user_id = %s AND reminder_text = %s"
    db_cursor.execute(sql_delete_reminder, (user_id, task_reminder))
    db_connector.commit()
    return True

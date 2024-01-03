from db_connection import connect_to_db, get_user_all_tasks_from_db
from time import sleep
import threading


# Define a lock for synchronizing database access
db_lock = threading.Lock()


def get_tasks_loop():

    while True:

        with db_lock:
            print(len(get_user_all_tasks_from_db("222151854")))

        sleep(1)


def main():

    print("connecting to db...")

    connect_to_db()

    print("connection success")

    t1 = threading.Thread(
        target=get_tasks_loop, daemon=True)

    t2 = threading.Thread(
        target=get_tasks_loop, daemon=True)

    # t3 = threading.Thread(
    #     target=get_tasks_loop, daemon=True)

    # t4 = threading.Thread(
    #     target=get_tasks_loop, daemon=True)

    # t5 = threading.Thread(
    #     target=get_tasks_loop, daemon=True)

    t1.start()
    t2.start()
    # t3.start()
    # t4.start()
    # t5.start()

    sleep(9999999)


if __name__ == "__main__":
    main()

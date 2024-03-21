import psycopg2
import os

from database import meta, model

def reset_db():

    connection = psycopg2.connect("postgres:///postgres")

    with connection.cursor() as cursor:
        connection.autocommit = True
        cursor.execute("DROP DATABASE IF EXISTS task_manager_v4")
        cursor.execute("CREATE DATABASE task_manager_v4")

    print("Database reset successfully!")


def alembic_upgrades():
    os.chdir("/mnt/task_manager/backend")
    os.system("alembic upgrade head")

    print("Alembic upgrade completed successfully!")



def _seed_create_user():
    email = "user1@gmail.com"
    password = "user1"

    user = model.User(
        email=email,
        password=password,
        first_name="USER1_FN",
        last_name="USER1_LN",
    )

    meta.session.add(user)
    meta.session.flush()

def _seed_create_user2():
    email = "user2@gmail.com"
    password = "user2"

    user2 = model.User(
        email=email,
        password=password,
        first_name="USER2_FN",
        last_name="USER2_LN",
    )

    meta.session.add(user2)
    meta.session.flush()
    

def _seed_create_tasks():
    meta.session.add_all(
        [
            model.Task(
                title="Task1",
                description="Task1 for User1",
                due_date="2024-01-11 00:00:00",
                create_date="2023-12-29 00:00:00",
                is_deleted=False,
                is_completed=False,
                user_id=1,
                assigned_to=1,
            ),
            model.Task(
                title="Task2",
                description="Task2 for User1",
                due_date="2024-01-10 00:00:00",
                create_date="2023-12-29 00:00:00",
                is_deleted=False,
                is_completed=False,
                user_id=1,
                assigned_to=1,
            ),
            model.Task(
                title="Task3",
                description="Task3 for User1",
                due_date="2024-01-10 00:00:00",
                create_date="2023-12-29 00:00:00",
                is_deleted=False,
                is_completed=False,
                user_id=1,
                assigned_to=1,
            ),
        ]
    )


def _seed_groups():
    meta.session.add_all(
        [
            model.Group(
                name="Group1",
                organizer_id=1,
            ),
            model.Group(
                name="Group2",
                organizer_id=1,
            ),
        ]
    )


def seed_database():
    _seed_create_user()
    _seed_create_user2() 
      
    _seed_create_tasks()

    meta.session.commit()

    _seed_groups()
    meta.session.commit()


if __name__ == "__main__":
    # reset_db()
    # alembic_upgrades()

    seed_database()

    print("DONE!")
  
# Execute Location and code:
# /mnt/task_manager_v4/backend# PYTHONPATH="." python bin/reset_database.py



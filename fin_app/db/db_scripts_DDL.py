import sqlite3
import os
from fin_app.settings.config import DB_PATH

create_transactions_table = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

# SR[20260218]: don't actually use this table. App uses categories from Pydantic model
# create_categories_table = """
# CREATE TABLE IF NOT EXISTS categories (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL
# )
# """

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(create_transactions_table)
        # cursor.execute(create_categories_table)
        cursor.execute(create_users_table)
        conn.commit()

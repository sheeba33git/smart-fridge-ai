import sqlite3

DB_NAME = "fridge.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fridge_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vegetable TEXT,
        freshness TEXT,
        expiry TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_data(veg, fresh, expiry, date):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO fridge_data (vegetable, freshness, expiry, date) VALUES (?, ?, ?, ?)",
        (veg, fresh, expiry, date)
    )

    conn.commit()
    conn.close()


def get_all():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fridge_data ORDER BY id DESC")

    data = cursor.fetchall()

    conn.close()

    return data
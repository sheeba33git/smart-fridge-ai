import sqlite3

DB_NAME = "fridge.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fridge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            veg TEXT,
            freshness TEXT,
            expiry INTEGER,
            date TEXT,
            filename TEXT,
            quantity REAL
        )
    """)

    conn.commit()
    conn.close()


# ✅ INSERT OR UPDATE (SMART LOGIC)
def insert_data(veg, fresh, expiry, date, filename, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 🔍 Check if vegetable already exists
    cursor.execute("SELECT id, quantity FROM fridge WHERE veg = ?", (veg,))
    result = cursor.fetchone()

    if result:
        # ✅ UPDATE quantity instead of new row
        cursor.execute("""
            UPDATE fridge
            SET quantity = quantity + ?, 
                freshness = ?, 
                expiry = ?, 
                date = ?, 
                filename = ?
            WHERE veg = ?
        """, (quantity, fresh, expiry, date, filename, veg))
    else:
        # ✅ INSERT new row
        cursor.execute("""
            INSERT INTO fridge (veg, freshness, expiry, date, filename, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (veg, fresh, expiry, date, filename, quantity))

    conn.commit()
    conn.close()


# ✅ REMOVE (UPDATE QUANTITY)
def update_quantity(veg, quantity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get current quantity
    cursor.execute("SELECT quantity FROM fridge WHERE veg = ?", (veg,))
    result = cursor.fetchone()

    if result:
        new_qty = result[0] - quantity

        # ❗ Prevent negative values
        if new_qty <= 0:
            cursor.execute("DELETE FROM fridge WHERE veg = ?", (veg,))
        else:
            cursor.execute("""
                UPDATE fridge
                SET quantity = ?
                WHERE veg = ?
            """, (new_qty, veg))

    conn.commit()
    conn.close()


def get_all():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ✅ Now only one row per vegetable
    cursor.execute("SELECT * FROM fridge ORDER BY id DESC")

    data = cursor.fetchall()

    conn.close()

    return data
import sqlite3

def get_connection():
    return sqlite3.connect('ship.db')

def setup_database():
    con = get_connection()
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS container (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_name TEXT,
        weight REAL,
        destination TEXT,
        type TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS ship (
        id INTEGER PRIMARY KEY,
        name TEXT,
        capacity REAL
    )''')

    # Initialize one ship if not exists
    cur.execute("INSERT OR IGNORE INTO ship (id, name, capacity) VALUES (1, 'Ocean Carrier', 100000)")
    con.commit()
    con.close()

def add_container(name, weight, destination, type_):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO container (container_name, weight, destination, type) VALUES (?, ?, ?, ?)",
                (name, weight, destination, type_))
    con.commit()
    con.close()

def get_all_containers():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM container")
    data = cur.fetchall()
    con.close()
    return data

def get_total_weight():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT SUM(weight) FROM container")
    total = cur.fetchone()[0]
    con.close()
    return total or 0

def get_ship_capacity():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT capacity FROM ship WHERE id=1")
    capacity = cur.fetchone()[0]
    con.close()
    return capacity
def delete_all_containers():
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM container")
    con.commit()
    con.close()

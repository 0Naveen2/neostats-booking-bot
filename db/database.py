# File 5

import sqlite3
import os
from app.config import DB_NAME

def init_db():
    if not os.path.exists("db"):
        os.makedirs("db")
    
    conn = sqlite3.connect(os.path.join("db", DB_NAME))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, 
                  booking_type TEXT, date TEXT, time TEXT, status TEXT, 
                  FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    conn.commit()
    conn.close()

def save_booking_to_db(data):
    try:
        conn = sqlite3.connect(os.path.join("db", DB_NAME))
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", 
                  (data['name'], data['email'], data['phone']))
        customer_id = c.lastrowid
        c.execute("INSERT INTO bookings (customer_id, booking_type, date, time, status) VALUES (?, ?, ?, ?, ?)", 
                  (customer_id, data['booking_type'], data['date'], data['time'], "Confirmed"))
        booking_id = c.lastrowid
        conn.commit()
        return booking_id
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()

def fetch_all_bookings():
    if not os.path.exists(os.path.join("db", DB_NAME)): return []
    conn = sqlite3.connect(os.path.join("db", DB_NAME))
    try:
        data = conn.execute("""
            SELECT b.id, c.name, c.email, b.booking_type, b.date, b.time, b.status 
            FROM bookings b JOIN customers c ON b.customer_id = c.id
        """).fetchall()
        return data
    except: return []
    finally: conn.close()
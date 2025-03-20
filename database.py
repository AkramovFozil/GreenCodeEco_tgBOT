import sqlite3


def init_db():
    conn = sqlite3.connect('eco_bot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, language TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS trees
                      (tree_id INTEGER PRIMARY KEY, name TEXT, price REAL)''')
    conn.commit()
    conn.close()


init_db()

import sqlite3 as db

MAIN_DB=db.connect('bot_db.db',check_same_thread=False)
Cursor=MAIN_DB.cursor()

Cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users(
    chat_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    state TEXT,
    created_at DATETIME
    );

    CREATE TABLE IF NOT EXISTS settings(
    user_id INTEGER PRIMARY KEY,
    background_color TEXT,
    font TEXT,
    background_type TEXT,
    background_path TEXT
    );

    CREATE TABLE IF NOT EXISTS projects(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    type TEXT,
    text TEXT,
    output_path TEXT,
    created_at DATETIME
    );
    
''')

MAIN_DB.commit()
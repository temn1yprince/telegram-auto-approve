import sqlite3

DB_NAME = "stats.db"


def connect():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total INTEGER DEFAULT 0,
            today INTEGER DEFAULT 0,
            last_user_id INTEGER,
            last_username TEXT,
            last_name TEXT,
            last_time TEXT
        )
    """)

    cur.execute("SELECT * FROM stats WHERE id = 1")

    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO stats
            (id,total,today)
            VALUES
            (1,0,0)
        """)

    conn.commit()
    conn.close()


def add_join(user_id, username, full_name, time):

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        UPDATE stats
        SET
            total = total + 1,
            today = today + 1,
            last_user_id=?,
            last_username=?,
            last_name=?,
            last_time=?
        WHERE id=1
    """, (
        user_id,
        username,
        full_name,
        time
    ))

    conn.commit()
    conn.close()


def get_stats():

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
        total,
        today,
        last_user_id,
        last_username,
        last_name,
        last_time
        FROM stats
        WHERE id=1
    """)

    data = cur.fetchone()

    conn.close()

    return data

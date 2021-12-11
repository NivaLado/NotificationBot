import sqlite3

try:
    conn = sqlite3.connect("C:\\NotificationBot\\NotificationBot.db")
    cursor = conn.cursor()

    # Create user
    cursor.execute("INSERT OR IGNORE INTO 'users' ('userId') VALUES (?)", (1001,))

    # Read all users
    users = cursor.execute("SELECT * FROM 'users'")
    print(users.fetchall())

    conn.commit()

except sqlite3.Error as error:
    print("Error", error)

finally:
    if (conn):
        conn.close()
import sqlite3

conn = sqlite3.connect('./database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS to_do (id INTEGER PRIMARY KEY, Task TEXT, Assignee TEXT, Notes TEXT, Status TEXT)')
conn.commit()
conn.close()

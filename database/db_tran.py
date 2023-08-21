import sqlite3
import os
file_path = os.path.dirname(__file__)


conn = sqlite3.connect(os.path.join(file_path, 'database', 'user.db'))
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE user_db (
    aid str PRIMARY KEY,
    server str,
    last_query_time int,
    battle_count int,
    use_ac bool,
    ac str
);
''')
conn.commit()
conn.close()


conn = sqlite3.connect(os.path.join(file_path, 'data', 'user.db'))
c = conn.cursor()
cursor = c.execute("SELECT * from user_db")
old = list(cursor)
conn.close()

db_path = os.path.join(file_path, 'database', 'user.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

i = 1
for index in old:
    if str(index[0]) != '2023619512':
        continue
    uid = index[0]
    server = index[1]
    time = index[2]
    print(i, server, uid)
    cursor.execute(
        "INSERT INTO user_db (aid,server,last_query_time,battle_count,use_ac,ac) VALUES (?, ?, ?, ?, ?, ?)", (uid, server, time, 0, 0, None))
    conn.commit()
    i += 1
cursor.close()
conn.close()

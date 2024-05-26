import sqlite3
from sqlite3 import Error as SQLError

# Alternative for models.py

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except SQLError as e:
        print(e)
    return conn


def readSQL(cur):
    cur.execute("SELECT * FROM uzivatele")
    for u in cur.fetchall():
        print(u)


def insertSQL(cur, prezdivka, email, heslo):
    insrt_cmd = "INSERT INTO uzivatele(prezdivka, email, heslo) VALUES(?, ?, ?)"
    insrt_data = (prezdivka, email, heslo)
    cur.execute(insrt_cmd, insrt_data)


def main():
    database = "database_pro_web.db"
    conn = create_connection(database)
    if conn is not None:
        cur = conn.cursor()
        insertSQL(cur, "Lambert", "lamy@gmail.com", "489a4d354ad9s")
        readSQL(cur)
        conn.commit()
        conn.close()
    else:
        print("Chyba spojeni s databazi!/n" - SQLError)


if __name__ == "__main__":
    main()

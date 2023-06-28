"""sqlHandler."""

import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pathDb = os.path.join(BASE_DIR, '..', 'DB', 'nagruzka.db')
SETTING_DB = os.path.join(BASE_DIR, '..', 'DB', 'settings.db')


def create_tables():
    """func."""
    create_teachers_table()
    create_work_table()
    create_doljnosti_table()
    create_groups_table()
    create_discipline_table()
    create_nap_pod_table()
    create_settings_table()


# Для преддипломки
def create_work_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        CREATE TABLE IF NOT EXISTS workTables (
        tblId INTEGER,
        fio TEXT,
        teacher_id INTEGER,
        type TEXT,
        mainstvka REAL,
        pochas REAL,
        pochasDop REAL,
        sovmest REAL,
        total REAL
        )
        """)
        cur.execute(query)
        con.commit()


def create_settings_table():
    """func."""
    with sqlite3.connect(SETTING_DB) as con:
        cur = con.cursor()
        query = ("""
        CREATE TABLE IF NOT EXISTS settings (
        start_year INTEGER,
        end_year INTEGER,
        otdel TEXT,
        kafedra TEXT,
        mag_lim INTEGER,
        baq_lim INTEGER,
        start_row INTEGER,
        end_row INTEGER,
        start_col INTEGER,
        end_col INTEGER
        )
        """)
        cur.execute(query)
        con.commit()


def create_teachers_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER,
        fio TEXT,
        zvanie TEXT,
        stepen TEXT,
        doljnost TEXT,
        dipLimit INTEGER,
        curator TEXT
        )
        """)
        cur.execute(query)
        con.commit()


def create_doljnosti_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS doljnosti (
        doljnost TEXT PRIMARY KEY,
        stavka REAL
        )
        """)


def create_groups_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS kafedraGroups (
        group_id INTEGER PRIMARY KEY,
        groupName TEXT,
        amount INTEGER,
        curator TEXT,
        napCode TEXT
        )""")
        con.commit()


def create_discipline_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        CREATE TABLE IF NOT EXISTS disciplines(
        dis_id INTEGER PRIMARY KEY,
        nap_code TEXT,
        discipline TEXT
        )
        """)
        cur.execute(query)
        con.commit()


def create_nap_pod_table():
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        CREATE TABLE IF NOT EXISTS napPod(
        nap_code TEXT,
        nap_name TEXT
        )
        """)
        cur.execute(query)
        con.commit()


def insert_into_setting_table(list_to_add):
    """func."""
    with sqlite3.connect(SETTING_DB) as con:
        cur = con.cursor()
        drop_settings_table()
        create_settings_table()
        cur.execute("""
        INSERT INTO settings (
        start_year,
        end_year,
        otdel,
        kafedra,
        mag_lim,
        baq_lim,
        start_row,
        end_row,
        start_col,
        end_col
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, list_to_add)
        con.commit()


def insert_into_teachers_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        drop_table_by_name('teachers')
        create_teachers_table()
        cur.executemany("""
        INSERT INTO teachers (
        teacher_id,
        fio,
        zvanie,
        stepen,
        doljnost,
        dipLimit,
        curator
        ) VALUES(?, ?, ?, ?, ?, ?, ?)
        """, list_to_add)
        con.commit()


def insert_into_doljnost_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        drop_table_by_name('doljnosti')
        create_doljnosti_table()
        cur.executemany("""
        INSERT INTO doljnosti (
        doljnost, stavka
        ) VALUES( ?, ?)
         """, list_to_add)
        con.commit()


def insert_into_groups_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        DROP TABLE kafedraGroups
        """)
        cur.execute(query)
        create_groups_table()
        query = ("""
        INSERT INTO kafedraGroups VALUES(?, ?, ?, ?, ?)
        """)
        cur.executemany(query, list_to_add)
        con.commit()


def insert_into_napPod_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        DROP TABLE napPod
        """)
        cur.execute(query)
        create_nap_pod_table()
        query = ("""
        INSERT INTO napPod VALUES(?, ?)
        """)
        cur.executemany(query, list_to_add)
        con.commit()


def insert_into_work_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        drop_table_by_name('workTables')
        create_work_table()
        query = ("""
        INSERT INTO workTables VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)
        cur.executemany(query, list_to_add)
        con.commit()


def insert_into_disciplines_table(list_to_add):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        drop_table_by_name('disciplines')
        create_discipline_table()
        query = ("""
        INSERT INTO disciplines VALUES(?, ?, ?)
        """)
        cur.executemany(query, list_to_add)
        con.commit()


def select_all_from_table(tablename):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = "SELECT * FROM " + tablename
        cur.execute(query)
        data = cur.fetchall()
    return data


def select_settings():
    """func."""
    with sqlite3.connect(SETTING_DB) as con:
        cur = con.cursor()
        query = "SELECT * FROM " + 'settings'
        cur.execute(query)
        data = cur.fetchall()
    return data


def drop_table_by_name(tablename):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("DROP TABLE " + tablename)
        cur.execute(query)
        con.commit()


def drop_settings_table():
    """func."""
    with sqlite3.connect(SETTING_DB) as con:
        cur = con.cursor()
        query = ("DROP TABLE " + 'settings')
        cur.execute(query)
        con.commit()


def get_col_where(col_to_get, col_condition, condition, tablename):
    """func."""
    """функция для получения ставки из таблицы должностей"""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        # query = (
        #     "SELECT " + col_to_get + " FROM " + tablename + """
        #       WHERE """ + col_condition + " = " + str(condition))
        query = (
            "SELECT " + col_to_get + " FROM " + tablename + """
              WHERE """ + col_condition + " LIKE '" + condition + "'")
        cur.execute(query)
        data = cur.fetchone()
    return data


def get_row_where(col_condition, condition, tablename):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = (
            "SELECT * FROM " + tablename + """
              WHERE """ + col_condition + " LIKE '" + condition + "'")
        cur.execute(query)
        data = cur.fetchone()
    return data


def update_teachers(data):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        UPDATE teachers
        SET teacher_id = ?,
            fio = ?,
            zvanie = ?,
            stepen = ?,
            doljnost = ?,
            dipLimit = ?,
            curator = ?
        WHERE teacher_id = {}
        """.format(data[0]))
        cur.execute(query, data)
        con.commit()


def update_work_table(data):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        UPDATE workTables
        SET tblId = ?,
            fio = ?,
            teacher_id = ?,
            type = ?,
            mainstvka = ?,
            pochas = ?,
            pochasDop = ?,
            sovmest = ?,
            total = ?
        WHERE tblId = {}
        """.format(data[0]))
        cur.execute(query, data)
        con.commit()


def remove_work_table_where_teacher(id):
    """func."""
    with sqlite3.connect(pathDb) as con:
        cur = con.cursor()
        query = ("""
        DELETE FROM workTables
        WHERE teacher_id LIKE
        """ + str(id))
        cur.execute(query)
        con.commit()


if __name__ == '__main__':
    create_teachers_table()
    data = select_all_from_table('teachers')
    print(data)

"""Схема SQLite и запросы к базам нагрузки и настроек."""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "DB")
pathDb = os.path.join(DB_DIR, "nagruzka.db")
SETTING_DB = os.path.join(DB_DIR, "settings.db")

TABLES = {
    "teachers": (
        "teacher_id",
        "fio",
        "zvanie",
        "stepen",
        "doljnost",
        "dipLimit",
        "curator",
    ),
    "workTables": (
        "tblId",
        "fio",
        "teacher_id",
        "type",
        "mainstvka",
        "pochas",
        "pochasDop",
        "sovmest",
        "total",
    ),
    "doljnosti": ("doljnost", "stavka"),
    "kafedraGroups": (
        "group_id",
        "groupName",
        "amount",
        "curator",
        "napCode",
    ),
    "disciplines": ("dis_id", "nap_code", "discipline"),
    "napPod": ("nap_code", "nap_name"),
}


def _connect(path):
    """func."""
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    return con


def _require_table(tablename):
    """func."""
    if tablename not in TABLES:
        raise ValueError("Неизвестная таблица")
    return tablename


def _require_column(tablename, column):
    """func."""
    _require_table(tablename)
    if column not in TABLES[tablename]:
        raise ValueError("Неизвестный столбец")
    return column


def create_tables():
    """func."""
    os.makedirs(DB_DIR, exist_ok=True)
    create_teachers_table()
    create_work_table()
    create_doljnosti_table()
    create_groups_table()
    create_discipline_table()
    create_nap_pod_table()
    create_settings_table()
    ensure_default_settings()
    return migrate_primary_keys()


def ensure_default_settings():
    """func."""
    with _connect(SETTING_DB) as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM settings")
        if cur.fetchone()[0] == 0:
            cur.execute(
                """
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
                """,
                (0, 0, "", "", 0, 0, 0, 0, 0, 0),
            )
            con.commit()


# Для преддипломки
def create_work_table():
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS workTables (
        tblId INTEGER PRIMARY KEY,
        fio TEXT,
        teacher_id INTEGER REFERENCES teachers(teacher_id)
            DEFERRABLE INITIALLY DEFERRED,
        type TEXT,
        mainstvka REAL,
        pochas REAL,
        pochasDop REAL,
        sovmest REAL,
        total REAL
        )
        """
        cur.execute(query)
        con.commit()


def create_settings_table():
    """func."""
    with _connect(SETTING_DB) as con:
        cur = con.cursor()
        query = """
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
        """
        cur.execute(query)
        con.commit()


def create_teachers_table():
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY,
        fio TEXT,
        zvanie TEXT,
        stepen TEXT,
        doljnost TEXT,
        dipLimit INTEGER,
        curator TEXT
        )
        """
        cur.execute(query)
        con.commit()


def create_doljnosti_table():
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS doljnosti (
        doljnost TEXT PRIMARY KEY,
        stavka REAL
        )
        """)


def create_groups_table():
    """func."""
    with _connect(pathDb) as con:
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
    with _connect(pathDb) as con:
        cur = con.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS disciplines(
        dis_id INTEGER PRIMARY KEY,
        nap_code TEXT,
        discipline TEXT
        )
        """
        cur.execute(query)
        con.commit()


def create_nap_pod_table():
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS napPod(
        nap_code TEXT PRIMARY KEY,
        nap_name TEXT
        )
        """
        cur.execute(query)
        con.commit()


def _column_is_pk(cur, table, column):
    """func."""
    for row in cur.execute("PRAGMA table_info(" + table + ")"):
        if row[1] == column and row[5]:
            return True
    return False


def _work_table_fk_ready(cur):
    """func."""
    row = cur.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        ("workTables",),
    ).fetchone()
    if row is None or "DEFERRABLE" not in row[0].upper():
        return False
    for fk in cur.execute("PRAGMA foreign_key_list(workTables)"):
        if fk[2] == "teachers" and fk[3] == "teacher_id" and fk[4] == "teacher_id":
            return True
    return False


def _schema_current(cur):
    """func."""
    return (
        _column_is_pk(cur, "teachers", "teacher_id")
        and _column_is_pk(cur, "workTables", "tblId")
        and _column_is_pk(cur, "napPod", "nap_code")
        and _work_table_fk_ready(cur)
    )


def _duplicate_key_message(cur):
    """func."""
    checks = (
        ("teachers", "teacher_id", "преподавателей"),
        ("workTables", "tblId", "рабочих таблиц"),
        ("napPod", "nap_code", "направлений"),
    )
    found = []
    for table, column, label in checks:
        duplicates = cur.execute(
            "SELECT COUNT(*) FROM ("
            "SELECT "
            + column
            + " FROM "
            + table
            + " GROUP BY "
            + column
            + " HAVING COUNT(*) > 1)"
        ).fetchone()[0]
        empty = cur.execute(
            "SELECT COUNT(*) FROM " + table + " WHERE " + column + " IS NULL"
        ).fetchone()[0]
        if duplicates or empty:
            found.append(label)
    if not found:
        return None
    return (
        "Миграция не выполнена: повторяются или пустые ключи у "
        + ", ".join(found)
        + ". Старые таблицы оставлены без изменений."
    )


def _orphan_work_table_message(cur):
    """func."""
    orphans = cur.execute(
        """
        SELECT COUNT(*) FROM workTables AS work
        LEFT JOIN teachers AS teacher
            ON work.teacher_id = teacher.teacher_id
        WHERE work.teacher_id IS NOT NULL
            AND teacher.teacher_id IS NULL
        """
    ).fetchone()[0]
    if not orphans:
        return None
    return (
        "Миграция не выполнена: рабочая таблица ссылается "
        "на преподавателя, которого нет. "
        "Старые таблицы оставлены без изменений."
    )


def _rebuild_keyed_tables(con):
    """func."""
    con.execute(
        """
        CREATE TABLE teachers_new (
        teacher_id INTEGER PRIMARY KEY,
        fio TEXT,
        zvanie TEXT,
        stepen TEXT,
        doljnost TEXT,
        dipLimit INTEGER,
        curator TEXT
        )
        """
    )
    con.execute(
        """
        INSERT INTO teachers_new (
        teacher_id, fio, zvanie, stepen, doljnost, dipLimit, curator
        )
        SELECT teacher_id, fio, zvanie, stepen, doljnost, dipLimit, curator
        FROM teachers
        """
    )
    con.execute("DROP TABLE teachers")
    con.execute("ALTER TABLE teachers_new RENAME TO teachers")
    con.execute(
        """
        CREATE TABLE workTables_new (
        tblId INTEGER PRIMARY KEY,
        fio TEXT,
        teacher_id INTEGER REFERENCES teachers(teacher_id)
            DEFERRABLE INITIALLY DEFERRED,
        type TEXT,
        mainstvka REAL,
        pochas REAL,
        pochasDop REAL,
        sovmest REAL,
        total REAL
        )
        """
    )
    con.execute(
        """
        INSERT INTO workTables_new (
        tblId, fio, teacher_id, type, mainstvka, pochas, pochasDop, sovmest, total
        )
        SELECT tblId, fio, teacher_id, type, mainstvka, pochas,
               pochasDop, sovmest, total
        FROM workTables
        """
    )
    con.execute("DROP TABLE workTables")
    con.execute("ALTER TABLE workTables_new RENAME TO workTables")
    con.execute(
        """
        CREATE TABLE napPod_new (
        nap_code TEXT PRIMARY KEY,
        nap_name TEXT
        )
        """
    )
    con.execute(
        """
        INSERT INTO napPod_new (nap_code, nap_name)
        SELECT nap_code, nap_name FROM napPod
        """
    )
    con.execute("DROP TABLE napPod")
    con.execute("ALTER TABLE napPod_new RENAME TO napPod")


def migrate_primary_keys():
    """func."""
    con = sqlite3.connect(pathDb)
    try:
        con.isolation_level = None
        cur = con.cursor()
        if _schema_current(cur):
            return None
        message = _duplicate_key_message(cur)
        if message is None:
            message = _orphan_work_table_message(cur)
        if message:
            return message
        con.execute("PRAGMA foreign_keys=OFF")
        con.execute("BEGIN")
        _rebuild_keyed_tables(con)
        con.execute("COMMIT")
    except sqlite3.Error:
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        return (
            "Миграция не выполнена: не удалось обновить ключи таблиц. "
            "Старые данные оставлены без изменений."
        )
    finally:
        con.close()
    return None


def insert_into_setting_table(list_to_add):
    """func."""
    with _connect(SETTING_DB) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM settings")
        cur.execute(
            """
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
        """,
            list_to_add,
        )


def insert_into_teachers_table(list_to_add):
    """func."""
    con = _connect(pathDb)
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM teachers")
        cur.executemany(
            """
        INSERT INTO teachers (
        teacher_id,
        fio,
        zvanie,
        stepen,
        doljnost,
        dipLimit,
        curator
        ) VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
            list_to_add,
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def insert_into_doljnost_table(list_to_add):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM doljnosti")
        cur.executemany(
            """
        INSERT INTO doljnosti (
        doljnost, stavka
        ) VALUES( ?, ?)
         """,
            list_to_add,
        )


def insert_into_groups_table(list_to_add):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM kafedraGroups")
        cur.executemany(
            "INSERT INTO kafedraGroups VALUES(?, ?, ?, ?, ?)",
            list_to_add,
        )


def insert_into_napPod_table(list_to_add):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM napPod")
        cur.executemany(
            "INSERT INTO napPod VALUES(?, ?)",
            list_to_add,
        )


def insert_into_work_table(list_to_add):
    """func."""
    con = _connect(pathDb)
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM workTables")
        cur.executemany(
            "INSERT INTO workTables VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            list_to_add,
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def replace_teachers_and_work_tables(teachers, work_tables):
    """Сначала снимает рабочие таблицы, затем записывает оба списка."""
    con = _connect(pathDb)
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM workTables")
        cur.execute("DELETE FROM teachers")
        cur.executemany(
            """
            INSERT INTO teachers (
            teacher_id, fio, zvanie, stepen, doljnost, dipLimit, curator
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            teachers,
        )
        cur.executemany(
            "INSERT INTO workTables VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
            work_tables,
        )
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def insert_into_disciplines_table(list_to_add):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM disciplines")
        cur.executemany(
            "INSERT INTO disciplines VALUES(?, ?, ?)",
            list_to_add,
        )


def select_all_from_table(tablename):
    """func."""
    table = _require_table(tablename)
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM " + table)
        data = cur.fetchall()
    return data


def select_settings():
    """func."""
    with _connect(SETTING_DB) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM settings")
        data = cur.fetchall()
    return data


def drop_table_by_name(tablename):
    """func."""
    table = _require_table(tablename)
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute("DROP TABLE " + table)
        con.commit()


def drop_settings_table():
    """func."""
    with _connect(SETTING_DB) as con:
        cur = con.cursor()
        cur.execute("DROP TABLE settings")
        con.commit()


def get_col_where(col_to_get, col_condition, condition, tablename):
    """func."""
    """функция для получения ставки из таблицы должностей"""
    table = _require_table(tablename)
    column = _require_column(table, col_to_get)
    condition_column = _require_column(table, col_condition)
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT "
            + column
            + " FROM "
            + table
            + " WHERE "
            + condition_column
            + " = ?",
            (condition,),
        )
        data = cur.fetchone()
    return data


def get_row_where(col_condition, condition, tablename):
    """func."""
    table = _require_table(tablename)
    condition_column = _require_column(table, col_condition)
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM " + table + " WHERE " + condition_column + " = ?",
            (condition,),
        )
        data = cur.fetchone()
    return data


def update_teachers(data):
    """Обновляет преподавателя и фамилию в его рабочих таблицах."""
    teacher_id = data[0]
    fio = data[1]
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE teachers
            SET teacher_id = ?,
                fio = ?,
                zvanie = ?,
                stepen = ?,
                doljnost = ?,
                dipLimit = ?,
                curator = ?
            WHERE teacher_id = ?
            """,
            list(data) + [teacher_id],
        )
        cur.execute(
            "UPDATE workTables SET fio = ? WHERE teacher_id = ?",
            (fio, teacher_id),
        )
        con.commit()


def update_work_table(data):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        query = """
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
        WHERE tblId = ?
        """
        cur.execute(query, list(data) + [data[0]])
        con.commit()


def remove_work_table_where_teacher(id):
    """func."""
    with _connect(pathDb) as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM workTables WHERE teacher_id = ?",
            (id,),
        )
        con.commit()

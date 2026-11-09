"""Пример без окна: справочник, исходная книга и три выгрузки.

Запуск из каталога, где лежит main.py:

    uv run python -m Example.run_example

Обе строки книги в этом примере отданы одному преподавателю.
Перенос часов по ячейкам остаётся в окне программы.
"""

from pathlib import Path

from openpyxl import Workbook

import Models.DataHandler as DH
import Models.SqlHandler as SQH
from Models.ExcelHandler import ExcelHandler

HOUR_HEADERS = [
    "лек",
    "лаб 1",
    "лаб 2",
    "прак 1",
    "прак 2",
    "конт, реф, ргр 1",
    "конт, реф, ргр 2",
    "КП, КР 1",
    "КП, КР 2",
    "конс 1",
    "конс 2",
    "экз 1",
    "экз 2",
    "зач 1",
    "зач 2",
    "доп",
]

TEACHER_NAME = "Иванов Иван Иванович"
TEACHER_LABEL = "Иванов И.И."
TABLE_LIMIT = 900


def use_databases(db_dir):
    """Направляет запросы в базы примера, а не в DB/."""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    SQH.pathDb = str(db_dir / "nagruzka.db")
    SQH.SETTING_DB = str(db_dir / "settings.db")


def seed_catalogs():
    """Записывает должность, преподавателя, рабочую таблицу и настройки."""
    SQH.create_tables()
    SQH.insert_into_doljnost_table([("доцент", TABLE_LIMIT)])
    SQH.insert_into_teachers_table(
        [(1, TEACHER_NAME, "доцент", "к.т.н.", "доцент", 0, "")]
    )
    SQH.insert_into_work_table(
        [(1, TEACHER_NAME, 1, "Обычная", 1, 0, 0, 0, TABLE_LIMIT)]
    )
    SQH.insert_into_setting_table(
        (
            2025,
            2026,
            "Отделение информационных технологий",
            "Кафедра системного анализа",
            TABLE_LIMIT,
            800,
            0,
            0,
            0,
            0,
        )
    )


def source_headers():
    """Шапка листа: число, колонка «1» и пустая колонка при чтении выпадают."""
    return [
        "отд",
        "вып. каф",
        "направление",
        1,
        "курс",
        "сем",
        "Дисциплина",
        1,
        "группа",
        "студ",
        None,
        *HOUR_HEADERS,
        "всего",
    ]


def source_row(semester, discipline, hours):
    """Строка входящей книги до отбрасывания служебных колонок."""
    values = [0] * len(HOUR_HEADERS)
    for name, amount in hours.items():
        values[HOUR_HEADERS.index(name)] = amount
    return [
        "Отделение информационных технологий",
        "Кафедра системного анализа",
        "09.03.01 Пример",
        1,
        1,
        semester,
        discipline,
        1,
        "П-101",
        25,
        None,
        *values,
    ]


def write_source(path):
    """Пишет книгу с листом «нагрузка кафедры»."""
    book = Workbook()
    sheet = book.active
    sheet.title = "нагрузка кафедры"
    sheet.append([])
    sheet.append(source_headers())
    sheet.append(
        source_row(
            1,
            "Математика",
            {"лек": 18, "прак 1": 16, "конс 1": 2, "экз 1": 4},
        )
    )
    sheet.append(source_row(2, "Физика", {"лек": 20, "лаб 1": 10, "зач 1": 2}))
    sheet.append(["Итого"])
    book.save(path)


def read_source(path):
    """Читает книгу тем же разбором, что и окно программы."""
    excel = ExcelHandler(str(path))
    excel.open_workbook()
    excel.get_sheet_by_name("нагрузка кафедры")
    return excel.read_rows_to_list()


def add_ids(data):
    """Ставит номер строки в первую колонку, как после загрузки в окне."""
    rows = []
    for index, row in enumerate(data):
        rows.append([index, *list(row)])
    return rows


def hour_totals(rows):
    """Суммы колонок часов с 9-й по 24-ю."""
    totals = []
    for col in range(9, 25):
        total = 0.0
        for row in rows:
            value = row[col]
            if value in ("", None, 0):
                continue
            total += float(value)
        if total % 1 == 0:
            total = int(total)
        totals.append(total)
    return totals


def export_sample(output_dir):
    """Собирает исходную книгу, план, общую нагрузку и статистику."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source = output_dir / "nagruzka_istochnik.xlsx"
    plan = output_dir / "plan_ivanov.xlsx"
    general = output_dir / "obsh_nagruzka.xlsx"
    statistics = output_dir / "statistika.xlsx"

    write_source(source)
    seed_catalogs()
    _header, data = read_source(source)
    rows = DH.makeNumberable(add_ids(data))
    osen, vesna, error = DH.divideOsenVesna(rows)
    if error:
        raise RuntimeError(error)

    excel = ExcelHandler()
    excel.writeRows(osen, vesna, str(plan), 1)
    excel.write_nagruzka(DH.make_obsh_nagruzka_for_save(rows), str(general))
    totals = hour_totals(rows)
    stats_header, _empty = DH.get_settings_to_stats_table()
    grand = sum(totals)
    excel.write_statistics(
        [
            stats_header,
            ["Общ", "Общ", *totals, grand],
            [TEACHER_LABEL, "Обычная", *totals, grand],
        ],
        str(statistics),
    )
    return {
        "source": source,
        "plan": plan,
        "general": general,
        "statistics": statistics,
        "hours": grand,
    }


def main():
    """Пишет базы и книги в Example/db и Example/output."""
    root = Path(__file__).resolve().parent
    use_databases(root / "db")
    result = export_sample(root / "output")
    print("Пример собрал файлы:")
    print("Исходная книга:", result["source"])
    print("Индивидуальный план:", result["plan"])
    print("Общая нагрузка:", result["general"])
    print("Статистика:", result["statistics"])
    print("Часов в книге:", result["hours"])
    print("Лимит рабочей таблицы:", TABLE_LIMIT)


if __name__ == "__main__":
    main()

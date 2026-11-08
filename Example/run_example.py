"""example."""

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
    """func."""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    SQH.pathDb = str(db_dir / "nagruzka.db")
    SQH.SETTING_DB = str(db_dir / "settings.db")


def seed_catalogs():
    """func."""
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
    """func."""
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
    """func."""
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
    """func."""
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
    """func."""
    excel = ExcelHandler(str(path))
    excel.open_workbook()
    excel.get_sheet_by_name("нагрузка кафедры")
    return excel.read_rows_to_list()


def add_ids(data):
    """func."""
    rows = []
    for index, row in enumerate(data):
        rows.append([index, *list(row)])
    return rows


def hour_totals(rows):
    """func."""
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
    """func."""
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
    """func."""
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

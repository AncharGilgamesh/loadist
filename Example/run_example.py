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

OTDEL = "Отделение информационных технологий"
KAFEDRA = "Кафедра системного анализа"
TEACHER_NAME = "Иванов Иван Иванович"
TEACHER_LABEL = "Иванов И.И."

RATES = {
    "профессор": 800,
    "доцент": 900,
    "старший преподаватель": 850,
    "ассистент": 800,
    "заведующий кафедрой": 700,
}
TABLE_LIMIT = RATES["доцент"]

DIRECTIONS = [
    ("09.03.01", "Информатика и вычислительная техника"),
    ("09.03.02", "Информационные системы и технологии"),
    ("01.03.02", "Прикладная математика и информатика"),
    ("02.03.03", "Математическое обеспечение и администрирование ИС"),
    ("09.04.01", "Информатика и вычислительная техника"),
]

# курс, студентов, код направления, куратор
GROUPS = [
    ("ИВТ-101", 1, 24, "09.03.01", "Иванов Иван Иванович"),
    ("ИВТ-102", 1, 22, "09.03.01", ""),
    ("ИВТ-201", 2, 21, "09.03.01", "Смирнова Елена Павловна"),
    ("ИВТ-301", 3, 19, "09.03.01", ""),
    ("ИВТ-401", 4, 17, "09.03.01", "Петрова Анна Сергеевна"),
    ("ИСТ-101", 1, 26, "09.03.02", ""),
    ("ИСТ-201", 2, 23, "09.03.02", "Смирнова Елена Павловна"),
    ("ИСТ-301", 3, 18, "09.03.02", ""),
    ("ПМИ-101", 1, 20, "01.03.02", "Сидоров Павел Андреевич"),
    ("ПМИ-201", 2, 18, "01.03.02", ""),
    ("ПМИ-301", 3, 16, "01.03.02", ""),
    ("МОА-101", 1, 15, "02.03.03", ""),
    ("МОА-201", 2, 14, "02.03.03", "Кузнецова Мария Викторовна"),
    ("ИВТм-101", 1, 12, "09.04.01", "Белова Ирина Александровна"),
    ("ИВТм-201", 2, 10, "09.04.01", "Белова Ирина Александровна"),
]

PROFILES = {
    "exam": {"лек": 36, "прак 1": 18, "конс 1": 4, "экз 1": 8},
    "exam_spring": {"лек": 32, "прак 2": 16, "конс 2": 4, "экз 2": 8},
    "lab": {"лек": 18, "лаб 1": 16, "лаб 2": 16, "зач 1": 4},
    "practice": {"прак 1": 28, "конт, реф, ргр 1": 8, "зач 2": 4},
    "project": {"лек": 8, "КП, КР 1": 12, "конс 1": 4, "доп": 2},
    "project2": {"прак 2": 8, "КП, КР 2": 16, "конс 2": 6},
    "control": {"лек": 10, "конт, реф, ргр 2": 12, "зач 1": 2},
    "extra": {"лек": 12, "конс 2": 6, "доп": 20},
}

# код направления -> курс -> полугодие (1 или 2) -> (дисциплина, профиль)
LESSONS = {
    "09.03.01": {
        1: {
            1: [
                ("Математический анализ", "exam"),
                ("Информатика", "lab"),
                ("Программирование", "practice"),
            ],
            2: [
                ("Физика", "lab"),
                ("Математический анализ", "exam_spring"),
                ("Программирование", "project"),
            ],
        },
        2: {
            1: [
                ("Дискретная математика", "exam"),
                ("Базы данных", "lab"),
                ("Алгоритмы и структуры данных", "practice"),
            ],
            2: [
                ("Теория вероятностей", "exam_spring"),
                ("Операционные системы", "lab"),
                ("Базы данных", "project"),
            ],
        },
        3: {
            1: [
                ("Компьютерные сети", "exam"),
                ("Веб-технологии", "lab"),
                ("Методы оптимизации", "control"),
            ],
            2: [
                ("Архитектура ЭВМ", "exam_spring"),
                ("Системное программирование", "project2"),
                ("Веб-технологии", "practice"),
            ],
        },
        4: {
            1: [
                ("Машинное обучение", "exam"),
                ("Защита информации", "lab"),
                ("Производственная практика", "practice"),
            ],
            2: [
                ("Проектирование информационных систем", "project2"),
                ("Защита информации", "control"),
                ("Подготовка ВКР", "extra"),
            ],
        },
    },
    "09.03.02": {
        1: {
            1: [("Математика", "exam"), ("Информатика", "lab")],
            2: [("Физика", "exam_spring"), ("Информатика", "project")],
        },
        2: {
            1: [("Базы данных", "lab"), ("Проектирование ИС", "exam")],
            2: [
                ("Сети и телекоммуникации", "exam_spring"),
                ("Базы данных", "project2"),
            ],
        },
        3: {
            1: [
                ("Корпоративные информационные системы", "exam"),
                ("Тестирование программного обеспечения", "practice"),
            ],
            2: [
                ("Управление ИТ-проектами", "control"),
                ("Корпоративные информационные системы", "project2"),
            ],
        },
    },
    "01.03.02": {
        1: {
            1: [
                ("Математический анализ", "exam"),
                ("Алгебра и геометрия", "practice"),
            ],
            2: [
                ("Математический анализ", "exam_spring"),
                ("Программирование", "lab"),
            ],
        },
        2: {
            1: [
                ("Дифференциальные уравнения", "exam"),
                ("Численные методы", "lab"),
            ],
            2: [
                ("Теория вероятностей", "exam_spring"),
                ("Численные методы", "project"),
            ],
        },
        3: {
            1: [
                ("Методы оптимизации", "exam"),
                ("Математическая статистика", "practice"),
            ],
            2: [
                ("Исследование операций", "project2"),
                ("Математическая статистика", "control"),
            ],
        },
    },
    "02.03.03": {
        1: {
            1: [
                ("Введение в программную инженерию", "exam"),
                ("Языки программирования", "lab"),
            ],
            2: [
                ("Дискретная математика", "exam_spring"),
                ("Языки программирования", "project"),
            ],
        },
        2: {
            1: [
                ("Структуры и алгоритмы обработки данных", "exam"),
                ("Системное администрирование", "lab"),
            ],
            2: [
                ("Операционные системы", "project2"),
                ("Системное администрирование", "practice"),
            ],
        },
    },
    "09.04.01": {
        1: {
            1: [
                ("Методы научных исследований", "exam"),
                ("Современные проблемы информатики", "lab"),
            ],
            2: [
                ("Архитектура программных систем", "project"),
                ("Методы научных исследований", "exam_spring"),
            ],
        },
        2: {
            1: [
                ("Управление данными", "exam"),
                ("Интеллектуальные системы", "lab"),
            ],
            2: [
                ("Интеллектуальные системы", "project2"),
                ("Научно-исследовательская работа", "extra"),
            ],
        },
    },
}

EXTRA_DISCIPLINES = [
    ("09.03.01", "Иностранный язык"),
    ("09.03.01", "Физическая культура"),
    ("09.03.02", "Экономика"),
    ("01.03.02", "История"),
]

TEACHERS = [
    (1, TEACHER_NAME, "доцент", "к.т.н.", "доцент", 2, "ИВТ-101"),
    (2, "Петрова Анна Сергеевна", "профессор", "д.т.н.", "профессор", 3, "ИВТ-401"),
    (3, "Сидоров Павел Андреевич", "доцент", "к.ф.-м.н.", "доцент", 1, "ПМИ-101"),
    (
        4,
        "Кузнецова Мария Викторовна",
        "",
        "",
        "старший преподаватель",
        0,
        "МОА-201",
    ),
    (5, "Орлов Дмитрий Олегович", "", "", "ассистент", 0, ""),
    (
        6,
        "Смирнова Елена Павловна",
        "доцент",
        "к.т.н.",
        "доцент",
        1,
        "ИСТ-201",
    ),
    (7, "Волков Николай Игоревич", "", "", "старший преподаватель", 0, ""),
    (8, "Морозова Ольга Дмитриевна", "доцент", "к.т.н.", "доцент", 0, ""),
    (9, "Зайцев Артём Николаевич", "", "", "ассистент", 0, ""),
    (
        10,
        "Белова Ирина Александровна",
        "профессор",
        "д.ф.-м.н.",
        "заведующий кафедрой",
        2,
        "ИВТм-101",
    ),
    (11, "Новиков Сергей Петрович", "", "", "ассистент", 0, ""),
]


def use_databases(db_dir):
    """func."""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    SQH.pathDb = str(db_dir / "nagruzka.db")
    SQH.SETTING_DB = str(db_dir / "settings.db")


def _teacher(teacher_id):
    """func."""
    for row in TEACHERS:
        if row[0] == teacher_id:
            return row
    raise KeyError(teacher_id)


def _usual(tbl_id, teacher_id, main, sovmest=0, extra=0):
    """func."""
    teacher = _teacher(teacher_id)
    rate = RATES[teacher[4]]
    total = main * rate + sovmest * rate + extra
    return (tbl_id, teacher[1], teacher_id, "Обычная", main, 0, extra, sovmest, total)


def _hourly(tbl_id, teacher_id, hours):
    """func."""
    teacher = _teacher(teacher_id)
    return (tbl_id, teacher[1], teacher_id, "Почасовая", 0, hours, 0, 0, hours)


def work_tables():
    """func."""
    return [
        _usual(1, 1, 1),
        _usual(2, 2, 1),
        _hourly(3, 2, 160),
        _usual(4, 3, 1, sovmest=0.25),
        _usual(5, 4, 1),
        _usual(6, 5, 0.5),
        _usual(7, 6, 1, extra=36),
        _hourly(8, 7, 240),
        _usual(9, 8, 0.5),
        _hourly(10, 8, 100),
        _usual(11, 9, 1),
        _usual(12, 10, 1),
    ]


def load_records():
    """func."""
    records = []
    for code, courses in LESSONS.items():
        for course, parts in courses.items():
            groups = [
                group
                for group in GROUPS
                if group[3] == code and group[1] == course
            ]
            for part, subjects in parts.items():
                semester = (course - 1) * 2 + part
                for name, _course, students, _code, _curator in groups:
                    for title, profile in subjects:
                        records.append(
                            {
                                "code": code,
                                "course": course,
                                "semester": semester,
                                "group": name,
                                "students": students,
                                "discipline": title,
                                "hours": dict(PROFILES[profile]),
                            }
                        )
    aspirant = "Руководство аспирантом (Соколов А.А., Егорова М.В.)"
    for semester in (1, 2):
        records.append(
            {
                "code": "09.04.01",
                "course": 1,
                "semester": semester,
                "group": "асп",
                "students": 2,
                "discipline": aspirant,
                "hours": {"доп": 50},
            }
        )
    return records


def first_semester_record(semester):
    """func."""
    for record in load_records():
        if record["semester"] == semester:
            return record
    raise RuntimeError("Нет строк семестра " + str(semester))


def seed_catalogs():
    """func."""
    SQH.create_tables()
    SQH.insert_into_doljnost_table(list(RATES.items()))
    SQH.replace_teachers_and_work_tables(TEACHERS, work_tables())
    SQH.insert_into_napPod_table(DIRECTIONS)
    groups = []
    for index, (name, _course, students, code, curator) in enumerate(GROUPS, 1):
        groups.append((index, name, students, curator, code))
    groups.append((len(groups) + 1, "асп", 2, TEACHERS[9][1], "09.04.01"))
    SQH.insert_into_groups_table(groups)
    disciplines = []
    seen = set()
    for record in load_records():
        key = (record["code"], record["discipline"])
        if key in seen:
            continue
        seen.add(key)
        disciplines.append((len(disciplines) + 1, key[0], key[1]))
    for code, title in EXTRA_DISCIPLINES:
        disciplines.append((len(disciplines) + 1, code, title))
    SQH.insert_into_disciplines_table(disciplines)
    SQH.insert_into_setting_table(
        (2025, 2026, OTDEL, KAFEDRA, 800, TABLE_LIMIT, 0, 0, 0, 0)
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


def _direction_title(code):
    """func."""
    for direction_code, title in DIRECTIONS:
        if direction_code == code:
            return code + " " + title
    return code


def source_row(record):
    """func."""
    values = [0] * len(HOUR_HEADERS)
    for name, amount in record["hours"].items():
        values[HOUR_HEADERS.index(name)] = amount
    return [
        OTDEL,
        KAFEDRA,
        _direction_title(record["code"]),
        1,
        record["course"],
        record["semester"],
        record["discipline"],
        1,
        record["group"],
        record["students"],
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
    for record in load_records():
        sheet.append(source_row(record))
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
    if len(data) != len(load_records()):
        raise RuntimeError("Из книги прочитаны не все строки нагрузки")
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
        "rows": len(data),
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
    print("Строк нагрузки:", result["rows"])
    print("Часов в книге:", result["hours"])
    print("Преподавателей:", len(TEACHERS))
    print("Рабочих таблиц:", len(work_tables()))
    print("Лимит ставки доцента:", TABLE_LIMIT)


if __name__ == "__main__":
    main()

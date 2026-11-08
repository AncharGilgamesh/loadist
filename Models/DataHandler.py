"""Разбор строк, семестры, статистика и перенос часов."""

import re

import Models.SqlHandler as SQH
from Data.Teacher import Teacher


def parse_non_negative_number(text, integer=False):
    """func."""
    raw = str(text).strip().replace(",", ".")
    if integer:
        if not re.fullmatch(r"\d+", raw):
            return None, "Введите целое неотрицательное число"
        return int(raw), None
    if not re.fullmatch(r"\d+(?:\.\d+)?", raw):
        return None, "Введите неотрицательное число"
    return float(raw), None


def makeNumberable(dataIn, startCol=9):
    """func."""
    data = dataIn.copy()
    for r in range(len(data)):
        for c in range(startCol, len(data[0])):
            el = data[r][c]
            if not el:
                continue
            el = float(data[r][c])
            if el % 1 == 0:
                data[r][c] = int(el)
            else:
                data[r][c] = float(el)
    return data.copy()


def divideOsenVesna(data):
    """func."""
    """
    Функция разделяет строки по семестрам и возвращает списки
    с предметами из осеннего и весеннего семестров
    """
    semRow = 5
    data = data.copy()
    osenSem = [1, 3, 5, 7]
    vesnaSem = [2, 4, 6, 8]
    osen = []
    vesna = []
    for row in data:
        semester, error = _semester_number(row[semRow])
        if error:
            return None, None, error
        newRow = row[1:4] + [""] + row[4:7] + [""] + row[7:9] + [""]
        newRow += row[9:]
        if semester in osenSem:
            osen.append(newRow)
        elif semester in vesnaSem:
            vesna.append(newRow)
        else:
            return None, None, "Семестр должен быть числом от 1 до 8"
    return osen, vesna, None


def _semester_number(value):
    """func."""
    if value is None or str(value).strip() == "":
        return None, "Не указан семестр"
    if isinstance(value, float) and value.is_integer():
        text = str(int(value))
    else:
        text = str(value).strip().replace(",", ".")
        if re.fullmatch(r"\d+\.0+", text):
            text = text.split(".", 1)[0]
    return parse_non_negative_number(text, integer=True)


def data_comparsion(data, data_to_compare):
    """func."""
    return data_to_compare in data


def divide_aspirants(data):
    """func."""
    new_data = []
    for i in data:
        if i == "асп":
            continue
        new_data.append(i)
    return new_data


def make_obsh_nagruzka_for_save(data):
    """func."""
    new_data = []
    for row in data:
        new_row = row[1:4] + [""] + row[4:7] + [""] + row[7:9] + [""]
        new_row += row[9:]
        new_data.append(new_row)
    return new_data


def kafedra_id_add(model, id_col_name, data):
    """func."""
    """функция для добавления id в таблицы кафедр"""
    row_count = model.rowCount()
    ids = model.get_col_by_name(id_col_name)
    if row_count in ids:
        data.insert(0, row_count + len(ids))
    else:
        data.insert(0, row_count)
    model.insertRow(row_count, data)


def return_fio_inicials(fio, type):
    """func."""
    words = fio.strip().split()
    last_name, first_name, middle_name = words
    if type == "Обычная":
        key = f"{last_name} {first_name[0]}.{middle_name[0]}."
    if type == "Почасовая":
        key = f"{last_name} {first_name[0]}.{middle_name[0]}. (почас)"
    return key


def update_prepods_dict(data, dict):
    """func."""
    """
    data -
    [(tableid, fio, teacher_id, type,mainstavka, pochas, pochas+,  sovmest,
      total)]
    Ключ — id рабочей таблицы, иначе вторая таблица того же типа затирает первую.
    """
    for row in data:
        tbl_id = row[0]
        tchr_id = row[2]
        total = row[-1]
        teacher = Teacher(tbl_id, tchr_id, total)
        dict[tbl_id] = teacher


def work_table_labels(data):
    """func."""
    bases = []
    for row in data:
        bases.append((row[0], return_fio_inicials(row[1], row[3])))
    counts = {}
    for _, label in bases:
        counts[label] = counts.get(label, 0) + 1
    labels = {}
    for tbl_id, label in bases:
        if counts[label] > 1:
            labels[tbl_id] = f"{label} ({tbl_id})"
        else:
            labels[tbl_id] = label
    return labels


def get_settings_to_stats_table():
    """func."""
    header = [
        "ФИО",
        "Таблица",
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
        "Итого",
    ]
    data = []
    return header, data


def get_nagruzka_stats(table_view):
    """func."""
    data_to_insert = table_view.model().getAllColSum()
    data_to_insert.append(sum(data_to_insert))
    data_to_insert.insert(0, "Общ")
    data_to_insert.insert(1, "Общ")
    return data_to_insert


def set_prepods_stats(rtbl_model_dict, stats_model, labels):
    """func."""
    for tbl_id, model in rtbl_model_dict.items():
        data_to_insert = model.getAllColSum()
        data_to_insert.append(sum(data_to_insert))
        label = labels.get(tbl_id, str(tbl_id))
        if "почас" in label:
            index = label.find("(почас)")
            data_to_insert.insert(0, label[:index])
            data_to_insert.insert(1, "Почасовая")
        else:
            data_to_insert.insert(0, label)
            data_to_insert.insert(1, "Обычная")
        stats_model.insertRow(len(stats_model.get_data()), data_to_insert)


def get_prepod_info(tbl_id):
    """func."""
    tchr_work = SQH.get_row_where("tblId", str(tbl_id), "workTables")
    if tchr_work is None:
        raise ValueError("Не найдена рабочая таблица преподавателя")
    tchr_info = SQH.get_row_where("teacher_id", str(tchr_work[2]), "teachers")
    if tchr_info is None:
        raise ValueError("Не найден преподаватель рабочей таблицы")
    name = tchr_info[1]
    zvanie = tchr_info[2]
    stepen = tchr_info[3]
    doljnost = tchr_info[4]
    stavka = tchr_work[4]
    pochas = tchr_work[5]
    pochas_v_osn = tchr_work[6]
    sovmestitelstvo = tchr_work[7]
    # total = tchr_work[8]
    rate_row = SQH.get_col_where("stavka", "doljnost", doljnost, "doljnosti")
    stvkaDljnst = None if rate_row is None else rate_row[0]
    list_to_send = [
        name,
        zvanie,
        stepen,
        doljnost,
        stavka,
        pochas,
        pochas_v_osn,
        sovmestitelstvo,
        stvkaDljnst,
    ]
    return list_to_send


def aspirant_name_from_cell(text):
    """func."""
    if not text or "Руководство аспирантом" not in str(text):
        return None
    names = extract_names(str(text))
    if len(names) == 1:
        return names[0]
    return None


def extract_names(string):
    """func."""
    names = re.findall(r"\((.*?)\)", string)  # Извлечение имен из скобок
    name_list = [name.strip() for name in names[0].split(",")] if names else []
    return name_list


def remove_value_from_brackets(value, text):
    """func."""
    # Ищем все вхождения скобок в тексте
    start_bracket = "("
    end_bracket = ")"
    bracket_pairs = []
    i = 0
    while i < len(text):
        if text[i] == start_bracket:
            # Находим закрывающую скобку
            j = i + 1
            while j < len(text):
                if text[j] == end_bracket:
                    bracket_pairs.append((i, j))
                    i = j
                    break
                j += 1
        i += 1

    # Удаляем переданное значение внутри скобок и запятую после него
    for start, end in bracket_pairs:
        bracket_content = text[start + 1 : end]
        bracket_values = [v.strip() for v in bracket_content.split(",")]
        updated_values = [v for v in bracket_values if v != value]
        updated_bracket_content = ", ".join(updated_values)
        updated_text = text[: start + 1] + updated_bracket_content + text[end:]
        text = updated_text
    return text


def check_single_value_inside_brackets(text):
    """func."""
    start_bracket = "("
    end_bracket = ")"
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку, начиная с позиции
    #  после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    bracket_content = text[start_index + 1 : end_index].strip()
    # Разделяем содержимое по запятым
    values = [v.strip() for v in bracket_content.split(",")]
    if len(values) == 1:
        return True
    else:
        return False


def extract_value_from_brackets(text):
    """func."""
    start_bracket = "("
    end_bracket = ")"
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку,
    #  начиная с позиции после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    value = text[start_index + 1 : end_index].strip()
    return value


def add_value_to_brackets(additional_value, text):
    """func."""
    start_bracket = "("
    end_bracket = ")"
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку,
    #  начиная с позиции после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    bracket_content = text[start_index + 1 : end_index].strip()
    # Разделяем содержимое по запятым
    values = [v.strip() for v in bracket_content.split(",")]
    # Добавляем дополнительное значение
    values.append(additional_value)
    # Обновляем содержимое скобок
    updated_bracket_content = ", ".join(values)
    # Заменяем исходное содержимое скобок на обновленное в тексте
    updated_text = text[: start_index + 1] + updated_bracket_content
    updated_text += text[end_index:]
    return updated_text


def collect_selected_rows(model, selected_indexes, choose_aspirant):
    """Собирает переносимые строки. None, если выбор аспиранта отменён."""
    row_data = {}
    for index in selected_indexes:
        row = index.row()
        column = index.column()
        if row in row_data:
            row_data[row][column] = str(model.index(row, column).data())
            continue
        current_row = []
        for col in range(9):
            current_row.append(str(model.index(row, col).data()))
        discipline = model.index(row, 6).data()
        if discipline and "Руководство аспирантом" in str(discipline):
            selected_item = choose_aspirant(extract_names(str(discipline)))
            if not selected_item:
                return None
            current_row[6] = "Руководство аспирантом (" + selected_item + ")"
            current_row[8] = int(current_row[8]) - 1
        for col in range(9, model.columnCount()):
            if col == column:
                current_row.append(str(model.index(row, col).data()))
            else:
                current_row.append("")
        row_data[row] = current_row
    return row_data


def move_rows(source, destination, selected_indexes, row_data):
    """Переносит собранные строки из одной таблицы в другую."""
    edited = source.get_edited_cells()
    selected = {}
    for index in selected_indexes:
        row = index.row()
        column = index.column()
        if row in selected:
            selected[row].add(column)
        else:
            selected[row] = {column}
    empty_rows = []
    for key in edited:
        if key in selected:
            edited[key] = edited[key] - selected[key]
            if not edited[key]:
                empty_rows.append(key)
    for key in empty_rows:
        del edited[key]
    for key, columns in edited.items():
        for column in columns:
            source.get_back_not_selected_edited_cols(key, column)
    data_dict = source.get_diff()
    edited_keys = edited.keys()
    for row_index in row_data:
        aspirant = aspirant_name_from_cell(row_data[row_index][6])
        if row_index in data_dict and row_index not in edited_keys:
            source.divide_changed_row(row_index, data_dict[row_index], aspirant)
        elif row_index in data_dict and row_index in edited_keys:
            source.special_divide_row(
                row_index, row_data[row_index], data_dict[row_index], aspirant
            )
        else:
            source.divide_row(row_index, row_data[row_index])
    source.clear_edited_dict()
    model_ids = destination.getIds()
    start_row = destination._startEditRow
    for row in row_data.values():
        if row[0] in model_ids:
            destination.addToRow(model_ids[row[0]], row, start_row)
        else:
            destination.appendRow(row)
            destination.addId(row[0])
    source.clearChangesDict()
    source.clearBasicDict()


def sum_lists(dictionary):
    """func."""
    total_sum = 0.0
    for key in dictionary:
        if isinstance(dictionary[key], list):
            for item in dictionary[key][9:]:
                try:
                    total_sum += float(item)
                except ValueError:
                    pass
    return total_sum

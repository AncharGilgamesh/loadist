"""work with data."""
from Data.Teacher import Teacher
from PyQt5.QtWidgets import QDialog
from UICode.NameSelectionDialog import NameSelectionDialog
import Models.SqlHandler as SQH
import re


def makeNumberable(dataIn, startCol=8):
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
        newRow = row[1:4] + [''] + row[4:7] + [''] + row[7:9] + ['']
        newRow += row[9:]
        if int(row[semRow]) in osenSem:
            osen.append(newRow)
        elif int(row[semRow]) in vesnaSem:
            vesna.append(newRow)
    return osen, vesna


def data_comparsion(data, data_to_compare):
    """func."""
    return data_to_compare in data


def divide_aspirants(data):
    """func."""
    new_data = []
    for i in data:
        if i == 'асп':
            continue
        new_data.append(i)
    return new_data


def make_obsh_nagruzka_for_save(data):
    """func."""
    new_data = []
    for row in data:
        new_row = row[1:4] + [''] + row[4:7] + [''] + row[7:9] + ['']
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
    if type == 'Обычная':
        key = f'{last_name} {first_name[0]}.{middle_name[0]}.'
    if type == 'Почасовая':
        key = f'{last_name} {first_name[0]}.{middle_name[0]}. (почас)'
    return key


def update_prepods_dict(data, dict):
    """func."""
    """
    data -
    [(tableid, fio, teacher_id, type,mainstavka, pochas, pochas+,  sovmest,
      total)]
    """
    tbl_id = None
    tchr_id = None
    total = None
    key = None
    for row in data:
        tbl_id = row[0]
        tchr_id = row[2]
        total = row[-1]
        key = return_fio_inicials(row[1], row[3])
        teacher = Teacher(tbl_id, tchr_id, total)
        dict[key] = teacher


def get_settings_to_stats_table():
    """func."""
    header = [
            'ФИО',
            'Таблица',
            'лек',
            'лаб 1',
            'лаб 2',
            'прак 1',
            'прак 2',
            'конт, реф, ргр 1',
            'конт, реф, ргр 2',
            'КП, КР 1',
            'КП, КР 2',
            'конс 1',
            'конс 2',
            'экз 1',
            'экз 2',
            'зач 1',
            'зач 2',
            'доп',
            'Итого'
        ]
    data = []
    return header, data


def get_nagruzka_stats(table_view):
    """func."""
    data_to_insert = table_view.model().getAllColSum()
    data_to_insert.append(sum(data_to_insert))
    data_to_insert.insert(0, 'Общ')
    data_to_insert.insert(1, 'Общ')
    return data_to_insert


def set_prepods_stats(rtbl_model_dict, stats_model):
    """func."""
    for k, v in rtbl_model_dict.items():
        data_to_insert = v.getAllColSum()
        data_to_insert.append(sum(data_to_insert))
        if 'почас' in k:
            index = k.find('(почас)')
            data_to_insert.insert(0, k[:index])
            data_to_insert.insert(1, 'Почасовая')
        else:
            data_to_insert.insert(0, k)
            data_to_insert.insert(1, 'Обычная')
        stats_model.insertRow(
            len(stats_model.get_data()), data_to_insert)


def get_prepod_info(tbl_id):
    """func."""
    tchr_work = SQH.get_row_where('tblId', str(tbl_id), 'workTables')
    tchr_info = SQH.get_row_where('teacher_id', str(tchr_work[2]), 'teachers')
    name = tchr_info[1]
    zvanie = tchr_info[2]
    stepen = tchr_info[3]
    doljnost = tchr_info[4]
    stavka = tchr_work[4]
    pochas = tchr_work[5]
    pochas_v_osn = tchr_work[6]
    sovmestitelstvo = tchr_work[7]
    # total = tchr_work[8]
    stvkaDljnst = SQH.get_col_where(
            'stavka', 'doljnost', doljnost, 'doljnosti')[0]
    list_to_send = [
        name, zvanie, stepen, doljnost, stavka, pochas, pochas_v_osn,
        sovmestitelstvo, stvkaDljnst
    ]
    return list_to_send


def extract_names(string):
    """func."""
    names = re.findall(r'\((.*?)\)', string)  # Извлечение имен из скобок
    name_list = [
        name.strip() for name in names[0].split(',')] if names else []
    return name_list


def remove_value_from_brackets(value, text):
    """func."""
    # Ищем все вхождения скобок в тексте
    start_bracket = '('
    end_bracket = ')'
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
        bracket_content = text[start + 1: end]
        bracket_values = [v.strip() for v in bracket_content.split(',')]
        updated_values = [v for v in bracket_values if v != value]
        updated_bracket_content = ', '.join(updated_values)
        updated_text = text[:start + 1] + updated_bracket_content + text[end:]
        text = updated_text
    return text


def check_single_value_inside_brackets(text):
    """func."""
    start_bracket = '('
    end_bracket = ')'
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку, начиная с позиции
    #  после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    bracket_content = text[start_index + 1: end_index].strip()
    # Разделяем содержимое по запятым
    values = [v.strip() for v in bracket_content.split(',')]
    if len(values) == 1:
        return True
    else:
        return False


def extract_value_from_brackets(text):
    """func."""
    start_bracket = '('
    end_bracket = ')'
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку,
    #  начиная с позиции после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    value = text[start_index + 1: end_index].strip()
    return value


def add_value_to_brackets(additional_value, text):
    """func."""
    start_bracket = '('
    end_bracket = ')'
    # Находим первую открывающую скобку
    start_index = text.find(start_bracket)
    # Находим последнюю закрывающую скобку,
    #  начиная с позиции после открывающей скобки
    end_index = text.find(end_bracket, start_index + 1)
    # Извлекаем содержимое скобок
    bracket_content = text[start_index + 1: end_index].strip()
    # Разделяем содержимое по запятым
    values = [v.strip() for v in bracket_content.split(',')]
    # Добавляем дополнительное значение
    values.append(additional_value)
    # Обновляем содержимое скобок
    updated_bracket_content = ', '.join(values)
    # Заменяем исходное содержимое скобок на обновленное в тексте
    updated_text = text[:start_index + 1] + updated_bracket_content
    updated_text += text[end_index:]
    return updated_text


def get_selected_rows(sel_index, model):
    """func."""
    row_data = {}
    selected_item = None
    for index in sel_index:
        # строка текущего индекса
        row = index.row()
        # столбец текущего индекса
        column = index.column()
        if row in row_data.keys():
            col_value = str(model.index(row, column).data())
            row_data[row][column] = col_value
        else:
            """
            Если строка в цикле первый раз, то мы заполняем ее.
            Первый цикл заполняет столбцы до учебных часов.
            Второй цикл забивает нулями строку, если индекс
            строки не равен индексу выбранного столбца. Если индекс
            строки будет равен индексу выбранного столбца, то ему будет
            присвоено значение из таблицы
            """
            current_row = []
            for col in range(9):
                current_row.append(str(model.index(row, col).data()))
            if 'Руководство аспирантом' in model.index(row, 6).data():
                names = extract_names(model.index(row, 6).data())
                dialog = NameSelectionDialog(names)
                if dialog.exec_() == QDialog.Accepted:
                    selected_item = dialog.get_selected_item()
                    current_row[6] = 'Руководство аспирантом ('
                    current_row[6] += selected_item + ')'
                    current_row[8] = int(current_row[8]) - 1
            for col in range(9, model.columnCount()):
                if col == column:
                    current_row.append(str(model.index(row, col).data()))
                else:
                    current_row.append('')
            row_data[row] = current_row
    return row_data, selected_item


def insert_rows_to_table_view(rows_to_insert, model_to_insert):
    """func."""
    start_row = model_to_insert._startEditRow
    model_ids = model_to_insert.getIds()
    for row in rows_to_insert:
        if row[0] in model_ids:
            model_to_insert.addToRow(
                model_ids[row[0]], row, start_row)
        else:
            model_to_insert.appendRow(row)
            model_to_insert.addId(row[0])


def replace_rows(model, rep_data, asp):
    """func."""
    """
    Получает разницу и меняет строки.
    rep_data ->
    [[i, list]]
    i - row index, list - row
    """
    data_dict = model.get_diff()
    list_of_keys = data_dict.keys()
    for i in rep_data.keys():
        if i in list_of_keys:
            model.divide_changed_row(i, data_dict[i], asp)
        else:
            model.divide_row(i, rep_data[i])


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

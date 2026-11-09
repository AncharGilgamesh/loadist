"""Проверки сохранения, номеров, фамилии и отката строк без окна Qt."""

import sqlite3

import pytest

import Models.DataHandler as DH
import Models.SqlHandler as SQH


def _use_temp_db(monkeypatch, tmp_path):
    monkeypatch.setattr(SQH, "pathDb", str(tmp_path / "nagruzka.db"))


def test_failed_teacher_save_keeps_previous_rows(monkeypatch, tmp_path):
    """Сбой вставки откатывает удаление, старые преподаватели остаются."""
    _use_temp_db(monkeypatch, tmp_path)
    SQH.create_teachers_table()
    original = [(1, "Иванов И.И.", "", "", "доцент", 0, "")]
    SQH.insert_into_teachers_table(original)
    broken = [
        (2, "Петров П.П.", "", "", "доцент", 0, ""),
        (2, "Сидоров С.С.", "", "", "доцент", 0, ""),
    ]
    with pytest.raises(sqlite3.IntegrityError):
        SQH.insert_into_teachers_table(broken)
    assert SQH.select_all_from_table("teachers") == original


def test_position_with_quote_is_read_by_parameter(monkeypatch, tmp_path):
    """Название с апострофом читается параметризованным запросом."""
    _use_temp_db(monkeypatch, tmp_path)
    SQH.create_doljnosti_table()
    title = "доцент O'Brien"
    SQH.insert_into_doljnost_table([(title, 900.5)])
    row = SQH.get_col_where("stavka", "doljnost", title, "doljnosti")
    assert row == (900.5,)


def test_make_numberable_leaves_columns_before_nine():
    """Числами становятся только ячейки часов, начиная с колонки 9."""
    row = ["4", "b", "c", "d", "e", "f", "g", "h", "текст", "12.0", "1.5"]
    result = DH.makeNumberable([row])
    assert result[0][0] == "4"
    assert result[0][8] == "текст"
    assert result[0][9] == 12
    assert result[0][10] == 1.5


def test_name_not_three_words_is_kept():
    """Фамилия не из трёх слов возвращается как есть и не бросает исключение."""
    assert DH.return_fio_inicials("Иванов Иван", "Обычная") == "Иванов Иван"
    assert DH.return_fio_inicials("Иванов", "Почасовая") == "Иванов"
    assert DH.return_fio_inicials("Иванов Иван Иванович", "Обычная") == "Иванов И.И."


def test_next_row_id_is_one_past_the_maximum():
    """Новый номер — максимум плюс один, а не число строк."""
    ids = [1, 3, 4]
    assert DH.next_row_id(ids) == 5
    assert DH.next_row_id(ids) != len(ids)


def test_duplicate_position_save_keeps_previous_rows(monkeypatch, tmp_path):
    """Повтор должности откатывает запись, старые строки остаются."""
    _use_temp_db(monkeypatch, tmp_path)
    SQH.create_doljnosti_table()
    original = [("доцент", 900.0), ("профессор", 1200.0)]
    SQH.insert_into_doljnost_table(original)
    duplicate = [("доцент", 900.0), ("доцент", 1.0)]
    with pytest.raises(sqlite3.IntegrityError):
        SQH.insert_into_doljnost_table(duplicate)
    assert SQH.select_all_from_table("doljnosti") == original


def test_restore_order_keeps_the_lower_row():
    """Верхний индекс раньше нижнего не сдвигает вторую строку."""
    rows = ["above", "upper", "neighbor", "lower"]
    saved = {1: "upper-original", 3: "lower-original"}
    assert DH.restore_row_order(saved) == [3, 1]
    for index in DH.restore_row_order(saved):
        del rows[index]
        rows.insert(index, saved[index])
    assert rows == ["above", "upper-original", "neighbor", "lower-original"]


def test_empty_semester_returns_error():
    """Пустой семестр не роняет разбор и возвращает текст ошибки."""
    row = [""] * 9
    osen, vesna, error = DH.divideOsenVesna([row])
    assert osen is None
    assert vesna is None
    assert error == "Не указан семестр"


def _model_row(semester, discipline, lecture):
    row = [1, "отд", "каф", "09.03.01", 1, semester, discipline, "П-101", 20]
    hours = [0] * 16
    hours[0] = lecture
    row.extend(hours)
    return row


def test_parse_non_negative_number_accepts_comma_and_rejects_sign():
    """Запятая становится точкой, минус и дробь в целом числе отвергаются."""
    number, error = DH.parse_non_negative_number("12,5")
    assert number == 12.5
    assert error is None
    number, error = DH.parse_non_negative_number("-1")
    assert number is None
    assert error == "Введите неотрицательное число"
    number, error = DH.parse_non_negative_number("4", integer=True)
    assert number == 4
    assert error is None
    number, error = DH.parse_non_negative_number("4.2", integer=True)
    assert number is None
    assert error == "Введите целое неотрицательное число"


def test_divide_osen_vesna_splits_semesters_and_rejects_nine():
    """Семестры 1 и 2 расходятся по спискам, 9 возвращает текст ошибки."""
    autumn = _model_row(1, "Математика", 18)
    spring = _model_row(2.0, "Физика", 20)
    osen, vesna, error = DH.divideOsenVesna([autumn, spring])
    assert error is None
    assert osen[0][6] == "Математика"
    assert osen[0][5] == 1
    assert osen[0][11] == 18
    assert vesna[0][6] == "Физика"
    assert len(osen[0]) == 27
    broken = _model_row(9, "Химия", 1)
    osen, vesna, error = DH.divideOsenVesna([broken])
    assert osen is None
    assert vesna is None
    assert error == "Семестр должен быть числом от 1 до 8"


def test_obsh_save_row_inserts_the_skipped_columns():
    """В строке общей нагрузки пустые колонки стоят на местах шаблона."""
    saved = DH.make_obsh_nagruzka_for_save([_model_row(1, "Математика", 18)])
    assert len(saved[0]) == 27
    assert saved[0][3] == ""
    assert saved[0][7] == ""
    assert saved[0][10] == ""
    assert saved[0][6] == "Математика"


def test_work_table_labels_split_duplicates_and_hourly():
    """Повтор подписи получает номер, почасовая — суффикс."""
    data = [
        (1, "Иванов Иван Иванович", 10, "Обычная"),
        (2, "Иванов Иван Иванович", 10, "Обычная"),
        (3, "Сидорова Анна Павловна", 11, "Почасовая"),
    ]
    labels = DH.work_table_labels(data)
    assert labels[1] == "Иванов И.И. (1)"
    assert labels[2] == "Иванов И.И. (2)"
    assert labels[3] == "Сидорова А.П. (почас)"


def test_sum_lists_adds_hour_cells_and_skips_blanks():
    """Сумма переноса берёт часы с 9-й колонки и пропускает пустые ячейки."""
    row = [""] * 9 + ["2", "", "3.5"]
    assert DH.sum_lists({1: row, 2: "не строка"}) == 5.5


def test_aspirant_name_and_brackets():
    """Одно имя в скобках читается, второе добавляется и снимается."""
    single = "Руководство аспирантом (Иванов И.И.)"
    assert DH.aspirant_name_from_cell(single) == "Иванов И.И."
    assert DH.aspirant_name_from_cell("Математика") is None
    both = DH.add_value_to_brackets("Петров П.П.", single)
    assert both == "Руководство аспирантом (Иванов И.И., Петров П.П.)"
    assert DH.aspirant_name_from_cell(both) is None
    left = DH.remove_value_from_brackets("Иванов И.И.", both)
    assert left == "Руководство аспирантом (Петров П.П.)"


def test_divide_aspirants_drops_the_marker():
    """Список групп для диалога не содержит строку аспирантов."""
    assert DH.divide_aspirants(["П-101", "асп", "П-102"]) == ["П-101", "П-102"]
    assert DH.data_comparsion(["П-101"], "П-101")
    assert DH.data_comparsion(["П-101"], "П-102") is False


def test_next_row_id_without_numbers_is_zero():
    """Пустой список номеров даёт 0, мусор пропускается."""
    assert DH.next_row_id([]) == 0
    assert DH.next_row_id(["x", 2]) == 3


def test_teacher_rename_updates_work_table_fio(monkeypatch, tmp_path):
    """Новая фамилия записывается и в рабочие таблицы этого преподавателя."""
    _use_temp_db(monkeypatch, tmp_path)
    SQH.create_teachers_table()
    SQH.create_work_table()
    SQH.insert_into_teachers_table(
        [(1, "Иванов Иван Иванович", "", "", "доцент", 0, "")]
    )
    SQH.insert_into_work_table(
        [(1, "Иванов Иван Иванович", 1, "Обычная", 1, 0, 0, 0, 100)]
    )
    SQH.update_teachers(
        (1, "Петров Петр Петрович", "доцент", "к.т.н.", "доцент", 2, "")
    )
    teacher = SQH.select_all_from_table("teachers")
    work = SQH.select_all_from_table("workTables")
    assert teacher[0][1] == "Петров Петр Петрович"
    assert work[0][1] == "Петров Петр Петрович"
    assert work[0][2] == 1


def test_replace_teachers_rolls_back_missing_teacher(monkeypatch, tmp_path):
    """Ссылка на отсутствующего преподавателя возвращает прежние строки."""
    _use_temp_db(monkeypatch, tmp_path)
    SQH.create_teachers_table()
    SQH.create_work_table()
    teachers = [(1, "Иванов Иван Иванович", "", "", "доцент", 0, "")]
    works = [(1, "Иванов Иван Иванович", 1, "Обычная", 1, 0, 0, 0, 100)]
    SQH.replace_teachers_and_work_tables(teachers, works)
    missing = [(2, "Нет такого", 99, "Обычная", 1, 0, 0, 0, 10)]
    with pytest.raises(sqlite3.IntegrityError):
        SQH.replace_teachers_and_work_tables(teachers, missing)
    assert SQH.select_all_from_table("teachers") == teachers
    assert SQH.select_all_from_table("workTables") == works

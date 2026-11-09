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

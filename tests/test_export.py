"""tests."""

from openpyxl import load_workbook

import Models.SqlHandler as SQH
from Example.run_example import (
    TABLE_LIMIT,
    TEACHER_LABEL,
    TEACHER_NAME,
    export_sample,
    first_semester_record,
    load_records,
)


def _use_temp_db(monkeypatch, tmp_path):
    monkeypatch.setattr(SQH, "pathDb", str(tmp_path / "nagruzka.db"))
    monkeypatch.setattr(SQH, "SETTING_DB", str(tmp_path / "settings.db"))


def _markers(sheet):
    names = ("Осенний семестр", "Весенний семестр", "Итого за год")
    found = []
    for row in range(1, sheet.max_row + 1):
        value = sheet.cell(row=row, column=3).value
        if value in names:
            found.append((value, row))
    return found


def test_export_sample(monkeypatch, tmp_path):
    _use_temp_db(monkeypatch, tmp_path)
    output = tmp_path / "output"
    result = export_sample(output)

    plan = load_workbook(result["plan"])
    sheet = plan["ШАА"]
    markers = _markers(sheet)
    assert [name for name, _row in markers] == [
        "Осенний семестр",
        "Весенний семестр",
        "Итого за год",
    ]
    osen_row = markers[0][1]
    vesna_row = markers[1][1]
    itogo_row = markers[2][1]
    assert osen_row < vesna_row < itogo_row
    autumn = first_semester_record(1)
    spring = first_semester_record(2)
    assert sheet.cell(row=osen_row + 1, column=7).value == autumn["discipline"]
    assert sheet.cell(row=osen_row + 1, column=12).value == autumn["hours"]["лек"]
    assert sheet.cell(row=vesna_row + 1, column=7).value == spring["discipline"]
    assert sheet.cell(row=vesna_row + 1, column=12).value == spring["hours"]["лек"]
    assert vesna_row - osen_row > 20
    assert itogo_row - vesna_row > 20
    assert sheet["E3"].value == TEACHER_NAME
    assert sheet["E1"].value == "Индивидуальный план на 2025/2026 уч.год"
    assert sheet["AA3"].value == TABLE_LIMIT

    general = load_workbook(result["general"])
    general_sheet = general["нагрузка кафедры"]
    texts = []
    for row in general_sheet.iter_rows(values_only=True):
        texts.extend(cell for cell in row if isinstance(cell, str))
    assert autumn["discipline"] in texts
    assert spring["discipline"] in texts
    assert "Руководство аспирантом (Соколов А.А., Егорова М.В.)" in texts
    assert "ИВТ-401" in texts
    assert "09.04.01 Информатика и вычислительная техника" in texts

    stats = load_workbook(result["statistics"])
    values = []
    for row in stats.active.iter_rows(values_only=True):
        values.extend(row)
    assert TEACHER_LABEL in values
    assert result["hours"] in values
    assert result["rows"] == len(load_records())
    assert result["rows"] > 70
    assert result["hours"] > 3000
    assert len(SQH.select_all_from_table("teachers")) == 11
    assert len(SQH.select_all_from_table("workTables")) == 12
    assert len(SQH.select_all_from_table("kafedraGroups")) == 16
    assert len(SQH.select_all_from_table("disciplines")) > 30

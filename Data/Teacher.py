"""Итог часов одной рабочей таблицы."""


class Teacher():
    """id таблицы, id преподавателя и итог часов."""

    def __init__(self, tbl_id, tchr_id, total):
        """func."""
        self._totalTime = total
        self._tbl_id = tbl_id
        self._teacher_id = tchr_id

    def get_tbl_id(self):
        """func."""
        return self._tbl_id

    def get_teacher_id(self):
        """func."""
        return self._teacher_id

    def getTotalTime(self):
        """func."""
        return self._totalTime

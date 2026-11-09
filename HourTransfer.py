"""Перенос часов между общей нагрузкой и таблицей преподавателя."""

from PyQt5.QtWidgets import QDialog, QMessageBox

import Models.DataHandler as DH
from UICode.NameSelectionDialog import NameSelectionDialog


class HourTransfer:
    """Перенос выбранных ячеек преподавателю и обратно."""

    def _choose_aspirant(self, names):
        """Спрашивает имя аспиранта. None, если окно закрыли без выбора."""
        dialog = NameSelectionDialog(names)
        if dialog.exec_() != QDialog.Accepted:
            return None
        return dialog.get_selected_item()

    def row_inserting(self):
        """Перенос часов выбранному преподавателю."""
        selected_indexes = self.leftTableView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Ошибка", "Выберите ячейки")
            return
        row_data = DH.collect_selected_rows(
            self.model1, selected_indexes, self._choose_aspirant
        )
        if row_data is None:
            return
        difference = self.check_hours(row_data)
        if difference < 0:
            self.get_back_basic()
            self.model1.clearChangesDict()
            self.model1.clearBasicDict()
            self.model1.clear_edited_dict()
            QMessageBox.warning(
                self, "Ошибка", "Часы превышены на " + str(abs(difference))
            )
            return
        tbl_id = self.current_work_table_id()
        DH.move_rows(
            self.model1,
            self._rtblModels[tbl_id],
            selected_indexes,
            row_data,
        )
        self.leftTableView.reset()

    def check_hours(self, row_data):
        """func."""
        tbl_id = self.current_work_table_id()
        transfer_sum = DH.sum_lists(row_data)
        table_sum = sum(self._rtblModels[tbl_id].getAllColSum())
        table_limit = self._prepods[tbl_id].getTotalTime()
        difference = table_limit - transfer_sum - table_sum
        return difference

    def get_back_basic(self):
        """Возвращает изменённые строки с большего номера к меньшему."""
        basic_data = self.model1.get_basic_rows()
        for key in sorted(basic_data, key=int, reverse=True):
            index = int(key)
            self.model1.removeRows(index, 1)
            self.model1.insertRow(index, basic_data[key].copy())
        self.model1.updateIds()

    def row_outserting(self):
        """Возврат часов в общую нагрузку."""
        selected_indexes = self.rightTableView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Ошибка", "Выберите ячейки")
            return
        model = self._rtblModels[self.current_work_table_id()]
        row_data = DH.collect_selected_rows(
            model, selected_indexes, self._choose_aspirant
        )
        if row_data is None:
            return
        DH.move_rows(model, self.model1, selected_indexes, row_data)
        self.rightTableView.reset()

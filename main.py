"""Распределитель учебной нагрузки.

Sorry for that
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,\
      QMessageBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from Models.ExcelHandler import ExcelHandler, XlsHandler
from Data.Teacher import Teacher
from UICode.DoljnostiAdd import DoljnostAdd
from UICode.PrepodAddNew import PrepodAdd
from UICode.GroupAdd import GroupAdd
from UICode.NapPodAdd import NapPodAdd
from UICode.DiscipAdd import DisciplineAdd
from UICode.WorkTableAdd import CreateWorkTable
from UICode.NameSelectionDialog import NameSelectionDialog
from UICode.SettingsDialog import SettingsDialog
from Models.Models import MyModel, KafedraModels, MyListModel
from PyQt5.QtCore import QFile, QTextStream, QPersistentModelIndex
import Models.SqlHandler as SQH
import Models.DataHandler as DH
import Resources.breeze_resources
import Resources.res_images
import os

import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, 'UI', 'mainView.ui')


class MainWindow(QMainWindow):
    """main."""

    def __init__(self):
        """func."""
        super(MainWindow, self).__init__()
        loadUi(UI_PATH, self)
        self._rtblModels = {}
        self._prepods = {}
        self.kafedraModel = None
        self.nap_pod_model = None
        self._discipline_model = None
        self._doljnosti_model = None
        self.nap_code_model = None
        self._dljnst_combo_model = None
        self._groups_model = None
        self._teacher_tbl_model = None
        self._teacher_names_model = None
        self._work_tbl_model = None
        self._stat_model = None
        self._data_loaded = False
        SQH.create_tables()
        self.update_teacher_table()
        self.updateKafedraGroups()
        self.update_kafedra_doljnosti()
        self.update_discipline()
        self.update_nap_pod()
        self.update_nap_code()
        self.update_dljnst_combo_model()
        self.update_groups_without_aspirants()
        self.update_teacher_names()
        self.update_work_table()
        self.update_prepods_dict()
        self.updatePrepodsComboBox()
        self.testButton.clicked.connect(self.row_inserting_mod)
        self.transferButton.clicked.connect(self.row_inserting_mod)
        self.transferBackButton.clicked.connect(self.row_outserting_mod)
        self.loadButton.clicked.connect(self.loadData)
        self.uploadButton.clicked.connect(self.uploadData)
        self.saveMainNagruzka.clicked.connect(self.save_obsh_nagruzka)
        self.mainTeacherComboBox.currentIndexChanged.connect(
            self.onComboBoxIndexChanged)
        # Dojlnosti
        self.addDoljnostButton.clicked.connect(self.open_add_doljnosti)
        self.saveDoljnostiButton.clicked.connect(self.save_doljnost)
        self.delCurrentDoljnostButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
             self.doljnostiTableView, self._doljnosti_model
            )
        )
        self.delAllDoljnostiButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self._doljnosti_model)
        )
        # Prepods
        self.addPrepodButton.clicked.connect(self.open_add_teacher)
        self.savePreodButton.clicked.connect(self.save_teacher)
        self.editPrepodButton.clicked.connect(self.open_edit_teacher)
        self.delPrepodButton.clicked.connect(
            lambda: self.del_cur_row_tbl_view_for_sel_rows(
             self.prepodsTableView, self._teacher_tbl_model
            )
        )
        self.delAllPrepodButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self._teacher_tbl_model)
        )
        # Work tables
        self.addWorkTblButton.clicked.connect(self.open_work_create)
        self.saveWorkTblsButton.clicked.connect(self.save_work_table)
        self.editWorkTblButton.clicked.connect(self.open_edit_work_table)
        self.delWorkTblButton.clicked.connect(
            lambda: self.del_cur_row_tbl_view_for_sel_rows(
             self.workTableView, self._work_tbl_model
            )
        )
        self.delAllWorkTblsButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self._work_tbl_model))
        # Groups
        self.addGroupButton.clicked.connect(self.open_add_group)
        # self.delCurrentGrButton.clicked.connect(self.del_current_group)
        self.delCurrentGrButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
             self.groupsTableView, self.kafedraModel))
        self.saveGroups.clicked.connect(self.save_groups)
        self.dellAllGrButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self.kafedraModel))
        # Направления подготовки
        self.addNapPodButton.clicked.connect(self.open_add_napravlenia)
        self.saveNapPodButton.clicked.connect(self.save_nap_pod)
        self.delCurrNapButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
             self.napPodTableView, self.nap_pod_model
            ))
        self.dellAllNapPod.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self.nap_pod_model)
        )
        # Дисциплины
        self.addDisciplineButton.clicked.connect(self.open_add_discipline)
        self.saveDisButton.clicked.connect(self.save_discipline)
        self.delCurrDisButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
             self.disciplineTableView, self._discipline_model
            )
        )
        self.dellAllDisButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self._discipline_model)
        )
        # Статистика
        self.refreshStatButton.clicked.connect(self.set_statistics)
        self.saveStatButton.clicked.connect(self.save_statistics)
        # Меню
        self.loadDataAction.triggered.connect(self.loadData)
        self.saveNagrAction.triggered.connect(self.save_obsh_nagruzka)
        self.savePrepodNagrAction.triggered.connect(self.uploadData)
        self.settingsAction.triggered.connect(self.open_settings)
        self.exitAction.triggered.connect(lambda: self.close())
        # Навигация
        self.goToKafedraButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(
             self.stackedWidget.currentIndex() + 1))
        self.goToMainButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(
             self.stackedWidget.currentIndex() - 1))
        self.setWindowIcon(QtGui.QIcon(
            QtGui.QPixmap(':/icons/Images/logo.png')))
        self.setWindowTitle('Распределитель учебной нагрзуки')

    def get_checked_indexes(self, model, selected_indexes):
        """func."""
        # selected_indexes = tbl_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, 'Ошибка', 'Выберите ячейки')
            return
        # для хранения выбранных строк
        # model = tbl_view.model()
        row_data = {}
        for index in selected_indexes:
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
                selected_item = None
                for col in range(9):
                    current_row.append(str(model.index(row, col).data()))
                if 'Руководство аспирантом' in model.index(row, 6).data():
                    names = DH.extract_names(model.index(row, 6).data())
                    dialog = NameSelectionDialog(names)
                    if dialog.exec_() == QDialog.Accepted:
                        selected_item = dialog.get_selected_item()
                        current_row[6] = 'Руководство аспирантом (' + selected_item + ')'
                        current_row[8] = int(current_row[8]) - 1
                for col in range(9, model.columnCount()):
                    if col == column:
                        current_row.append(str(model.index(row, col).data()))
                    else:
                        current_row.append('')
                row_data[row] = current_row
        return row_data, selected_item

    def check_for_selection(self, model, selected_indexes):
        """func."""
        edited = model.get_edited_cells()
        selected_index_control = {}
        for index in selected_indexes:
            # строка текущего индекса
            row = index.row()
            # столбец текущего индекса
            column = index.column()
            if row in selected_index_control.keys():
                selected_index_control[row].add(column)
            else:
                selected_index_control[row] = {column}
        selected = selected_index_control
        keys_to_delete = set()
        for k in edited.keys():
            if k in selected.keys():
                # Разность множеств
                edited[k] = edited[k] - selected[k]
                if not edited[k]:
                    keys_to_delete.add(k)
        for k in keys_to_delete:
            del edited[k]
        if edited:
            for k, v in edited.items():
                for i in v:
                    model.get_back_not_selected_edited_cols(k, i)
        return edited

    def add_rows_to_second_table(self, model_to_insert, row_data, startRow):
        """func."""
        modelIds = model_to_insert.getIds()
        rows_to_insert = [x for x in row_data.values()]
        for row in rows_to_insert:
            if row[0] in modelIds:
                model_to_insert.addToRow(
                    modelIds[row[0]], row, startRow)
            else:
                model_to_insert.appendRow(row)
                model_to_insert.addId(row[0])

    def row_inserting_mod(self):
        """func."""
        model = self.leftTableView.model()
        selected_indexes = self.leftTableView.selectedIndexes()
        row_data, selected_item = self.get_checked_indexes(
            model, selected_indexes)
        # check_for_difference
        difference = self.check_hours(row_data)
        if difference < 0:
            self.get_back_basic()
            model.clearChangesDict()
            model.clearBasicDict()
            model.clear_edited_dict()
            QMessageBox.warning(
                self,
                'Ошибка',
                'Часы превышены на ' + str(abs(difference))
            )
            return
        # check for selection
        edited = self.check_for_selection(model, selected_indexes)
        # replace_rows
        self.replace_rows(row_data, selected_item, edited)
        model.clear_edited_dict()
        self.leftTableView.reset()
        # adding_rows
        model_name = self.mainTeacherComboBox.currentText()
        model_to_insert = self._rtblModels[model_name]
        startRow = model._startEditRow
        self.add_rows_to_second_table(model_to_insert, row_data, startRow)
        model.clearChangesDict()
        model.clearBasicDict()

    def row_outserting_mod(self):
        """func."""
        selected_indexes = self.rightTableView.selectedIndexes()
        model_name = self.mainTeacherComboBox.currentText()
        model = self._rtblModels[model_name]
        row_data, selected_item = self.get_checked_indexes(
            model, selected_indexes)
        # check for selection
        edited = self.check_for_selection(model, selected_indexes)
        # replace_rows
        self.replace_rows_outserting(row_data, selected_item, edited)
        model.clear_edited_dict()
        self.rightTableView.reset()
        # adding rows
        model_to_insert = self.model1
        startRow = model._startEditRow
        self.add_rows_to_second_table(model_to_insert, row_data, startRow)
        model.clearChangesDict()
        model.clearBasicDict()

    def row_inserting(self):
        """func."""
        selected_indexes = self.leftTableView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, 'Ошибка', 'Выберите ячейки')
            return
        # для хранения выбранных строк
        row_data = {}
        for index in selected_indexes:
            # строка текущего индекса
            row = index.row()
            # столбец текущего индекса
            column = index.column()
            if row in row_data.keys():
                col_value = str(self.model1.index(row, column).data())
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
                selected_item = None
                for col in range(9):
                    current_row.append(str(self.model1.index(row, col).data()))
                if 'Руководство аспирантом' in self.model1.index(row, 6).data():
                    names = DH.extract_names(self.model1.index(row, 6).data())
                    dialog = NameSelectionDialog(names)
                    if dialog.exec_() == QDialog.Accepted:
                        selected_item = dialog.get_selected_item()
                        current_row[6] = 'Руководство аспирантом (' + selected_item + ')'
                        current_row[8] = int(current_row[8]) - 1
                for col in range(9, self.model1.columnCount()):
                    if col == column:
                        current_row.append(str(self.model1.index(row, col).data()))
                    else:
                        current_row.append('')
                row_data[row] = current_row
        difference = self.check_hours(row_data)
        if difference < 0:
            self.get_back_basic()
            self.model1.clearChangesDict()
            self.model1.clearBasicDict()
            self.model1.clear_edited_dict()
            QMessageBox.warning(
                self,
                'Ошибка',
                'Часы превышены на ' + str(abs(difference))
            )
            return
        # check for selection
        edited = self.model1.get_edited_cells()
        selected_index_control = {}
        for index in selected_indexes:
            # строка текущего индекса
            row = index.row()
            # столбец текущего индекса
            column = index.column()
            if row in selected_index_control.keys():
                selected_index_control[row].add(column)
            else:
                selected_index_control[row] = {column}
        selected = selected_index_control
        keys_to_delete = set()
        for k in edited.keys():
            if k in selected.keys():
                # Разность множеств
                edited[k] = edited[k] - selected[k]
                if not edited[k]:
                    keys_to_delete.add(k)
        for k in keys_to_delete:
            del edited[k]
        if edited:
            for k, v in edited.items():
                for i in v:
                    self.model1.get_back_not_selected_edited_cols(k, i)
        # в Edited хранятся те клетки, которые отредакитрованы, но не выделены
        self.replace_rows(row_data, selected_item, edited)
        self.model1.clear_edited_dict()
        # self.compare_selection_and_edit(
        #     self.model1, edited_cells, selected_indexes)

        # end of check
        self.leftTableView.reset()
        # Список для передачи в соседнюю таблицу
        rows_to_insert = [x for x in row_data.values()]
        # rowcount = len(rows_to_insert)
        model_name = self.mainTeacherComboBox.currentText()
        modelIds = self._rtblModels[model_name].getIds()
        startRow = self.model1._startEditRow
        for row in rows_to_insert:
            if row[0] in modelIds:
                self._rtblModels[model_name].addToRow(
                    modelIds[row[0]], row, startRow)
            else:
                self._rtblModels[model_name].appendRow(row)
                self._rtblModels[model_name].addId(row[0])
        # Обновляем модели после передачи информации
        self.model1.clearChangesDict()
        self.model1.clearBasicDict()

    def compare_selection_and_edit(self, model, edited_cells, selected_indx):
        """func."""
        edited = edited_cells
        selected_indexes = selected_indx
        selected_index_control = {}
        for index in selected_indexes:
            # строка текущего индекса
            row = index.row()
            # столбец текущего индекса
            column = index.column()
            if row in selected_index_control.keys():
                selected_index_control[row].add(column)
            else:
                selected_index_control[row] = {column}
        selected = selected_index_control
        keys_to_delete = set()
        for k in edited.keys():
            if k in selected.keys():
                # Разность множеств
                edited[k] = edited[k] - selected[k]
                if not edited[k]:
                    keys_to_delete.add(k)
        for k in keys_to_delete:
            del edited[k]
        if edited:
            for k, v in edited.items():
                for i in v:
                    model.get_back_not_selected_edited_cols(k, i)
        model.clear_edited_dict()

    def check_hours(self, row_data):
        """func."""
        model_name = self.mainTeacherComboBox.currentText()
        transfer_sum = DH.sum_lists(row_data)
        table_sum = sum(self._rtblModels[model_name].getAllColSum())
        table_limit = self._prepods[model_name].getTotalTime()
        difference = table_limit - transfer_sum - table_sum
        return difference

    def get_back_basic(self):
        """func."""
        basic_data = self.model1.get_basic_rows()
        for k, v in basic_data.items():
            self.model1.removeRows(int(k), 1)
            self.model1.insertRow(int(k), v)
        self.model1.updateIds()

    def replace_rows(self, rep_data, asp, edited):
        """func."""
        """
        Получает разницу и меняет строки.
        rep_data ->
        [[i, list]]
        i - row index, list - row
        """
        data_dict = self.model1.get_diff()
        edited_keys = edited.keys()
        list_of_keys = data_dict.keys()
        for i in rep_data.keys():
            if i in list_of_keys and i not in edited_keys:
                self.model1.divide_changed_row(i, data_dict[i], asp)
            elif i in list_of_keys and i in edited_keys:
                self.model1.special_divide_row(
                    i, rep_data[i], data_dict[i], asp)
            else:
                self.model1.divide_row(i, rep_data[i])

    def replace_rows_outserting(self, rep_data, asp, edited):
        """func."""
        model_name = self.mainTeacherComboBox.currentText()
        model = self._rtblModels[model_name]
        data_dict = model.get_diff()
        list_of_keys = data_dict.keys()
        edited_keys = edited.keys()
        for i in rep_data.keys():
            if i in list_of_keys and i not in edited_keys:
                model.divide_changed_row(i, data_dict[i], asp)
            elif i in list_of_keys and i in edited_keys:
                model.special_divide_row(
                    i, rep_data[i], data_dict[i], asp)
            else:
                model.divide_row(i, rep_data[i])
                # print(i, rep_data[i])

    def row_outserting(self):
        """func."""
        selected_indexes = self.rightTableView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, 'Ошибка', 'Выберите ячейки')
            return
        model_name = self.mainTeacherComboBox.currentText()
        model = self._rtblModels[model_name]
        # для хранения выбранных строк
        row_data = {}
        for index in selected_indexes:
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
                selected_item = None
                for col in range(9):
                    current_row.append(str(model.index(row, col).data()))
                if 'Руководство аспирантом' in model.index(row, 6).data():
                    names = DH.extract_names(model.index(row, 6).data())
                    dialog = NameSelectionDialog(names)
                    if dialog.exec_() == QDialog.Accepted:
                        selected_item = dialog.get_selected_item()
                        current_row[6] = 'Руководство аспирантом (' + selected_item + ')'
                        current_row[8] = int(current_row[8]) - 1
                for col in range(9, model.columnCount()):
                    if col == column:
                        current_row.append(str(model.index(row, col).data()))
                    else:
                        current_row.append('')
                row_data[row] = current_row
        # check for selection
        edited = model.get_edited_cells()
        selected_index_control = {}
        for index in selected_indexes:
            # строка текущего индекса
            row = index.row()
            # столбец текущего индекса
            column = index.column()
            if row in selected_index_control.keys():
                selected_index_control[row].add(column)
            else:
                selected_index_control[row] = {column}
        selected = selected_index_control
        keys_to_delete = set()
        for k in edited.keys():
            if k in selected.keys():
                # Разность множеств
                edited[k] = edited[k] - selected[k]
                if not edited[k]:
                    keys_to_delete.add(k)
        for k in keys_to_delete:
            del edited[k]
        if edited:
            for k, v in edited.items():
                for i in v:
                    model.get_back_not_selected_edited_cols(k, i)
        self.replace_rows_outserting(row_data, selected_item, edited)
        model.clear_edited_dict()
        self.rightTableView.reset()
        # Список для передачи в соседнюю таблицу
        rows_to_insert = [x for x in row_data.values()]
        # rowcount = len(rows_to_insert)
        modelIds = self.model1.getIds()
        startRow = self.model1._startEditRow
        for row in rows_to_insert:
            if row[0] in modelIds:
                self.model1.addToRow(
                    modelIds[row[0]], row, startRow)
            else:
                self.model1.appendRow(row)
                self.model1.addId(row[0])
        # Обновляем модели после передачи информации
        model.clearChangesDict()
        model.clearBasicDict()

    # Настройки
    def open_settings(self):
        """func."""
        settings = SettingsDialog()
        settings.exec_()

    # Статистика
    def set_statistics(self):
        """func."""
        header, data = DH.get_settings_to_stats_table()
        self._stat_model = KafedraModels(data, header)
        self.statisticTableView.setModel(self._stat_model)
        data_to_insert = DH.get_nagruzka_stats(self.leftTableView)
        self._stat_model.insertRow(0, data_to_insert)
        # таблицы преподавателей
        if self._rtblModels:
            DH.set_prepods_stats(self._rtblModels, self._stat_model)
        self.statisticTableView.resizeColumnsToContents()

    def save_statistics(self):
        """func."""
        data = self._stat_model.get_data()
        header = self._stat_model.get_header()
        data.insert(0, header)
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options)
        if not fname:
            return
        excel = ExcelHandler()
        excel.write_statistics(data, fname)

    # Универсальные функции для модуля кафедры
    # Удаление всей инфы из таблицы в Kafedra модуле
    def remove_all_rows_in_table_view(self, model):
        """func."""
        data_len = model.rowCount()
        model.removeRows(0, data_len)

    # Удаление выбранной строки для типа выбора Select Items
    def del_current_row_in_table_view(self, tableView, model):
        """func."""
        """Удаляет выбранные строки для selectionBehaviour - Select Items"""
        index_list = []
        for model_index in tableView.selectedIndexes():
            index = QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            model.removeRow(index.row())

    # Удаление выбранной строки для типа выбора Select Rows
    def del_cur_row_tbl_view_for_sel_rows(self, tableView, model):
        """func."""
        """
        Удаляет выбранные строки для selectionBehaviour - Select Rows
        """
        selection_model = tableView.selectionModel()
        selected_indexes = selection_model.selectedRows()
        for index in selected_indexes:
            model.removeRow(index.row())

    def get_selected_row_kafedra(self, tableView, row):
        """func."""
        selection_model = tableView.selectionModel()
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            QMessageBox.information(
                self,
                'Выберите строку',
                'Выберите строку, которую хотите редактировать'
            )
            return False
        model = tableView.model()
        for col in range(model.columnCount()):
            data = model.data(
                model.index(selected_rows[0].row(), col), Qt.DisplayRole)
            row.append(data)
        return True

    # Добавить должности
    def open_add_doljnosti(self):
        """func."""
        self.addDoljnosti = DoljnostAdd()
        self.addDoljnosti.submitted.connect(self.add_doljnosti)
        self.addDoljnosti.show()

    def save_doljnost(self):
        """func."""
        data_to_save = self._doljnosti_model.get_data()
        SQH.insert_into_doljnost_table(data_to_save)
        self.update_dljnst_combo_model()

    def add_doljnosti(self, dljnst, stvka):
        """func."""
        list_to_add = [dljnst, stvka]
        self._doljnosti_model.insertRow(0, list_to_add)

    def update_kafedra_doljnosti(self):
        """func."""
        doljnosti_data = SQH.select_all_from_table('doljnosti')
        doljnosti_header = ['Должность', 'Ставка(час)']
        self._doljnosti_model = KafedraModels(doljnosti_data, doljnosti_header)
        self.doljnostiTableView.setModel(self._doljnosti_model)

    def update_dljnst_combo_model(self):
        """func."""
        dljnsti = self._doljnosti_model.get_col_by_name('Должность')
        self._dljnst_combo_model = MyListModel(dljnsti)

    # Занимаемся преподавателями
    # Смотри на это, как пример порядка определения
    # Преподаватели
    def open_add_teacher(self):
        """func."""
        if not self._dljnst_combo_model.rowCount():
            QMessageBox.warning(
                self,
                'Ошибка',
                'Для продолжения работы добавьте должности'
            )
            return
        self.addTeacher = PrepodAdd()
        # self.addTeacher.set_dljnsti(self._dljnst_combo_model)
        # self.addTeacher.data_signal.connect(self.add_teacher)
        # self.addTeacher.set_groups(self._groups_model)
        self.teacher_components(
            self.addTeacher,
            self._dljnst_combo_model,
            self._groups_model,
            self.add_teacher
        )
        self.addTeacher.show()

    def teacher_components(self, dialog, dljnst, groups, reciever):
        """func."""
        dialog.set_dljnsti(dljnst)
        dialog.data_signal.connect(reciever)
        dialog.set_groups(groups)

    def update_teacher_table(self):
        """func."""
        teacher_data = SQH.select_all_from_table('teachers')
        teacher_header = [
            'id',
            'ФИО',
            'Ученое звание',
            'Ученая степень',
            'Должность',
            'Ограничение по дипломникам',
            'Курирует группу']
        self._teacher_tbl_model = KafedraModels(teacher_data, teacher_header)
        self.prepodsTableView.setModel(self._teacher_tbl_model)
        # self.prepodsTableView.setColumnHidden(0, True)

    def add_teacher(self, data):
        """func."""
        row_count = self._teacher_tbl_model.rowCount()
        ids = self._teacher_tbl_model.get_col_by_name('id')
        if row_count in ids:
            data.insert(0, row_count + len(ids))
        else:
            data.insert(0, row_count)
        self._teacher_tbl_model.insertRow(row_count, data)

    def save_teacher(self):
        """func."""
        data = self._teacher_tbl_model.get_data()
        SQH.insert_into_teachers_table(data)
        self.update_teacher_names()
        self.check_for_del_ids()

    def update_teacher_names(self):
        """func."""
        data = self._teacher_tbl_model.get_col_by_name('ФИО')
        teacher_ids = self._teacher_tbl_model.get_col_by_name('id')
        self._teacher_names_model = MyListModel(data, teacher_ids)

    def open_edit_teacher(self):
        """func."""
        row = []
        if not self.get_selected_row_kafedra(self.prepodsTableView, row):
            return
        editTeacher = PrepodAdd()
        editTeacher.setWindowTitle('Редактировать преподавателя')
        editTeacher.set_edit_lines(row[1:])
        self.teacher_components(
            editTeacher,
            self._dljnst_combo_model,
            self._groups_model,
            lambda data: self.edit_teacher(data, row[0])
        )
        # editTeacher.data_signal.connect(
        # lambda data: self.edit_teacher(data, row[0]))
        editTeacher.show()

    def edit_teacher(self, data, id):
        """func."""
        new_data = [id] + data
        SQH.update_teachers(new_data)
        self.update_teacher_table()

    # Рабочие таблицы
    def open_work_create(self):
        """func."""
        if not self._teacher_names_model.rowCount():
            QMessageBox.warning(
                self,
                'Ошибка',
                'Для продолжения работы добавьте преподавателей'
            )
            return
        self.addWorkTable = CreateWorkTable()
        self.addWorkTable.set_teachers(self._teacher_names_model)
        self.addWorkTable.data_signal.connect(self.add_work_table)
        self.addWorkTable.show()

    def update_work_table(self):
        """func."""
        work_tbl_data = SQH.select_all_from_table('workTables')
        work_tbl_headers = [
            'id',
            'ФИО',
            '№ пр.',
            'Тип',
            'Осн. ставка',
            'Почас.',
            'Почас. доп.',
            'Совместительство',
            'Итог'
        ]
        self._work_tbl_model = KafedraModels(work_tbl_data, work_tbl_headers)
        self.workTableView.setModel(self._work_tbl_model)
        # self.workTableView.setColumnHidden(0, True)
        # self.workTableView.setColumnHidden(2, True)

    def add_work_table(self, data):
        """func."""
        row_count = self._work_tbl_model.rowCount()
        data.insert(0, row_count)
        self._work_tbl_model.insertRow(row_count, data)

    def save_work_table(self):
        """func."""
        data = self._work_tbl_model.get_data()
        SQH.insert_into_work_table(data)
        self.update_prepods_dict()
        if self._data_loaded:
            self.update_right_models(self._header)
        self.updatePrepodsComboBox()

    def open_edit_work_table(self):
        """func."""
        row = []
        if not self.get_selected_row_kafedra(self.workTableView, row):
            return
        edit_work_table_window = CreateWorkTable()
        edit_work_table_window.set_teachers(self._teacher_names_model)
        edit_work_table_window.set_edit_lines(row[1:])
        edit_work_table_window.data_signal.connect(
            lambda data: self.edit_work_table(data, row[0]))
        edit_work_table_window.exec_()

    def edit_work_table(self, data, id):
        """func."""
        new_data = [id] + data
        SQH.update_work_table(new_data)
        self.update_work_table()

    def check_for_del_ids(self):
        """func."""
        table_prepods_ids = self._work_tbl_model.get_col_by_name('№ пр.')
        prepod_ids = self._teacher_tbl_model.get_col_by_name('id')
        for id in table_prepods_ids:
            if id not in prepod_ids:
                SQH.remove_work_table_where_teacher(id)
        self.save_work_table()  # Не нравится вот это

    # Дисциплины
    def open_add_discipline(self):
        """func."""
        self.addDiscipline = DisciplineAdd()
        self.addDiscipline.set_codes(self.nap_code_model)
        self.addDiscipline.data_signal.connect(self.add_discipline)
        self.addDiscipline.show()

    def add_discipline(self, code, name):
        """func."""
        list_to_insert = [code, name]
        DH.kafedra_id_add(self._discipline_model, 'id', list_to_insert)
        # self._discipline_model.insertRow(0, list_to_insert)

    def save_discipline(self):
        """func."""
        data = self._discipline_model.get_data()
        SQH.insert_into_disciplines_table(data)

    def update_discipline(self):
        """func."""
        discipline_data = SQH.select_all_from_table('disciplines')
        discip_headers = ['id', 'Направление', 'Дисциплина']
        self._discipline_model = KafedraModels(discipline_data, discip_headers)
        self.disciplineTableView.setModel(self._discipline_model)
        self.disciplineTableView.setColumnHidden(0, True)

    # Направления подготовки
    def open_add_napravlenia(self):
        """func."""
        self.addNapPod = NapPodAdd()
        self.addNapPod.data_signal.connect(self.add_nap_pod)
        self.addNapPod.exec_()

    def update_nap_pod(self):
        """func."""
        nap_pod_data = SQH.select_all_from_table('napPod')
        nap_pod_headers = ['Код', 'Наименование']
        self.nap_pod_model = KafedraModels(nap_pod_data, nap_pod_headers)
        self.napPodTableView.setModel(self.nap_pod_model)

    def update_nap_code(self):
        """func."""
        nap_codes = self.nap_pod_model.get_col_by_name('Код')
        self.nap_code_model = MyListModel(nap_codes)

    def save_nap_pod(self):
        """func."""
        data_to_save = self.nap_pod_model.get_data()
        SQH.insert_into_napPod_table(data_to_save)
        self.update_nap_code()

    def add_nap_pod(self, code, name):
        """func."""
        data_comparison = self.nap_pod_model.get_col_by_name('Код')
        if DH.data_comparsion(data_comparison, code):
            QMessageBox.warning(self, 'Ошибка', 'Группа уже есть в таблице')
            return
        list_to_insert = [code, name]
        self.nap_pod_model.insertRow(0, list_to_insert)

    # Группы
    def open_add_group(self):
        """Open groups dialog window."""
        self.addGroup = GroupAdd()
        self.addGroup.set_codes(self.nap_code_model)
        self.addGroup.data_signal.connect(self.add_group)
        self.addGroup.exec_()

    def add_group(self, grNum, amount, curator, code):
        """Add group."""
        data_comprasion = self.kafedraModel.get_col_by_name('Группа')
        data_comprasion = DH.divide_aspirants(data_comprasion)
        if DH.data_comparsion(data_comprasion, grNum):
            QMessageBox.warning(self, 'Ошибка', 'Группа уже есть в таблице')
            return
        list_to_insert = [
            grNum,
            int(amount),
            curator,
            code
        ]
        # self.kafedraModel.insertRow(0, list_to_insert)
        DH.kafedra_id_add(self.kafedraModel, 'id', list_to_insert)
        self._groups_model = MyListModel(data_comprasion)

    def updateKafedraGroups(self):
        """Update groups."""
        kafedraData = SQH.select_all_from_table('kafedraGroups')
        kafedraHeaders = [
            'id', 'Группа', 'Кол-во людей', 'Куратор', 'Направление']
        self.kafedraModel = KafedraModels(kafedraData, kafedraHeaders)
        self.groupsTableView.setModel(self.kafedraModel)
        self.groupsTableView.setColumnHidden(0, True)

    def update_groups_without_aspirants(self):
        """Update groups model that put in prepods dialog window."""
        data = self.kafedraModel.get_col_by_name('Группа')
        data = DH.divide_aspirants(data)
        self._groups_model = MyListModel(data)

    def save_groups(self):
        """Save all groups."""
        data_to_save = self.kafedraModel.get_data()
        SQH.insert_into_groups_table(data_to_save)
        self.update_groups_without_aspirants()

    def del_current_group(self):
        """Del current group."""
        index_list = []
        for model_index in self.groupsTableView.selectedIndexes():
            index = QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.kafedraModel.removeRow(index.row())

    # Распределение нагрузки
    # Метка работы
    def update_prepods_dict(self):
        """Update prepods dictionary."""
        data = SQH.select_all_from_table('workTables')
        self._prepods.clear()
        DH.update_prepods_dict(data, self._prepods)

    def onComboBoxIndexChanged(self, index=None):
        """Set work table."""
        if self._rtblModels:
            model_name = self.mainTeacherComboBox.currentText()
            rtbl_keys = list(self._rtblModels.keys())
            if model_name in rtbl_keys:
                self.rightTableView.setModel(self._rtblModels[model_name])
        else:
            print("nothing happens here")

    def addIds(self, data):
        """Adding ids."""
        """
        Функция для добавления айди к строкам
        """
        for i in range(len(data)):
            data[i] = [i] + data[i]

    def updatePrepodsComboBox(self):
        """Update prepods combo model."""
        self.mainTeacherComboBox.clear()
        model = MyListModel(list(self._prepods.keys()))
        self.mainTeacherComboBox.setModel(model)

    def makeColumnsHidden(self, tableView):
        """Make some columns hidden."""
        tableView.setColumnHidden(0, True)
        tableView.setColumnHidden(1, True)
        tableView.setColumnHidden(2, True)
        # tableView.setColumnHidden(8, True)

    def setRightModels(self, header):
        """Without this didn't work."""
        for k in self._prepods.keys():
            data = [
                [k] * 25,
                [k] * 25,
                [k] * 25
            ]
            self._rtblModels[k] = MyModel(data, header)
            self._rtblModels[k].removeRows(0, 1)
            self._rtblModels[k].removeRows(0, 1)
            self._rtblModels[k].removeRows(0, 1)

    def update_right_models(self, header):
        """Update work table models."""
        rtbl_keys = list(self._rtblModels.keys())
        for k in self._prepods.keys():
            data = [
                [k] * 25,
                [k] * 25,
                [k] * 25
            ]
            if k not in rtbl_keys:
                self._rtblModels[k] = MyModel(data, header)
                self._rtblModels[k].removeRows(0, 1)
                self._rtblModels[k].removeRows(0, 1)
                self._rtblModels[k].removeRows(0, 1)

    def loadData(self):
        """
        Load data.

        Функция для загрузки данных из эксель файла
        """
        if not self.mainTeacherComboBox.count():
            QMessageBox.warning(
                self, 'Ошибка', 'В программе отсутствуют рабочие таблицы')
            return
        fname, _ = QFileDialog.getOpenFileName(
            self, "Choose file", "", "Excel Files (*.xlsx *.xls *.xlsm)")
        if not fname:
            return
        new_excel = [
            '.xlsx',
            '.xlsm'
        ]
        old_excel = ['.xls']
        file_extension = os.path.splitext(fname)[-1].lower()
        try:
            if file_extension in new_excel:
                excel = ExcelHandler(fname)
                excel.open_workbook()
                excel.get_sheet_by_name('нагрузка кафедры')
                self._header, self._data = excel.read_rows_to_list()
            if file_extension in old_excel:
                excel = XlsHandler(fname)
                excel.open_workbook()
                excel.get_nagruzka_sheet()
                self._header, self._data = excel.read_rows_to_list()
        except KeyError:
            QMessageBox.warning(
                self,
                'Ошибка',
                'Что-то пошло не так.\
                  \nВозможно загружаемый файл не соответствует шаблону.')
            return
        self.addIds(self._data)
        self.model1 = MyModel(self._data, self._header)
        self.leftTableView.setModel(self.model1)
        # self.rightTableView.setModel(self.models[self.comboBox.currentText()])
        self.leftTableView.resizeColumnsToContents()
        self.model1.updateIds()
        self.makeColumnsHidden(self.leftTableView)
        self.setRightModels(self._header)
        modelname = self.mainTeacherComboBox.currentText()
        self.rightTableView.setModel(self._rtblModels[modelname])
        self.makeColumnsHidden(self.rightTableView)
        self.rightTableView.resizeColumnsToContents()
        self._data_loaded = True

    def check_lower_limit(self):
        """Check for lower limit."""
        model_name = self.mainTeacherComboBox.currentText()
        table_sum = sum(self._rtblModels[model_name].getAllColSum())
        table_limit = self._prepods[model_name].getTotalTime()
        difference = table_limit - table_sum
        return difference

    def check_lower_limit_message(self):
        """Check for hours limit."""
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Question)
        message_box.setText(
            "Часы работы в таблице меньше, чем нагрузка преподавателя")
        message_box.setWindowTitle("Хотите продолжить?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)
        result = message_box.exec()
        if result == QMessageBox.Yes:
            return True
        return False

    def uploadData(self):
        """Upload data."""
        if not self._data_loaded:
            QMessageBox.warning(
                self, 'Ошибка', 'Отсутствуют данные для выгрузки')
            return
        difference = self.check_lower_limit()
        if difference != 0:
            if not self.check_lower_limit_message():
                return
        modelname = self.mainTeacherComboBox.currentText()
        data = self._rtblModels[modelname].get_data()
        workdata = DH.makeNumberable(data.copy())
        osen, vesna = DH.divideOsenVesna(workdata)
        # fname, _ = QFileDialog.getOpenFileName(
        #     self, "Choose  save file", "*", "*.xlsx")
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options)
        if not fname:
            return
        excel = ExcelHandler()
        tchr_id = self.get_prepod_id()
        excel.writeRows(osen, vesna, fname, tchr_id)

    def get_prepod_id(self):
        """Get prepod id."""
        key = self.mainTeacherComboBox.currentText()
        return self._prepods[key].get_tbl_id()

    def save_obsh_nagruzka(self):
        """Save obs nagruzka."""
        # Сохраняем общую нагрузку
        if not self._data_loaded:
            QMessageBox.warning(
                self, 'Ошибка', 'Общая нагрузка не загружена')
            return
        data = self.model1.get_data()
        workdata = DH.makeNumberable(data.copy())
        workdata = DH.make_obsh_nagruzka_for_save(workdata)
        # fname, _ = QFileDialog.getOpenFileName(
        #     self, "Choose  save file", "*", "*.xlsx")
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options)
        if not fname:
            return
        excel = ExcelHandler()
        excel.write_nagruzka(workdata, fname)


def toggle_stylesheet(path):
    """Toggle stylesheet."""
    """
    Toggle the stylesheet to use the desired path in the Qt resource
    system (prefixed by `:/`) or generically (a path to a file on
    system).
    """
    app = QApplication.instance()
    if app is None:
        raise RuntimeError('Qt application not found')
    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.actionDark.triggered.connect(
        lambda: toggle_stylesheet(":/dark/stylesheet.qss"))
    mainwindow.actionLight.triggered.connect(
        lambda: toggle_stylesheet(":/light/stylesheet.qss"))
    mainwindow.actionDefault.triggered.connect(
        lambda: app.setStyleSheet(""))
    mainwindow.show()
    app.exec_()

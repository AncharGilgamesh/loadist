"""Распределитель учебной нагрузки.

Sorry for that
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,\
      QMessageBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.uic import loadUi
from Models.ExcelHandler import ExcelHandler, XlsHandler
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
import sqlite3
import Resources.breeze_resources
import Resources.res_images  # noqa: F401  регистрация иконок Qt
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
        self._prepod_labels = {}
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
        migration_error = SQH.create_tables()
        if migration_error:
            QMessageBox.warning(self, "Ошибка", migration_error)
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
        # self.testButton.clicked.connect(self.testing_func)
        self.transferButton.clicked.connect(self.row_inserting)
        self.transferBackButton.clicked.connect(self.row_outserting)
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
        self.saveAllPrepodNagrAction.triggered.connect(self.upload_all_teachers)
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
                for col in range(9):
                    current_row.append(str(self.model1.index(row, col).data()))
                discipline = self.model1.index(row, 6).data()
                if discipline and 'Руководство аспирантом' in discipline:
                    names = DH.extract_names(discipline)
                    dialog = NameSelectionDialog(names)
                    if dialog.exec_() != QDialog.Accepted:
                        return
                    selected_item = dialog.get_selected_item()
                    current_row[6] = (
                        'Руководство аспирантом (' + selected_item + ')')
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
        self.replace_rows(row_data, edited)
        self.model1.clear_edited_dict()
        # self.compare_selection_and_edit(
        #     self.model1, edited_cells, selected_indexes)

        # end of check
        self.leftTableView.reset()
        # Список для передачи в соседнюю таблицу
        rows_to_insert = [x for x in row_data.values()]
        # rowcount = len(rows_to_insert)
        tbl_id = self.current_work_table_id()
        modelIds = self._rtblModels[tbl_id].getIds()
        startRow = self.model1._startEditRow
        for row in rows_to_insert:
            if row[0] in modelIds:
                self._rtblModels[tbl_id].addToRow(
                    modelIds[row[0]], row, startRow)
            else:
                self._rtblModels[tbl_id].appendRow(row)
                self._rtblModels[tbl_id].addId(row[0])
        # Обновляем модели после передачи информации
        self.model1.clearChangesDict()
        self.model1.clearBasicDict()

    def testing_func(self):
        """func."""
        data = SQH.select_settings()[0][-4:]
        print(data)
        # Все это осталось сделать универсальным и закинуть в общую систему

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
        tbl_id = self.current_work_table_id()
        transfer_sum = DH.sum_lists(row_data)
        table_sum = sum(self._rtblModels[tbl_id].getAllColSum())
        table_limit = self._prepods[tbl_id].getTotalTime()
        difference = table_limit - transfer_sum - table_sum
        return difference

    def get_back_basic(self):
        """func."""
        basic_data = self.model1.get_basic_rows()
        for k, v in basic_data.items():
            self.model1.removeRows(int(k), 1)
            self.model1.insertRow(int(k), v)
        self.model1.updateIds()

    def replace_rows(self, rep_data, edited):
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
            asp = DH.aspirant_name_from_cell(rep_data[i][6])
            if i in list_of_keys and i not in edited_keys:
                self.model1.divide_changed_row(i, data_dict[i], asp)
            elif i in list_of_keys and i in edited_keys:
                self.model1.special_divide_row(
                    i, rep_data[i], data_dict[i], asp)
            else:
                self.model1.divide_row(i, rep_data[i])

    def replace_rows_outserting(self, rep_data, edited):
        """func."""
        model = self._rtblModels[self.current_work_table_id()]
        data_dict = model.get_diff()
        list_of_keys = data_dict.keys()
        edited_keys = edited.keys()
        for i in rep_data.keys():
            asp = DH.aspirant_name_from_cell(rep_data[i][6])
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
        model = self._rtblModels[self.current_work_table_id()]
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
                for col in range(9):
                    current_row.append(str(model.index(row, col).data()))
                discipline = model.index(row, 6).data()
                if discipline and 'Руководство аспирантом' in discipline:
                    names = DH.extract_names(discipline)
                    dialog = NameSelectionDialog(names)
                    if dialog.exec_() != QDialog.Accepted:
                        return
                    selected_item = dialog.get_selected_item()
                    current_row[6] = (
                        'Руководство аспирантом (' + selected_item + ')')
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
        self.replace_rows_outserting(row_data, edited)
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
            DH.set_prepods_stats(
                self._rtblModels, self._stat_model, self._prepod_labels)
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
        index_list = []
        for model_index in selected_indexes:
            index_list.append(QPersistentModelIndex(model_index))
        index_list.sort(key=lambda index: index.row(), reverse=True)
        for index in index_list:
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
        self.check_for_del_ids()
        try:
            SQH.replace_teachers_and_work_tables(
                self._teacher_tbl_model.get_data(),
                self._work_tbl_model.get_data(),
            )
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить преподавателей. "
                "Проверьте, что их номера не повторяются "
                "и что рабочие таблицы ссылаются на них.",
            )
            self.update_teacher_table()
            self.update_teacher_names()
            self.update_work_table()
            self.update_prepods_dict()
            if self._data_loaded:
                self.update_right_models(self._header)
            self.updatePrepodsComboBox()
            return
        self.update_teacher_names()
        self.update_prepods_dict()
        if self._data_loaded:
            self.update_right_models(self._header)
        self.updatePrepodsComboBox()

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
        try:
            SQH.insert_into_work_table(data)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить рабочие таблицы. "
                "Проверьте номера таблиц и наличие преподавателя.",
            )
            return False
        self.update_prepods_dict()
        if self._data_loaded:
            self.update_right_models(self._header)
        self.updatePrepodsComboBox()
        return True

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
        prepod_ids = {
            str(teacher_id)
            for teacher_id in self._teacher_tbl_model.get_col_by_name('id')
        }
        teacher_col = self._work_tbl_model.get_header().index('№ пр.')
        rows_to_remove = []
        for row_index, row in enumerate(self._work_tbl_model.get_data()):
            if str(row[teacher_col]) not in prepod_ids:
                rows_to_remove.append(row_index)
        for row_index in reversed(rows_to_remove):
            self._work_tbl_model.removeRow(row_index)

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
            QMessageBox.warning(self, 'Ошибка', 'Такое направление уже есть')
            return
        list_to_insert = [code, name]
        self.nap_pod_model.insertRow(0, list_to_insert)

    # Группы
    def open_add_group(self):
        """Open groups dialog window."""
        self.addGroup = GroupAdd()
        self.addGroup.set_codes(self.nap_code_model)
        self.addGroup.set_curators(self._teacher_names_model)
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
        self.update_groups_without_aspirants()

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
        self._prepod_labels = DH.work_table_labels(data)

    def current_work_table_id(self):
        """Id рабочей таблицы, выбранной в комбобоксе."""
        combo = self.mainTeacherComboBox
        index = combo.currentIndex()
        model = combo.model()
        if index < 0 or not hasattr(model, "get_id"):
            return None
        ids = getattr(model, "_ids", None)
        if not ids or index >= len(ids):
            return None
        return model.get_id(index)

    def onComboBoxIndexChanged(self, index=None):
        """Set work table."""
        if self._rtblModels:
            tbl_id = self.current_work_table_id()
            if tbl_id in self._rtblModels:
                self.rightTableView.setModel(self._rtblModels[tbl_id])
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
        ids = list(self._prepods.keys())
        labels = [self._prepod_labels[tbl_id] for tbl_id in ids]
        model = MyListModel(labels, ids)
        self.mainTeacherComboBox.setModel(model)

    def makeColumnsHidden(self, tableView):
        """Make some columns hidden."""
        tableView.setColumnHidden(0, True)
        tableView.setColumnHidden(1, True)
        tableView.setColumnHidden(2, True)
        # tableView.setColumnHidden(8, True)

    def _empty_right_model(self, key, header):
        """Пустая правая таблица преподавателя."""
        data = [
            [key] * 25,
            [key] * 25,
            [key] * 25
        ]
        model = MyModel(data, header)
        model.removeRows(0, 1)
        model.removeRows(0, 1)
        model.removeRows(0, 1)
        return model

    def setRightModels(self, header):
        """Without this didn't work."""
        self._rtblModels = {}
        for tbl_id in self._prepods:
            self._rtblModels[tbl_id] = self._empty_right_model(tbl_id, header)

    def update_right_models(self, header):
        """Update work table models."""
        for tbl_id in list(self._rtblModels):
            if tbl_id not in self._prepods:
                del self._rtblModels[tbl_id]
        for tbl_id in self._prepods:
            if tbl_id not in self._rtblModels:
                self._rtblModels[tbl_id] = self._empty_right_model(
                    tbl_id, header)

    def loadData(self):
        """
        Load data.

        Функция для загрузки данных из эксель файла
        """
        if not self.mainTeacherComboBox.count():
            QMessageBox.warning(
                self, 'Ошибка', 'В программе отсутствуют рабочие таблицы')
            return
        if self._data_loaded:
            answer = QMessageBox.question(
                self,
                "Повторная загрузка",
                "Заменить текущее распределение?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
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
        load_error = (
            "Не удалось загрузить файл. Проверьте, что это книга Excel "
            "по шаблону и что в настройках есть строка границ чтения."
        )
        try:
            if file_extension in new_excel:
                excel = ExcelHandler(fname)
                excel.open_workbook()
                excel.get_sheet_by_name('нагрузка кафедры')
                self._header, self._data = excel.read_rows_to_list()
            elif file_extension in old_excel:
                excel = XlsHandler(fname)
                excel.open_workbook()
                if excel.get_nagruzka_sheet() is None:
                    raise KeyError("sheet")
                self._header, self._data = excel.read_rows_to_list()
            else:
                raise ValueError("extension")
        except Exception:
            QMessageBox.warning(self, "Ошибка", load_error)
            return
        self.addIds(self._data)
        self.model1 = MyModel(self._data, self._header)
        self.leftTableView.setModel(self.model1)
        # self.rightTableView.setModel(self.models[self.comboBox.currentText()])
        self.leftTableView.resizeColumnsToContents()
        self.model1.updateIds()
        self.makeColumnsHidden(self.leftTableView)
        self.setRightModels(self._header)
        tbl_id = self.current_work_table_id()
        self.rightTableView.setModel(self._rtblModels[tbl_id])
        self.makeColumnsHidden(self.rightTableView)
        self.rightTableView.resizeColumnsToContents()
        self._data_loaded = True

    def check_lower_limit(self):
        """Check for lower limit."""
        tbl_id = self.current_work_table_id()
        table_sum = sum(self._rtblModels[tbl_id].getAllColSum())
        table_limit = self._prepods[tbl_id].getTotalTime()
        difference = table_limit - table_sum
        return difference

    def _hours_text(self, value):
        """func."""
        number = float(value)
        if number.is_integer():
            return str(int(number))
        return str(number)

    def _workbook_name(self, tbl_id):
        """func."""
        label = self._prepod_labels.get(tbl_id, str(tbl_id))
        cleaned = "".join(
            ch for ch in label if ch not in '\\/:*?"<>|'
        ).strip(" .")
        if not cleaned:
            cleaned = str(tbl_id)
        return cleaned + ".xlsx"

    def check_lower_limit_message(self):
        """Check for hours limit."""
        difference = self.check_lower_limit()
        if difference == 0:
            return True
        label = self._prepod_labels.get(self.current_work_table_id(), "")
        if difference > 0:
            text = (
                f"У преподавателя {label} недобор: часов меньше лимита на "
                f"{self._hours_text(difference)}."
            )
        else:
            text = (
                f"У преподавателя {label} превышение: часов больше лимита на "
                f"{self._hours_text(abs(difference))}."
            )
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Question)
        message_box.setText(text)
        message_box.setWindowTitle("Хотите продолжить?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)
        result = message_box.exec()
        if result == QMessageBox.Yes:
            return True
        return False

    def export_teacher_workbook(self, tbl_id, path):
        """Сохраняет план одного преподавателя. Возвращает текст ошибки."""
        data = self._rtblModels[tbl_id].get_data()
        workdata = DH.makeNumberable(data.copy())
        osen, vesna, error = DH.divideOsenVesna(workdata)
        if error:
            return error
        excel = ExcelHandler()
        try:
            excel.writeRows(
                osen, vesna, path, self._prepods[tbl_id].get_tbl_id())
        except ValueError as exc:
            return str(exc)
        return None

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
        tbl_id = self.current_work_table_id()
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options)
        if not fname:
            return
        error = self.export_teacher_workbook(tbl_id, fname)
        if error:
            QMessageBox.warning(self, "Ошибка", error)

    def upload_all_teachers(self):
        """Выгружает план каждого преподавателя в выбранную папку."""
        if not self._data_loaded:
            QMessageBox.warning(
                self, "Ошибка", "Отсутствуют данные для выгрузки")
            return
        if not self._prepods:
            QMessageBox.warning(
                self, "Ошибка", "В программе отсутствуют рабочие таблицы")
            return
        mismatches = []
        for tbl_id, teacher in self._prepods.items():
            table_sum = sum(self._rtblModels[tbl_id].getAllColSum())
            try:
                same = float(table_sum) == float(teacher.getTotalTime())
            except (TypeError, ValueError):
                same = False
            if not same:
                mismatches.append(
                    self._prepod_labels.get(tbl_id, str(tbl_id)))
        if mismatches:
            answer = QMessageBox.question(
                self,
                "Хотите продолжить?",
                "Сумма часов не равна лимиту:\n"
                + "\n".join(mismatches)
                + "\n\nПродолжить?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if not directory:
            return
        for tbl_id in self._prepods:
            path = os.path.join(directory, self._workbook_name(tbl_id))
            error = self.export_teacher_workbook(tbl_id, path)
            if error:
                label = self._prepod_labels.get(tbl_id, str(tbl_id))
                QMessageBox.warning(self, "Ошибка", f"{label}: {error}")
                return

    def get_prepod_id(self):
        """Get prepod id."""
        return self._prepods[self.current_work_table_id()].get_tbl_id()

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

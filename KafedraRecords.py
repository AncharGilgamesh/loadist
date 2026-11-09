"""Запись справочников кафедры в базу."""

import sqlite3

from PyQt5.QtCore import QPersistentModelIndex, Qt
from PyQt5.QtWidgets import QMessageBox

import Models.DataHandler as DH
import Models.SqlHandler as SQH
from Models.Models import KafedraModels, MyListModel
from UICode.DiscipAdd import DisciplineAdd
from UICode.DoljnostiAdd import DoljnostAdd
from UICode.GroupAdd import GroupAdd
from UICode.NapPodAdd import NapPodAdd
from UICode.PrepodAddNew import PrepodAdd
from UICode.WorkTableAdd import CreateWorkTable


class KafedraRecords:
    """Экраны справочников кафедры и их сохранение."""

    def remove_all_rows_in_table_view(self, model):
        """func."""
        answer = QMessageBox.question(
            self,
            "Удалить все",
            "Удалить все строки?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        data_len = model.rowCount()
        model.removeRows(0, data_len)

    def del_current_row_in_table_view(self, tableView, model):
        """func."""
        """Удаляет выбранные строки для selectionBehaviour - Select Items"""
        index_list = []
        for model_index in tableView.selectedIndexes():
            index = QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            model.removeRow(index.row())

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
                self, "Выберите строку", "Выберите строку, которую хотите редактировать"
            )
            return False
        model = tableView.model()
        for col in range(model.columnCount()):
            data = model.data(model.index(selected_rows[0].row(), col), Qt.DisplayRole)
            row.append(data)
        return True

    def open_add_doljnosti(self):
        """func."""
        self.addDoljnosti = DoljnostAdd()
        self.addDoljnosti.submitted.connect(self.add_doljnosti)
        self.addDoljnosti.show()

    def save_doljnost(self):
        """Сохраняет должности и возвращает прежние строки при повторе."""
        data_to_save = self._doljnosti_model.get_data()
        try:
            SQH.insert_into_doljnost_table(data_to_save)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить должности. "
                "Проверьте, что названия не повторяются.",
            )
            self.update_kafedra_doljnosti()
            return
        self.update_dljnst_combo_model()

    def add_doljnosti(self, dljnst, stvka):
        """func."""
        list_to_add = [dljnst, stvka]
        self._doljnosti_model.insertRow(0, list_to_add)

    def update_kafedra_doljnosti(self):
        """func."""
        doljnosti_data = SQH.select_all_from_table("doljnosti")
        doljnosti_header = ["Должность", "Ставка(час)"]
        self._doljnosti_model = KafedraModels(doljnosti_data, doljnosti_header)
        self.doljnostiTableView.setModel(self._doljnosti_model)

    def update_dljnst_combo_model(self):
        """func."""
        dljnsti = self._doljnosti_model.get_col_by_name("Должность")
        self._dljnst_combo_model = MyListModel(dljnsti)

    def open_add_teacher(self):
        """func."""
        if not self._dljnst_combo_model.rowCount():
            QMessageBox.warning(
                self, "Ошибка", "Для продолжения работы добавьте должности"
            )
            return
        self.addTeacher = PrepodAdd()
        self.teacher_components(
            self.addTeacher,
            self._dljnst_combo_model,
            self._groups_model,
            self.add_teacher,
        )
        self.addTeacher.show()

    def teacher_components(self, dialog, dljnst, groups, reciever):
        """func."""
        dialog.set_dljnsti(dljnst)
        dialog.data_signal.connect(reciever)
        dialog.set_groups(groups)

    def update_teacher_table(self):
        """func."""
        teacher_data = SQH.select_all_from_table("teachers")
        teacher_header = [
            "id",
            "ФИО",
            "Ученое звание",
            "Ученая степень",
            "Должность",
            "Ограничение по дипломникам",
            "Курирует группу",
        ]
        self._teacher_tbl_model = KafedraModels(teacher_data, teacher_header)
        self.prepodsTableView.setModel(self._teacher_tbl_model)

    def add_teacher(self, data):
        """Добавляет преподавателя с новым номером."""
        DH.kafedra_id_add(self._teacher_tbl_model, "id", data)

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
        data = self._teacher_tbl_model.get_col_by_name("ФИО")
        teacher_ids = self._teacher_tbl_model.get_col_by_name("id")
        self._teacher_names_model = MyListModel(data, teacher_ids)

    def open_edit_teacher(self):
        """func."""
        row = []
        if not self.get_selected_row_kafedra(self.prepodsTableView, row):
            return
        editTeacher = PrepodAdd()
        editTeacher.setWindowTitle("Редактировать преподавателя")
        editTeacher.set_edit_lines(row[1:])
        self.teacher_components(
            editTeacher,
            self._dljnst_combo_model,
            self._groups_model,
            lambda data: self.edit_teacher(data, row[0]),
        )
        editTeacher.show()

    def edit_teacher(self, data, id):
        """Сохраняет преподавателя и фамилию в его рабочих таблицах."""
        new_data = [id] + data
        try:
            SQH.update_teachers(new_data)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить преподавателя. "
                "Проверьте номер и связанные рабочие таблицы.",
            )
        self.update_teacher_table()
        self.update_teacher_names()
        self.update_work_table()
        self.update_prepods_dict()
        self.updatePrepodsComboBox()

    def open_work_create(self):
        """func."""
        if not self._teacher_names_model.rowCount():
            QMessageBox.warning(
                self, "Ошибка", "Для продолжения работы добавьте преподавателей"
            )
            return
        self.addWorkTable = CreateWorkTable()
        self.addWorkTable.set_teachers(self._teacher_names_model)
        self.addWorkTable.data_signal.connect(self.add_work_table)
        self.addWorkTable.show()

    def update_work_table(self):
        """func."""
        work_tbl_data = SQH.select_all_from_table("workTables")
        work_tbl_headers = [
            "id",
            "ФИО",
            "№ пр.",
            "Тип",
            "Осн. ставка",
            "Почас.",
            "Почас. доп.",
            "Совместительство",
            "Итог",
        ]
        self._work_tbl_model = KafedraModels(work_tbl_data, work_tbl_headers)
        self.workTableView.setModel(self._work_tbl_model)

    def add_work_table(self, data):
        """Добавляет рабочую таблицу с новым номером."""
        DH.kafedra_id_add(self._work_tbl_model, "id", data)

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
            lambda data: self.edit_work_table(data, row[0])
        )
        edit_work_table_window.exec_()

    def edit_work_table(self, data, id):
        """Сохраняет рабочую таблицу и читает её из базы при ошибке."""
        new_data = [id] + data
        try:
            SQH.update_work_table(new_data)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить рабочую таблицу. "
                "Проверьте номер таблицы и наличие преподавателя.",
            )
        self.update_work_table()

    def check_for_del_ids(self):
        """func."""
        prepod_ids = {
            str(teacher_id)
            for teacher_id in self._teacher_tbl_model.get_col_by_name("id")
        }
        teacher_col = self._work_tbl_model.get_header().index("№ пр.")
        rows_to_remove = []
        for row_index, row in enumerate(self._work_tbl_model.get_data()):
            if str(row[teacher_col]) not in prepod_ids:
                rows_to_remove.append(row_index)
        for row_index in reversed(rows_to_remove):
            self._work_tbl_model.removeRow(row_index)

    def open_add_discipline(self):
        """func."""
        self.addDiscipline = DisciplineAdd()
        self.addDiscipline.set_codes(self.nap_code_model)
        self.addDiscipline.data_signal.connect(self.add_discipline)
        self.addDiscipline.show()

    def add_discipline(self, code, name):
        """func."""
        list_to_insert = [code, name]
        DH.kafedra_id_add(self._discipline_model, "id", list_to_insert)

    def save_discipline(self):
        """Сохраняет дисциплины и возвращает прежние строки при повторе."""
        data = self._discipline_model.get_data()
        try:
            SQH.insert_into_disciplines_table(data)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить дисциплины. "
                "Проверьте, что номера не повторяются.",
            )
            self.update_discipline()

    def update_discipline(self):
        """func."""
        discipline_data = SQH.select_all_from_table("disciplines")
        discip_headers = ["id", "Направление", "Дисциплина"]
        self._discipline_model = KafedraModels(discipline_data, discip_headers)
        self.disciplineTableView.setModel(self._discipline_model)
        self.disciplineTableView.setColumnHidden(0, True)

    def open_add_napravlenia(self):
        """func."""
        self.addNapPod = NapPodAdd()
        self.addNapPod.data_signal.connect(self.add_nap_pod)
        self.addNapPod.exec_()

    def update_nap_pod(self):
        """func."""
        nap_pod_data = SQH.select_all_from_table("napPod")
        nap_pod_headers = ["Код", "Наименование"]
        self.nap_pod_model = KafedraModels(nap_pod_data, nap_pod_headers)
        self.napPodTableView.setModel(self.nap_pod_model)

    def update_nap_code(self):
        """func."""
        nap_codes = self.nap_pod_model.get_col_by_name("Код")
        self.nap_code_model = MyListModel(nap_codes)

    def save_nap_pod(self):
        """Сохраняет направления и возвращает прежние строки при повторе."""
        data_to_save = self.nap_pod_model.get_data()
        try:
            SQH.insert_into_napPod_table(data_to_save)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить направления. "
                "Проверьте, что коды не повторяются.",
            )
            self.update_nap_pod()
            return
        self.update_nap_code()

    def add_nap_pod(self, code, name):
        """func."""
        data_comparison = self.nap_pod_model.get_col_by_name("Код")
        if DH.data_comparsion(data_comparison, code):
            QMessageBox.warning(self, "Ошибка", "Такое направление уже есть")
            return
        list_to_insert = [code, name]
        self.nap_pod_model.insertRow(0, list_to_insert)

    def open_add_group(self):
        """Open groups dialog window."""
        self.addGroup = GroupAdd()
        self.addGroup.set_codes(self.nap_code_model)
        self.addGroup.set_curators(self._teacher_names_model)
        self.addGroup.data_signal.connect(self.add_group)
        self.addGroup.exec_()

    def add_group(self, grNum, amount, curator, code):
        """Add group."""
        data_comprasion = self.kafedraModel.get_col_by_name("Группа")
        data_comprasion = DH.divide_aspirants(data_comprasion)
        if DH.data_comparsion(data_comprasion, grNum):
            QMessageBox.warning(self, "Ошибка", "Группа уже есть в таблице")
            return
        list_to_insert = [grNum, int(amount), curator, code]
        DH.kafedra_id_add(self.kafedraModel, "id", list_to_insert)
        self.update_groups_without_aspirants()

    def updateKafedraGroups(self):
        """Update groups."""
        kafedraData = SQH.select_all_from_table("kafedraGroups")
        kafedraHeaders = ["id", "Группа", "Кол-во людей", "Куратор", "Направление"]
        self.kafedraModel = KafedraModels(kafedraData, kafedraHeaders)
        self.groupsTableView.setModel(self.kafedraModel)
        self.groupsTableView.setColumnHidden(0, True)

    def update_groups_without_aspirants(self):
        """Update groups model that put in prepods dialog window."""
        data = self.kafedraModel.get_col_by_name("Группа")
        data = DH.divide_aspirants(data)
        self._groups_model = MyListModel(data)

    def save_groups(self):
        """Сохраняет группы и возвращает прежние строки при повторе."""
        data_to_save = self.kafedraModel.get_data()
        try:
            SQH.insert_into_groups_table(data_to_save)
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось сохранить группы. "
                "Проверьте, что номера не повторяются.",
            )
            self.updateKafedraGroups()
            return
        self.update_groups_without_aspirants()

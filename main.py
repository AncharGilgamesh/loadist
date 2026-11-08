"""Окно программы связывает сигналы кнопок со страницами нагрузки и кафедры."""

import os
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

import Models.DataHandler as DH
import Models.SqlHandler as SQH
import Resources.breeze_resources
import Resources.res_images  # noqa: F401  регистрация иконок Qt
from HourTransfer import HourTransfer
from KafedraRecords import KafedraRecords
from Models.ExcelHandler import ExcelHandler, XlsHandler
from Models.Models import KafedraModels, MyListModel, MyModel
from UICode.SettingsDialog import SettingsDialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, "UI", "mainView.ui")


class MainWindow(HourTransfer, KafedraRecords, QMainWindow):
    """Окно со страницами распределения и кафедры."""

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
        self.transferButton.clicked.connect(self.row_inserting)
        self.transferBackButton.clicked.connect(self.row_outserting)
        self.loadButton.clicked.connect(self.loadData)
        self.uploadButton.clicked.connect(self.uploadData)
        self.saveMainNagruzka.clicked.connect(self.save_obsh_nagruzka)
        self.mainTeacherComboBox.currentIndexChanged.connect(
            self.onComboBoxIndexChanged
        )
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
            lambda: self.remove_all_rows_in_table_view(self._work_tbl_model)
        )
        # Groups
        self.addGroupButton.clicked.connect(self.open_add_group)
        self.delCurrentGrButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
                self.groupsTableView, self.kafedraModel
            )
        )
        self.saveGroups.clicked.connect(self.save_groups)
        self.dellAllGrButton.clicked.connect(
            lambda: self.remove_all_rows_in_table_view(self.kafedraModel)
        )
        # Направления подготовки
        self.addNapPodButton.clicked.connect(self.open_add_napravlenia)
        self.saveNapPodButton.clicked.connect(self.save_nap_pod)
        self.delCurrNapButton.clicked.connect(
            lambda: self.del_current_row_in_table_view(
                self.napPodTableView, self.nap_pod_model
            )
        )
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
                self.stackedWidget.currentIndex() + 1
            )
        )
        self.goToMainButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(
                self.stackedWidget.currentIndex() - 1
            )
        )
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/Images/logo.png")))
        self.setWindowTitle("Распределитель учебной нагрузки")

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
                self._rtblModels, self._stat_model, self._prepod_labels
            )
        self.statisticTableView.resizeColumnsToContents()

    def save_statistics(self):
        """func."""
        data = self._stat_model.get_data()
        header = self._stat_model.get_header()
        data.insert(0, header)
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options
        )
        if not fname:
            return
        excel = ExcelHandler()
        excel.write_statistics(data, fname)

    # Распределение нагрузки
    # Метка работы
    def update_prepods_dict(self):
        """Update prepods dictionary."""
        data = SQH.select_all_from_table("workTables")
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
        data = [[key] * 25, [key] * 25, [key] * 25]
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
                self._rtblModels[tbl_id] = self._empty_right_model(tbl_id, header)

    def loadData(self):
        """
        Load data.

        Функция для загрузки данных из эксель файла
        """
        if not self.mainTeacherComboBox.count():
            QMessageBox.warning(
                self, "Ошибка", "В программе отсутствуют рабочие таблицы"
            )
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
            self, "Choose file", "", "Excel Files (*.xlsx *.xls *.xlsm)"
        )
        if not fname:
            return
        new_excel = [".xlsx", ".xlsm"]
        old_excel = [".xls"]
        file_extension = os.path.splitext(fname)[-1].lower()
        load_error = (
            "Не удалось загрузить файл. Проверьте, что это книга Excel "
            "по шаблону и что в настройках есть строка границ чтения."
        )
        try:
            if file_extension in new_excel:
                excel = ExcelHandler(fname)
                excel.open_workbook()
                excel.get_sheet_by_name("нагрузка кафедры")
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
        cleaned = "".join(ch for ch in label if ch not in '\\/:*?"<>|').strip(" .")
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
            excel.writeRows(osen, vesna, path, self._prepods[tbl_id].get_tbl_id())
        except ValueError as exc:
            return str(exc)
        return None

    def uploadData(self):
        """Upload data."""
        if not self._data_loaded:
            QMessageBox.warning(self, "Ошибка", "Отсутствуют данные для выгрузки")
            return
        difference = self.check_lower_limit()
        if difference != 0:
            if not self.check_lower_limit_message():
                return
        tbl_id = self.current_work_table_id()
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options
        )
        if not fname:
            return
        error = self.export_teacher_workbook(tbl_id, fname)
        if error:
            QMessageBox.warning(self, "Ошибка", error)

    def upload_all_teachers(self):
        """Выгружает план каждого преподавателя в выбранную папку."""
        if not self._data_loaded:
            QMessageBox.warning(self, "Ошибка", "Отсутствуют данные для выгрузки")
            return
        if not self._prepods:
            QMessageBox.warning(
                self, "Ошибка", "В программе отсутствуют рабочие таблицы"
            )
            return
        mismatches = []
        for tbl_id, teacher in self._prepods.items():
            table_sum = sum(self._rtblModels[tbl_id].getAllColSum())
            try:
                same = float(table_sum) == float(teacher.getTotalTime())
            except (TypeError, ValueError):
                same = False
            if not same:
                mismatches.append(self._prepod_labels.get(tbl_id, str(tbl_id)))
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
            QMessageBox.warning(self, "Ошибка", "Общая нагрузка не загружена")
            return
        data = self.model1.get_data()
        workdata = DH.makeNumberable(data.copy())
        workdata = DH.make_obsh_nagruzka_for_save(workdata)
        # fname, _ = QFileDialog.getOpenFileName(
        #     self, "Choose  save file", "*", "*.xlsx")
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options
        )
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
        raise RuntimeError("Qt application not found")
    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.actionDark.triggered.connect(
        lambda: toggle_stylesheet(":/dark/stylesheet.qss")
    )
    mainwindow.actionLight.triggered.connect(
        lambda: toggle_stylesheet(":/light/stylesheet.qss")
    )
    mainwindow.actionDefault.triggered.connect(lambda: app.setStyleSheet(""))
    mainwindow.show()
    app.exec_()

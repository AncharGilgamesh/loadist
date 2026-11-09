"""Окно программы связывает сигналы кнопок со страницами нагрузки и кафедры."""

import os
import sys
import zipfile

import xlrd
from openpyxl.utils.exceptions import InvalidFileException
from PyQt5 import QtGui
from PyQt5.QtCore import QFile, Qt, QTextStream
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from PyQt5.uic import loadUi
from xlrd.compdoc import CompDocError

import Models.DataHandler as DH
import Models.SqlHandler as SQH
import Resources.breeze_resources
import Resources.res_images  # noqa: F401  регистрация иконок Qt
from HourTransfer import HourTransfer
from KafedraRecords import KafedraRecords
from Models.ExcelHandler import ExcelHandler, XlsHandler
from Models.Models import KafedraModels, MyListModel, MyModel
from UICode.SettingsDialog import SettingsDialog
from UICode.WrappingHeader import WrappingHeader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(BASE_DIR, "UI", "mainView.ui")
ACADEMIC_THEME = os.path.join(
    BASE_DIR, "Resources", "themes", "academic", "stylesheet.qss"
)


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
        self._show_statistics_sample()
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
        self.goToKafedraButton.clicked.connect(self._open_kafedra)
        self.goToMainButton.clicked.connect(self._open_transfer)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/icons/Images/logo.png")))
        self.setWindowTitle("Распределитель учебной нагрузки")
        self._apply_academic_chrome()

    def _apply_academic_chrome(self):
        """Отступы, подписи разделов и зебра таблиц для учебной темы."""
        root = self.centralwidget.layout()
        root.setContentsMargins(20, 14, 20, 16)
        root.setSpacing(12)
        for name in ("label", "label_2", "label_4"):
            title = self.findChild(QLabel, name)
            if title is not None:
                title.setProperty("role", "section")
        self._make_layout_responsive()
        for view in self.findChildren(QTableView):
            view.setAlternatingRowColors(True)
            view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
            view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            view.setHorizontalHeader(WrappingHeader(view))
            self._give_extra_space(view)
            view.verticalHeader().setHighlightSections(False)
            if view.objectName() in {
                "prepodsTableView",
                "workTableView",
                "statisticTableView",
                "disciplineTableView",
                "napPodTableView",
                "groupsTableView",
                "doljnostiTableView",
            }:
                view.setWordWrap(True)
                view.verticalHeader().setSectionResizeMode(
                    QHeaderView.ResizeToContents
                )
        self.disciplineTableView.setColumnHidden(0, True)
        self.groupsTableView.setColumnHidden(0, True)
        self._set_stretch(self.mainPage.layout(), self.leftTableView, 3)
        self._set_stretch(self.mainPage.layout(), self.rightTableView, 2)
        self._mark_section(self.stackedWidget.currentIndex())
        self.statusBar().showMessage("Распределение учебной нагрузки кафедры")

    def _make_layout_responsive(self):
        """Даёт страницам и вкладкам занимать всё свободное место окна."""
        self._grid_transfer_toolbar()
        self._merge_kafedra_catalogs()
        expanding = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for widget in (
            self.stackedWidget,
            self.mainPage,
            self.KafedraPage,
            self.prepodsTabWidget,
        ):
            widget.setSizePolicy(expanding)
            widget.setMinimumWidth(0)
            widget.setMaximumWidth(16777215)
        self.mainTeacherComboBox.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.prepodsTabWidget.currentChanged.connect(self._fit_visible_headers)
        self.stackedWidget.currentChanged.connect(self._fit_visible_headers)

    def _grid_transfer_toolbar(self):
        """Ставит выбор преподавателя и кнопки переноса сеткой на всю ширину."""
        page_layout = self.mainPage.layout()
        old = page_layout.itemAt(0).layout()
        if old is None:
            return
        found = {}
        while old.count():
            item = old.takeAt(0)
            widget = item.widget()
            if widget is not None:
                found[widget.objectName()] = widget
        page_layout.takeAt(0)
        block = QVBoxLayout()
        block.setContentsMargins(0, 0, 0, 0)
        block.setSpacing(8)
        title = found["label"]
        title.setAlignment(Qt.AlignCenter)
        block.addWidget(title)
        combo = found["mainTeacherComboBox"]
        combo.setMinimumWidth(420)
        combo.setMaximumWidth(560)
        combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        combo_row = QHBoxLayout()
        combo_row.addStretch(1)
        combo_row.addWidget(combo)
        combo_row.addStretch(1)
        block.addLayout(combo_row)
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addStretch(1)
        for name in (
            "transferButton",
            "transferBackButton",
            "uploadButton",
            "loadButton",
            "saveMainNagruzka",
        ):
            button = found[name]
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            buttons.addWidget(button)
        buttons.addStretch(1)
        block.addLayout(buttons)
        page_layout.insertLayout(0, block)

    def _merge_kafedra_catalogs(self):
        """Собирает справочники в один список, переключение ставит справа."""
        target = self.prepodsTabWidget
        source = self.disNapTabWidget
        while source.count():
            title = source.tabText(0)
            page = source.widget(0)
            source.removeTab(0)
            target.addTab(page, title)
        page_layout = self.KafedraPage.layout()
        for index in range(page_layout.count() - 1, -1, -1):
            item = page_layout.itemAt(index)
            if item is not None and item.widget() is source:
                page_layout.takeAt(index)
                break
        source.hide()
        target.tabBar().hide()
        nav = QWidget()
        nav.setObjectName("kafedraNav")
        nav.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(12, 0, 0, 0)
        nav_layout.setSpacing(6)
        self._kafedra_nav_buttons = []
        for index in range(target.count()):
            button = QPushButton(target.tabText(index))
            button.setObjectName("kafedraNavButton")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            button.clicked.connect(
                lambda _checked, tab=index: target.setCurrentIndex(tab)
            )
            nav_layout.addWidget(button)
            self._kafedra_nav_buttons.append(button)
        nav_layout.addStretch(1)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        target_index = 0
        for index in range(page_layout.count()):
            item = page_layout.itemAt(index)
            if item is not None and item.widget() is target:
                target_index = index
                break
        page_layout.takeAt(target_index)
        row.addWidget(target, 1)
        row.addWidget(nav, 0)
        page_layout.insertLayout(target_index, row)
        page_layout.setStretch(target_index, 1)
        target.currentChanged.connect(self._mark_kafedra_section)
        self._mark_kafedra_section(target.currentIndex())

    def _mark_kafedra_section(self, index):
        """Подсвечивает кнопку открытого справочника."""
        for button_index, button in enumerate(self._kafedra_nav_buttons):
            active = button_index == index
            button.setChecked(active)
            button.setProperty("active", active)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def _fit_visible_headers(self, *_args):
        """Подгоняет колонки видимых таблиц под текущую ширину."""
        for view in self.findChildren(QTableView):
            if not view.isVisible():
                continue
            header = view.horizontalHeader()
            header.resizeSections()
            header._schedule_fit()
            if view.wordWrap():
                view.resizeRowsToContents()

    def showEvent(self, event):
        """Подгоняет колонки, когда окно уже получило размер."""
        super().showEvent(event)
        self._fit_visible_headers()

    def _give_extra_space(self, widget):
        """Отдаёт виджету лишнюю высоту и ширину родительских сеток."""
        current = widget
        while current is not None and current is not self:
            parent = current.parentWidget()
            layout = parent.layout() if parent is not None else None
            if layout is not None:
                self._set_stretch(layout, current, 1)
            current = parent

    def _set_stretch(self, layout, widget, stretch):
        """Задаёт долю виджета в сетке родителя."""
        if layout is None or not hasattr(layout, "setStretch"):
            return
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item is not None and item.widget() is widget:
                layout.setStretch(index, stretch)
                return

    def _open_kafedra(self):
        """Открывает страницу справочников кафедры."""
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + 1)
        self._mark_section(self.stackedWidget.currentIndex())

    def _open_transfer(self):
        """Открывает страницу распределения часов."""
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() - 1)
        self._mark_section(self.stackedWidget.currentIndex())

    def _mark_section(self, index):
        """Подсвечивает кнопку открытой страницы."""
        self.goToMainButton.setProperty("active", index == 0)
        self.goToKafedraButton.setProperty("active", index == 1)
        for button in (self.goToMainButton, self.goToKafedraButton):
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    # Настройки
    def open_settings(self):
        """func."""
        settings = SettingsDialog()
        settings.exec_()

    # Статистика
    def _show_statistics_sample(self):
        """Ставит заголовки статистики без часов."""
        header, data = DH.get_settings_to_stats_table()
        self._stat_model = KafedraModels(data, header)
        self.statisticTableView.setModel(self._stat_model)

    def set_statistics(self):
        """Считает статистику по загруженной общей нагрузке."""
        if not self._data_loaded:
            QMessageBox.warning(self, "Ошибка", "Считать нечего")
            return
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
        """Сохраняет статистику, если она уже посчитана."""
        if not self._data_loaded:
            QMessageBox.warning(self, "Ошибка", "Считать нечего")
            return
        rows = self._stat_model.get_data()
        if not rows:
            QMessageBox.warning(self, "Ошибка", "Сначала нажмите «Обновить»")
            return
        data = [self._stat_model.get_header(), *rows]
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
        """Загружает общую нагрузку из книги Excel."""
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
        except (
            OSError,
            ValueError,
            KeyError,
            IndexError,
            zipfile.BadZipFile,
            InvalidFileException,
            xlrd.XLRDError,
            CompDocError,
        ):
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
        failed = []
        for tbl_id in self._prepods:
            path = os.path.join(directory, self._workbook_name(tbl_id))
            try:
                error = self.export_teacher_workbook(tbl_id, path)
            except OSError as exc:
                error = str(exc)
            if error:
                label = self._prepod_labels.get(tbl_id, str(tbl_id))
                failed.append(f"{label}: {error}")
        if failed:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не записались планы:\n" + "\n".join(failed),
            )

    def get_prepod_id(self):
        """Get prepod id."""
        return self._prepods[self.current_work_table_id()].get_tbl_id()

    def save_obsh_nagruzka(self):
        """Сохраняет общую нагрузку и сообщает, если запись не удалась."""
        if not self._data_loaded:
            QMessageBox.warning(self, "Ошибка", "Общая нагрузка не загружена")
            return
        data = self.model1.get_data()
        workdata = DH.makeNumberable(data.copy())
        workdata = DH.make_obsh_nagruzka_for_save(workdata)
        options = QFileDialog.Options()
        fname, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Excel файлы (*.xlsx)", options=options
        )
        if not fname:
            return
        excel = ExcelHandler()
        try:
            excel.write_nagruzka(workdata, fname)
        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось записать общую нагрузку. "
                "Не найден шаблон или путь к файлу.",
            )
        except OSError:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось записать общую нагрузку."
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))


def apply_stylesheet(path):
    """Подключает тему: ресурс Qt (`:/`) или файл на диске."""
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("Qt application not found")
    file = QFile(path)
    if not file.open(QFile.ReadOnly | QFile.Text):
        return
    stream = QTextStream(file)
    stream.setCodec("UTF-8")
    app.setStyleSheet(stream.readAll())
    file.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QtGui.QFont("Segoe UI", 10))
    mainwindow = MainWindow()
    mainwindow.actionDark.triggered.connect(
        lambda: apply_stylesheet(":/dark/stylesheet.qss")
    )
    mainwindow.actionLight.triggered.connect(
        lambda: apply_stylesheet(":/light/stylesheet.qss")
    )
    mainwindow.actionDefault.triggered.connect(
        lambda: apply_stylesheet(ACADEMIC_THEME)
    )
    apply_stylesheet(ACADEMIC_THEME)
    mainwindow.show()
    app.exec_()

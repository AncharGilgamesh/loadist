"""Models."""

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant,\
      QAbstractListModel
import Models.DataHandler as DH


class BasicTableModel(QAbstractTableModel):
    """BasicModel."""

    def __init__(self, data=[], header=None):
        """func."""
        super(BasicTableModel, self).__init__()
        self._data = data
        self._header = header

    def rowCount(self, index=None):
        """func."""
        if self._data:
            return len(self._data)
        return 0

    def columnCount(self, index=None):
        """func."""
        if self._data:
            return len(self._data[0])
        return len(self._header)

    def headerData(self, section, orientation, role):
        """func."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self._header):
                    return self._header[section]
                else:
                    return 'Проверка'

    def get_data(self):
        """func."""
        return self._data

    def get_header(self):
        """Get header."""
        return self._header


class MyModel(BasicTableModel):
    """Model."""

    def __init__(self, data=[], header=None):
        """func."""
        super(MyModel, self).__init__(data, header)
        # self._data = data
        self._header = ['id'] + header
        # Начальная вариация строки
        self._basic_rows = {}
        # Разница между начальной вариацей строки и конечной
        self._changed_rows = {}
        self._edited_cells = {}
        """
        Для хранения id, чтобы в будущем можно было посмотреть,
        есть ли id-шник в таблице уже. Если есть, мы строки плюсуем
        если id-шников нет, мы строку просто вставим
        """
        self._ids = {}
        # Временно тут задаю номер строки, с которой можно редактировать
        self._startEditRow = 9
        self._discipline_row = 6
        self._colSum = []

    def data(self, index, role):
        """func."""
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            if value is None:
                return ''
            if value == 0 and index.column() > 0:
                return ''
            if isinstance(value, float) and value % 1 == 0:
                value = int(value)
            return value
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self._data[row][column]
        if role == Qt.TextAlignmentRole:
            return QVariant(Qt.AlignCenter)
        return QVariant()

    def flags(self, index):
        """func."""
        if not index.isValid():
            return Qt.NoItemFlags
        # row = index.row()
        column = index.column()
        if column >= self._startEditRow:
            value = self.data(index, Qt.DisplayRole)
            if value is None or value == '':
                return Qt.ItemIsEnabled
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled

    def setData(self, index, value, role):
        """func."""
        if role == Qt.EditRole:
            # print('Получаем копию изначальной строки')
            # Копия изначальной строки
            if float(value) < 0:
                return False
            if float(value) > float(self._data[index.row()][index.column()]):
                return False
            row_copy = self._data[index.row()].copy()
            # print('--------------------------------------2')
            # Если в словаре нет строки, то она добавляется
            if index.row() not in self._basic_rows.keys():
                self._basic_rows[index.row()] = row_copy.copy()
            # Вот словарь с базовыми значениями после добавления
            # print(self._basic_rows)
            # print('Получаем копию строки с измененным значением')
            # Копия строки с измененным значением
            # Заполняем инфу об измененных значениях
            if index.row() in self._edited_cells.keys():
                self._edited_cells[index.row()].add(index.column())
            else:
                self._edited_cells[index.row()] = {index.column()}

            row_copy[index.column()] = float(value)
            # print('--------------------------------------3')
            # print(row_copy)
            # print('--------------------------------------4')
            # print('тут просто выставляем в модель наше новое значение,
            #  которое было введено вручную')
            self._data[index.row()][index.column()] = float(value)
            # print('--------------------------------------6')
            # print(self._data)
            # Тут в модель посылаем сигнал, что у нас данные были изменены
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            # print('Показываем словарь с измененными значениями перед\
            #  добавлением туда нового')
            # print('--------------------------------------7')
            # print(self._changed_rows)
            # print('Добавляем в словарь с измененными значениями')
            difference = row_copy.copy()
            startRow = self._startEditRow
            for i in range(startRow, len(row_copy)):
                if self._basic_rows[index.row()][i] is None:
                    difference[i] = None
                    continue
                if self._basic_rows[index.row()][i] == '':
                    difference[i] = None
                    continue
                basic = float(self._basic_rows[index.row()][i])
                copy = float(row_copy[i])
                difference[i] = basic - copy
            self._changed_rows[index.row()] = difference
            # print('--------------------------------------8')
            # print(self._changed_rows)
            return True
        return False

    def insertRows(self, position, rows, values=None, parent=QModelIndex()):
        """func."""
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        if values is None:
            values = [
                [
                    '' for i in range(self.columnCount(None))
                    ] for j in range(rows)]
        for value in values:
            self._data.append(value)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        """Remove rows from the model."""
        self.beginRemoveRows(parent, position, position + rows - 1)
        del self._data[position:position+rows]
        self.endRemoveRows()
        return True

    def insertRow(self, row, value=None, parent=QModelIndex()):
        """func."""
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, value)
        self.endInsertRows()

    def appendRow(self, value=None, parent=QModelIndex()):
        """func."""
        row = self.rowCount()
        self.insertRow(row, value=value, parent=parent)

    def addToRow(self, row, values, startcol):
        """Add values to the given row."""
        """исправленная версия"""
        if row < self.rowCount():
            if 'Руководство аспирантом' in self._data[row][self._discipline_row]:
                aspirant = DH.extract_value_from_brackets(
                    values[self._discipline_row])
                old_ver = self._data[row][self._discipline_row]
                new_col = DH.add_value_to_brackets(aspirant, old_ver)
                self._data[row][self._discipline_row] = new_col
                self._data[row][self._discipline_row + 2] = int(
                    self._data[row][self._discipline_row + 2]) + 1
            for i in range(startcol, self.columnCount()):
                current_value = self._data[row][i]
                second_value = values[i]
                new_value = None
                if current_value and second_value:
                    current_value = float(current_value)
                    second_value = float(second_value)
                    new_value = current_value + second_value
                elif current_value:
                    new_value = current_value
                elif second_value:
                    new_value = second_value
                self._data[row][i] = new_value
                index = self.createIndex(row, i)
                self.dataChanged.emit(
                    index, index, [Qt.DisplayRole, Qt.EditRole])

    def get_back_not_selected_edited_cols(self, row, col):
        """func."""
        try:
            self._changed_rows[row][col] = None
            self._data[row][col] = self._basic_rows[row][col]
        except KeyError:
            print('Ошибка')
        index = self.createIndex(row, col)
        self.dataChanged.emit(
            index, index, [Qt.DisplayRole, Qt.EditRole])

    def get_diff(self):
        """func."""
        return self._changed_rows

    def get_edited_cells(self):
        """func."""
        return self._edited_cells

    def get_basic_rows(self):
        """func."""
        return self._basic_rows

    def clearChangesDict(self):
        """func."""
        self._changed_rows.clear()

    def clearBasicDict(self):
        """func."""
        self._basic_rows.clear()

    def clear_edited_dict(self):
        """func."""
        self._edited_cells.clear()

    def replace_rows(self, data_dict):
        """func."""
        """
        Это вроде работает, но нужно еще тщательно проверить все,
          мб что-то и не так
        """
        for row, data in data_dict.items():
            self.removeRows(row, 1)
            self.insertRow(row, data)
        # self.dataChanged.emit(
        # self.index(0, 0),
        #  self.index(self.rowCount()-1, self.columnCount()-1))

    def divide_row(self, row, data):
        """func."""
        new_data = []
        row = self._ids[data[0]]
        for i in range(self._startEditRow):
            new_data.append(self._data[row][i])
        for i in range(self._startEditRow, len(data)):
            old_val = self._data[row][i]
            new_val = data[i]
            if new_val:
                new_data.append(float(old_val) - float(new_val))
            else:
                new_data.append(old_val)
        if self.check_for_zeros(new_data):
            self.removeRows(row, 1)
            self.updateIds()
        else:
            self.removeRows(row, 1)
            self.insertRow(row, new_data)
            self.updateIds()

    def divide_changed_row(self, row, data, asp=None):
        """func."""
        new_data = []
        row = self._ids[str(data[0])]
        for i in range(self._startEditRow):
            new_data.append(self._data[row][i])
        for i in range(self._startEditRow, len(data)):
            old_val = self._data[row][i]
            new_val = data[i]
            if new_val:
                new_data.append(new_val)
            else:
                new_data.append(old_val)
        if 'Руководство аспирантом' in new_data[6]:
            new_data[6] = DH.remove_value_from_brackets(asp, new_data[6])
        if self.check_for_zeros(new_data):
            self.removeRows(row, 1)
            self.updateIds()
        else:
            self.removeRows(row, 1)
            self.insertRow(row, new_data)
            self.updateIds()

    def special_divide_row(self, row, rep_data, dict_data, asp=None):
        """func."""
        new_data = []
        row = self._ids[rep_data[0]]
        for i in range(self._startEditRow):
            new_data.append(self._data[row][i])
        for i in range(self._startEditRow, len(rep_data)):
            old_val = self._data[row][i]
            new_val = rep_data[i]
            changed_val = dict_data[i]
            if changed_val:
                new_data.append(changed_val)
            elif new_val:
                new_data.append(float(old_val) - float(new_val))
            else:
                new_data.append(old_val)
        if 'Руководство аспирантом' in new_data[6]:
            new_data[6] = DH.remove_value_from_brackets(asp, new_data[6])
        if self.check_for_zeros(new_data):
            self.removeRows(row, 1)
            self.updateIds()
        else:
            self.removeRows(row, 1)
            self.insertRow(row, new_data)
            self.updateIds()

    def replace_row(self, row, data):
        """func."""
        if self.check_for_zeros(data):
            self.removeRows(row, 1)
        else:
            self.removeRows(row, 1)
            self.insertRow(row, data)

    def check_for_zeros(self, values):
        """func."""
        """
        function for checking a row for zero values.
        This function should remove rows with zero values all in there
        star - начинаем с какого индекса
        value - значения
        """
        start = self._startEditRow
        for el in values[start:]:
            if el:
                return False
        return True

    def updateIds(self):
        """func."""
        self._ids.clear()
        for i, sub_list in enumerate(self._data):
            key = str(sub_list[0])
            value = i
            self._ids[key] = value

    def addId(self, id):
        """func."""
        self._ids[id] = len(self._ids)

    def getIds(self):
        """func."""
        return self._ids

    def delId(self, id):
        """func."""
        del self._ids[id]

    def getLectionsSum(self):
        """func."""
        column = 9
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getLab1Sum(self):
        """func."""
        column = 10
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getLab2Sum(self):
        """func."""
        column = 11
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getPrak1Sum(self):
        """func."""
        column = 12
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getPrak2Sum(self):
        """func."""
        column = 13
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getRgr1Sum(self):
        """func."""
        column = 14
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getRgr2Sum(self):
        """func."""
        column = 15
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getKpr1Sum(self):
        """func."""
        column = 16
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getKpr2Sum(self):
        """func."""
        column = 17
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getCons1Sum(self):
        """func."""
        column = 18
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getCons2Sum(self):
        """func."""
        column = 19
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getExam1Sum(self):
        """func."""
        column = 20
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getExam2Sum(self):
        """func."""
        column = 21
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getZachet1Sum(self):
        """func."""
        column = 22
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getZachet2Sum(self):
        """func."""
        column = 23
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getDopsum(self):
        """func."""
        column = 24
        sum = 0
        data = self._data.copy()
        sum = self.getColumnSum(data, column)
        print(sum)

    def getAllColSum(self):
        """func."""
        startCol = 9
        endCol = 24
        sum = 0
        data = self._data.copy()
        self._colSum.clear()
        for col in range(startCol, endCol + 1):
            sum = self.getColumnSum(data, col)
            self._colSum.append(sum)
        return self._colSum

    def getColumnSum(self, data, col):
        """func."""
        sum = 0
        for row in data:
            el = row[col]
            if not el:
                continue
            sum += float(el)
        return sum


class KafedraModels(BasicTableModel):
    """class."""

    def __init__(self, data=[], header=[]):
        """func."""
        super(KafedraModels, self).__init__(data, header)

    def flags(self, index=None):
        """func."""
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        """func."""
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            return value
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self._data[row][column]
        if role == Qt.TextAlignmentRole:
            return QVariant(Qt.AlignCenter)

    def removeRows(self, position, rows, parent=QModelIndex()):
        """Remove rows from the model."""
        self.beginRemoveRows(parent, position, position + rows - 1)
        del self._data[position:position+rows]
        self.endRemoveRows()
        return True

    def insertRow(self, row, value=None, parent=QModelIndex()):
        """func."""
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, value)
        self.endInsertRows()

    def get_col_by_name(self, colName):
        """func."""
        try:
            col_index = self._header.index(colName)
        except ValueError:
            return False
        data = []
        for i in self._data:
            data.append(i[col_index])
        return data


class MyListModel(QAbstractListModel):
    """class."""

    def __init__(self, data=[], ids=None):
        """func."""
        self.__data = data
        self._ids = ids
        super(MyListModel, self).__init__()

    def rowCount(self, parent=None):
        """func."""
        return len(self.__data)

    def data(self, index, role):
        """func."""
        if role == Qt.DisplayRole:
            row = index.row()
            value = self.__data[row]
            return value
        if role == Qt.ToolTipRole:
            return 'Нюхая бебру'

    def flags(self, index):
        """func."""
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRows(self, position, rows, data, parent=QModelIndex()):
        """func."""
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.__data.insert(position, data)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        """func."""
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            value = self.__data[position]
            self.__data.remove(value)
        self.endRemoveRows()
        return True

    def get_id(self, current_index):
        """Get the id for the current index."""
        return self._ids[current_index]

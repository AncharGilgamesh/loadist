"""Teacher class."""


class Teacher():
    """class."""

    """
    Класс предназначен для хранения информации о преподавателях
    self._name - ФИО.
    self._pochasPlus - Если хочешь добавить почасовку в осн таблицу
    self._pochas - если делаешь почасовую таблицу
    self._tableType - обычная/почасовая
    self._sovmestit - совместительство. Добавляется к часам работы препода
    Общая ставка строится по формуле:
     Часы работы = Ставка * ставка по должности + почасплюс +
     совместительство * ставка по должности
     Если просто почасовая таблица, то часы равны pochas
    """

    def __init__(self, tbl_id, tchr_id, total):
        """func."""
        self._name = None
        self._doljnost = None
        self._stvkaDljnst = None
        self._zvanie = None
        self._stepen = None
        self._pochasPlus = None
        self._sovmestit = None
        self._tableType = None
        self._pochas = None
        self._stvka = None
        self._totalTime = total
        self._tbl_id = tbl_id
        self._teacher_id = tchr_id

    def get_tbl_id(self):
        """func."""
        return self._tbl_id

    def set_tbl_id(self, id):
        """func."""
        self._tbl_id = id

    def get_teacher_id(self):
        """func."""
        return self._teacher_id

    def set_teacher_id(self, id):
        """func."""
        self._teacher_id = id

    def getName(self):
        """func."""
        return self._name

    def setName(self, name):
        """func."""
        self._name = name

    def setDoljnost(self, doljnost, stavka):
        """func."""
        self._doljnost[doljnost] = stavka

    def getDoljnost(self):
        """func."""
        return self._doljnost.items()

    def setZvanie(self, zvanie):
        """func."""
        self._zvanie = zvanie

    def getZvanie(self):
        """func."""
        return self._zvanie

    def setStepen(self, stepen):
        """func."""
        self._stepen = stepen

    def getStepen(self):
        """func."""
        return self._stepen

    def setPochasPlus(self, time):
        """func."""
        self._pochasPlus = time

    def getPochasPlus(self):
        """func."""
        return self._pochasPlus

    def setSovmest(self, time):
        """func."""
        self._sovmestit = time

    def getSovmest(self):
        """func."""
        return self._sovmestit

    def setPochas(self, time):
        """func."""
        self._pochas = time

    def getPochas(self):
        """func."""
        return self._pochas

    def setStvka(self, stvka):
        """func."""
        self._stvka = stvka

    def getStvka(self):
        """func."""
        return self._stvka

    def setDljnstStvka(self, stvka):
        """func."""
        self._stvkaDljnst = stvka

    def getDljnstStvka(self):
        """func."""
        return self._stvkaDljnst

    def setTotalTime(self, time):
        """func."""
        self._totalTime = time

    def getTotalTime(self):
        """func."""
        return self._totalTime

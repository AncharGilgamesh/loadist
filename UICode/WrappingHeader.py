"""Заголовок таблицы: колонки делят ширину, длинный текст переносится."""

from PyQt5.QtCore import QEvent, QRect, Qt, QTimer
from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader


class WrappingHeader(QHeaderView):
    """Растягивает колонки по ширине таблицы и держит подпись внутри секции."""

    def __init__(self, parent=None):
        """func."""
        super().__init__(Qt.Horizontal, parent)
        self._fitting = False
        self._pending = False
        self._text_color = None
        self.setHighlightSections(False)
        self.setStretchLastSection(False)
        self.setSectionResizeMode(QHeaderView.Stretch)
        self.setMinimumSectionSize(48)
        self.setDefaultAlignment(Qt.AlignCenter)
        self.setTextElideMode(Qt.ElideNone)
        self.sectionResized.connect(self._schedule_fit)
        self.sectionCountChanged.connect(self._schedule_fit)

    def event(self, event):
        """Сбрасывает цвет подписи, когда меняется тема."""
        if event.type() in (
            QEvent.StyleChange,
            QEvent.PaletteChange,
            QEvent.FontChange,
        ):
            self._text_color = None
        return super().event(event)

    def _section_text_color(self):
        """Берёт цвет подписи из текущей темы, а не из общей палитры окна."""
        if self._text_color is not None:
            return self._text_color
        image = QImage(28, 18, QImage.Format_ARGB32_Premultiplied)
        image.fill(QColor("#1e3a4c"))
        painter = QPainter(image)
        option = QStyleOptionHeader()
        self.initStyleOption(option)
        option.rect = QRect(0, 0, 28, 18)
        option.text = "Ag"
        option.textAlignment = Qt.AlignCenter
        self.style().drawControl(QStyle.CE_Header, option, painter, self)
        painter.end()
        background = image.pixelColor(1, 1)
        best = background
        best_delta = 0
        for y in range(18):
            for x in range(28):
                color = image.pixelColor(x, y)
                delta = abs(color.lightness() - background.lightness())
                if delta > best_delta:
                    best = color
                    best_delta = delta
        if best_delta < 25:
            if background.lightness() < 140:
                best = QColor("#f7f3ea")
            else:
                best = QColor("#243038")
        self._text_color = best
        return best

    def _schedule_fit(self, *_args):
        if self._fitting or self._pending:
            return
        self._pending = True
        QTimer.singleShot(0, self._fit_text)

    def _fit_text(self):
        """Поднимает строку заголовка, чтобы перенос поместился в колонку."""
        self._pending = False
        if self._fitting or self.model() is None:
            return
        self._fitting = True
        flags = Qt.AlignCenter | Qt.TextWordWrap | Qt.TextWrapAnywhere
        height = self.fontMetrics().height() + 14
        for index in range(self.count()):
            if self.isSectionHidden(index):
                continue
            text = self.model().headerData(index, Qt.Horizontal, Qt.DisplayRole)
            if text is None:
                continue
            width = max(self.sectionSize(index) - 16, 48)
            bounds = self.fontMetrics().boundingRect(
                0, 0, width, 500, flags, str(text)
            )
            height = max(height, bounds.height() + 14)
        if self.height() != height:
            self.setFixedHeight(height)
        self._fitting = False
        self.viewport().update()

    def paintSection(self, painter, rect, logical_index):
        """Рисует фон секции и подпись с переносом."""
        if self.model() is None or not rect.isValid():
            return
        painter.save()
        option = QStyleOptionHeader()
        self.initStyleOption(option)
        option.rect = rect
        option.section = logical_index
        option.text = ""
        self.style().drawControl(QStyle.CE_Header, option, painter, self)
        text = self.model().headerData(
            logical_index, Qt.Horizontal, Qt.DisplayRole
        )
        if text is not None:
            painter.setPen(self._section_text_color())
            painter.setClipRect(rect)
            painter.drawText(
                rect.adjusted(6, 4, -6, -4),
                int(Qt.AlignCenter | Qt.TextWordWrap | Qt.TextWrapAnywhere),
                str(text),
            )
        painter.restore()

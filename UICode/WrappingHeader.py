from PyQt5.QtCore import QEvent, QRect, Qt, QTimer
from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader, QToolTip


class WrappingHeader(QHeaderView):

    def __init__(self, parent=None):
        """func."""
        super().__init__(Qt.Horizontal, parent)
        self._fitting = False
        self._pending = False
        self._text_color = None
        self._max_lines = 2
        self.setHighlightSections(False)
        self.setStretchLastSection(False)
        self.setSectionResizeMode(QHeaderView.Stretch)
        self.setMinimumSectionSize(48)
        self.setDefaultAlignment(Qt.AlignCenter)
        self.setTextElideMode(Qt.ElideNone)
        self.sectionResized.connect(self._schedule_fit)
        self.sectionCountChanged.connect(self._schedule_fit)

    def event(self, event):
        """func."""
        if event.type() in (
            QEvent.StyleChange,
            QEvent.PaletteChange,
            QEvent.FontChange,
        ):
            self._text_color = None
        return super().event(event)

    def _section_text_color(self):
        """func."""
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

    def _wrap_header(self, text, width):
        """func."""
        metrics = self.fontMetrics()
        raw = str(text)
        if metrics.horizontalAdvance(raw) <= max(width, 1):
            return raw
        lines = []
        current = ""
        for word in raw.split(" "):
            for part in self._split_wide_word(word, width, metrics):
                candidate = part if not current else current + " " + part
                too_wide = metrics.horizontalAdvance(candidate) > width
                if current and too_wide:
                    lines.append(current)
                    current = part
                else:
                    current = candidate
        if current:
            lines.append(current)
        if len(lines) <= self._max_lines:
            return "\n".join(lines)
        visible = lines[: self._max_lines]
        last = visible[-1].rstrip()
        ellipsis = "…"
        while last and metrics.horizontalAdvance(last + ellipsis) > width:
            last = last[:-1].rstrip()
        visible[-1] = (last + ellipsis) if last else ellipsis
        return "\n".join(visible)

    def _split_wide_word(self, word, width, metrics):
        if metrics.horizontalAdvance(word) <= width:
            return [word]
        parts = []
        chunk = ""
        for char in word:
            trial = chunk + char
            if chunk and metrics.horizontalAdvance(trial) > width:
                parts.append(chunk)
                chunk = char
            else:
                chunk = trial
        if chunk:
            parts.append(chunk)
        return parts

    def _fit_text(self):
        """func."""
        self._pending = False
        if self._fitting or self.model() is None:
            return
        self._fitting = True
        metrics = self.fontMetrics()
        line = metrics.lineSpacing()
        padding = 8
        height = line + padding
        limit = self._max_lines * line + padding
        for index in range(self.count()):
            if self.isSectionHidden(index):
                continue
            text = self.model().headerData(index, Qt.Horizontal, Qt.DisplayRole)
            if text is None:
                continue
            width = max(self.sectionSize(index), 1)
            prepared = self._wrap_header(text, width)
            lines = prepared.count("\n") + 1
            height = max(height, lines * line + padding)
        height = min(height, limit)
        if self.height() != height:
            self.setFixedHeight(height)
        self._fitting = False
        self.viewport().update()

    def paintSection(self, painter, rect, logical_index):
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
                rect.adjusted(0, 2, 0, -2),
                int(Qt.AlignCenter),
                self._wrap_header(text, max(rect.width(), 1)),
            )
        painter.restore()

    def viewportEvent(self, event):
        if event.type() == QEvent.ToolTip and self.model() is not None:
            index = self.logicalIndexAt(event.pos())
            text = None
            if index >= 0:
                text = self.model().headerData(
                    index, Qt.Horizontal, Qt.DisplayRole
                )
            if text:
                QToolTip.showText(event.globalPos(), str(text), self.viewport())
            else:
                QToolTip.hideText()
            return True
        return super().viewportEvent(event)

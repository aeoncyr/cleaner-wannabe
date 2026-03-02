import math
from PySide6.QtCore import Qt, QTimer, QSize, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from gui_qt.theme import asset_path, THEME

def make_nav_icon(kind: str, color_hex: str) -> QPixmap:
    size = 20
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color_hex), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)

    if kind == "scan":
        painter.drawEllipse(3, 3, 10, 10)
        painter.drawLine(12, 12, 18, 18)
    elif kind == "clean":
        painter.drawLine(4, 14, 16, 2)
        painter.drawRoundedRect(3, 13, 10, 4, 2, 2)
    elif kind == "tools":
        painter.drawEllipse(4, 4, 12, 12)
        for i in range(6):
            angle = i * 60
            painter.save()
            painter.translate(10, 10)
            painter.rotate(angle)
            painter.drawLine(0, -10, 0, -7)
            painter.restore()
    else:
        painter.drawEllipse(4, 4, 12, 12)

    painter.end()
    return pix

class CatIllustration(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 160)
        self.pixmap = QPixmap(asset_path("cat.png"))
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)

    def sizeHint(self):
        return QSize(220, 160)

    def _tick(self):
        self.phase += 0.08
        if self.phase > 6.28:
            self.phase = 0.0
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Soft bubble background uses translucent white
        bubble = QColor(255, 255, 255, 160)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bubble)
        for x, y, r in [(30, 30, 18), (70, 20, 10), (190, 30, 14), (165, 90, 20), (60, 120, 16)]:
            painter.drawEllipse(QRectF(x, y, r * 2, r * 2))

        # Floating junk elements dynamically pulled from theme-ish colors
        painter.setPen(Qt.NoPen)
        paper = QColor(THEME["bg_sidebar"]) # "#F3EBE1"
        float_offset = 2.5 * math.sin(self.phase)
        for x, y, angle in [(40, 18, -10), (150, 24, 12), (120, 88, -6)]:
            painter.save()
            painter.translate(x, y + float_offset)
            painter.rotate(angle)
            painter.setBrush(paper)
            
            # Draw tiny shadow
            painter.setBrush(QColor(0,0,0,10))
            painter.drawRoundedRect(QRectF(1, 2, 24, 16), 3, 3)
            # Draw paper
            painter.setBrush(paper)
            painter.drawRoundedRect(QRectF(0, 0, 24, 16), 3, 3)
            painter.restore()

        # CD disk
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(QPen(QColor(THEME["border_light"]), 1))
        painter.drawEllipse(QRectF(w * 0.70, h * 0.20 + float_offset, 26, 26))
        painter.setBrush(QColor("#F7F1EA"))
        painter.drawEllipse(QRectF(w * 0.72, h * 0.22 + float_offset, 8, 8))

        # Banana peel
        painter.setBrush(QColor(THEME["accent"]))
        painter.setPen(QPen(QColor(THEME["primary"]), 1))
        painter.drawRoundedRect(QRectF(w * 0.75, h * 0.68 + float_offset, 26, 10), 6, 6)

        if not self.pixmap.isNull():
            max_w = int(w * 0.84)
            max_h = int(h * 0.84)
            pix = self.pixmap.scaled(
                max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            x = (w - pix.width()) / 2
            y = (h - pix.height()) / 2 + 4 + 2 * math.sin(self.phase)
            painter.drawPixmap(int(x), int(y), pix)

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect
from PySide6.QtGui import QFont, QColor
from gui_qt.theme import FONT_DISPLAY

class StatCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

        # Soft Premium Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 8)) # Extremely subtle
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("Muted")
        
        self.value_lbl = QLabel("0%")
        self.value_lbl.setFont(QFont(FONT_DISPLAY, 18, QFont.Bold))
        
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)
        layout.addWidget(self.bar)

    def set_value(self, percentage: float, label_text: str = None):
        self.bar.setValue(int(percentage))
        if label_text:
            self.value_lbl.setText(label_text)
        else:
            self.value_lbl.setText(f"{percentage}%")

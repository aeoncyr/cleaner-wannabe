import os
import datetime
import psutil

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QPushButton,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QColor

from gui_qt.theme import FONT_DISPLAY, FONT_BODY
from gui_qt.widgets.cards import StatCard

class DashboardView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self._build_ui()
        self._start_dashboard_timer()

    def _page_header(self, title, subtitle):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont(FONT_DISPLAY, 22, QFont.DemiBold))
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setObjectName("Muted")
        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)
        return container

    def _get_greeting(self):
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning, User"
        if 12 <= hour < 18:
            return "Good Afternoon, User"
        return "Good Evening, User"

    def _get_available_drives(self):
        drives = []
        try:
            for partition in psutil.disk_partitions():
                if "fixed" in partition.opts or "removable" in partition.opts:
                    drives.append(partition.device)
        except Exception:
            drives.append("C:\\")
        if not drives:
            drives.append("C:\\")
        return sorted(set(drives))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.addWidget(
            self._page_header(
                self._get_greeting(),
                "A calm, real-time snapshot of your system health.",
            )
        )
        header_row.addStretch(1)

        drive_card = QFrame()
        drive_card.setObjectName("Card")

        ds = QGraphicsDropShadowEffect(drive_card)
        ds.setBlurRadius(20)
        ds.setOffset(0, 4)
        ds.setColor(QColor(0, 0, 0, 8))
        drive_card.setGraphicsEffect(ds)

        drive_layout = QHBoxLayout(drive_card)
        drive_layout.setContentsMargins(12, 8, 12, 8)
        drive_layout.setSpacing(8)
        drive_label = QLabel("Monitor")
        drive_label.setObjectName("Muted")
        self.drive_combo = QComboBox()
        self.drive_combo.addItems(self._get_available_drives())
        self.drive_combo.currentTextChanged.connect(self._update_dashboard_stats)
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.drive_combo)
        header_row.addWidget(drive_card)
        layout.addLayout(header_row)

        stats = QHBoxLayout()
        self.cpu_card = StatCard("CPU Load")
        self.ram_card = StatCard("Memory")
        self.disk_card = StatCard("Storage")
        stats.addWidget(self.cpu_card)
        stats.addWidget(self.ram_card)
        stats.addWidget(self.disk_card)
        layout.addLayout(stats)

        actions_label = QLabel("Quick Actions")
        actions_label.setObjectName("Muted")
        actions_label.setFont(QFont(FONT_BODY, 11, QFont.Bold))
        layout.addWidget(actions_label)

        actions = QHBoxLayout()
        quick_clean = QPushButton("🧹  Quick Clean\nScan & clean junk")
        quick_clean.setObjectName("CardButton")
        quick_clean.clicked.connect(lambda: self.main_app.navigate_to("clean"))
        
        large_files = QPushButton("📦  Large Files\nFind space hogs")
        large_files.setObjectName("CardButton")
        large_files.clicked.connect(lambda: self.main_app.navigate_to("tools", 0))
        
        startup = QPushButton("🚀  Startup\nTrim boot time")
        startup.setObjectName("CardButton")
        startup.clicked.connect(lambda: self.main_app.navigate_to("tools", 1))
        
        for btn in (quick_clean, large_files, startup):
            btn.setMinimumHeight(88)
            btn.setCursor(Qt.PointingHandCursor)
            
        actions.addWidget(quick_clean)
        actions.addWidget(large_files)
        actions.addWidget(startup)
        layout.addLayout(actions)
        layout.addStretch(1)

    def _start_dashboard_timer(self):
        self._update_dashboard_stats()
        self.dashboard_timer = QTimer(self)
        self.dashboard_timer.timeout.connect(self._update_dashboard_stats)
        self.dashboard_timer.start(2000)

    def _update_dashboard_stats(self):
        try:
            cpu = psutil.cpu_percent()
            self.cpu_card.set_value(cpu)

            ram = psutil.virtual_memory()
            self.ram_card.set_value(ram.percent)

            drive = self.drive_combo.currentText()
            if os.path.exists(drive):
                disk = psutil.disk_usage(drive)
                self.disk_card.set_value(disk.percent, f"{disk.percent}% Used")
        except Exception:
            pass

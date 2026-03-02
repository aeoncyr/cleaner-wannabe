from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
)

from core.scanner import Scanner
from core.cleaner import Cleaner
from core.analyzer import Analyzer
from core.utils import is_admin

from gui_qt.theme import FONT_BODY, FONT_DISPLAY, THEME, asset_path, get_stylesheet
from gui_qt.widgets.illustrations import make_nav_icon
from gui_qt.views.dashboard_view import DashboardView
from gui_qt.views.cleaner_view import CleanerView
from gui_qt.views.tools_view import ToolsView

class CleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Core Engine Services
        self.scanner = Scanner()
        self.cleaner = Cleaner()
        self.analyzer = Analyzer()

        self.setWindowTitle("Cleaner Wannabe")
        self.resize(1200, 760)
        self.setFont(QFont(FONT_BODY, 10))
        self.setStyleSheet(get_stylesheet())

        self._build_sidebar()
        self._build_main_content()
        
        # Link UI Actions
        self._set_active_nav(self.btn_dashboard)
        self.btn_dashboard.clicked.connect(lambda: self._set_active_nav(self.btn_dashboard))
        self.btn_cleaner.clicked.connect(lambda: self._set_active_nav(self.btn_cleaner))
        self.btn_tools.clicked.connect(lambda: self._set_active_nav(self.btn_tools))

    def _build_sidebar(self):
        root = QWidget()
        self.root_layout = QHBoxLayout(root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(10)

        logo_row = QHBoxLayout()
        logo_icon = QLabel()
        logo_pix = QPixmap(asset_path("logo.png"))
        if not logo_pix.isNull():
            logo_icon.setPixmap(
                logo_pix.scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_icon.setFixedSize(28, 28)
        logo_text = QLabel("Cleaner Wannabe")
        logo_text.setFont(QFont(FONT_DISPLAY, 14, QFont.Bold))
        logo_row.addWidget(logo_icon)
        logo_row.addWidget(logo_text)
        logo_row.addStretch(1)
        logo_wrap = QWidget()
        logo_wrap.setLayout(logo_row)
        sidebar_layout.addWidget(logo_wrap)
        
        tagline = QLabel("Windows Cache Cleaner")
        tagline.setObjectName("Tagline")
        sidebar_layout.addWidget(tagline)

        self.btn_dashboard = self._nav_button("Overview", "scan")
        self.btn_cleaner = self._nav_button("Cleaner", "clean")
        self.btn_tools = self._nav_button("Tools", "tools")

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_cleaner)
        sidebar_layout.addWidget(self.btn_tools)
        
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 rgba(90,62,43,0), stop:0.5 rgba(90,62,43,0.18), stop:1 rgba(90,62,43,0));"
        )
        sidebar_layout.addSpacing(6)
        sidebar_layout.addWidget(divider)
        sidebar_layout.addStretch(1)

        status_label = QLabel("Admin Access" if is_admin() else "User Mode")
        status_label.setObjectName("StatusChip")
        status_label.setProperty("variant", "success" if is_admin() else "warning")
        sidebar_layout.addWidget(status_label)
        
        self.root_layout.addWidget(self.sidebar)
        self.setCentralWidget(root)

    def _build_main_content(self):
        self.stack = QStackedWidget()
        self.stack.setObjectName("AppBody")
        self.root_layout.addWidget(self.stack)
        self.root_layout.setStretch(1, 1)

        # Initialize modular views
        self.dashboard_view = DashboardView(main_app=self)
        self.cleaner_view = CleanerView(self.scanner, self.cleaner)
        self.tools_view = ToolsView(self.analyzer)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.cleaner_view)
        self.stack.addWidget(self.tools_view)

    def _nav_button(self, text, icon_kind):
        btn = QPushButton(text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(40)
        icon = make_nav_icon(icon_kind, THEME["primary"])
        btn.setIcon(icon)
        btn.setIconSize(QSize(18, 18))
        return btn

    def _set_active_nav(self, btn):
        for b in [self.btn_dashboard, self.btn_cleaner, self.btn_tools]:
            b.setChecked(b is btn)
        if btn is self.btn_dashboard:
            self.stack.setCurrentWidget(self.dashboard_view)
        elif btn is self.btn_cleaner:
            self.stack.setCurrentWidget(self.cleaner_view)
        else:
            self.stack.setCurrentWidget(self.tools_view)

    def navigate_to(self, view_name: str, tab_idx: int = None):
        """Allows internal views to route to each other."""
        if view_name == "clean":
            self._set_active_nav(self.btn_cleaner)
        elif view_name == "tools":
            self._set_active_nav(self.btn_tools)
            if tab_idx is not None:
                self.tools_view.set_tab_index(tab_idx)

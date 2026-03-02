import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QHeaderView,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QFont, QColor

from core.utils import format_size
from gui_qt.theme import FONT_DISPLAY
from gui_qt.workers import LargeFilesWorker, DuplicatesWorker, AppsWorker

class ToolsView(QWidget):
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        
        self.is_scanning_dupes = False
        self.is_scanning_large = False
        self.is_loading_apps = False

        self._build_ui()

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

    def _get_default_drive(self):
        import psutil
        drives = []
        try:
            for partition in psutil.disk_partitions():
                if "fixed" in partition.opts or "removable" in partition.opts:
                    drives.append(partition.device)
        except Exception:
            drives.append("C:\\")
        if not drives:
            drives.append("C:\\")
        return sorted(set(drives))[0]

    def _get_default_pictures(self):
        root = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        pics = os.path.join(root, "Pictures")
        return pics if os.path.isdir(pics) else root

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(
            self._page_header(
                "Power Tools",
                "Deeper scans and utilities for serious cleanups.",
            )
        )

        self.tools_tabs = QTabWidget()
        self.tools_tabs.setDocumentMode(True)

        tab_shadow = QGraphicsDropShadowEffect(self.tools_tabs)
        tab_shadow.setBlurRadius(20)
        tab_shadow.setOffset(0, 4)
        tab_shadow.setColor(QColor(0, 0, 0, 8))
        self.tools_tabs.setGraphicsEffect(tab_shadow)

        layout.addWidget(self.tools_tabs, 1)

        self._build_large_files_tab()
        self._build_startup_tab()
        self._build_duplicates_tab()
        self._build_uninstaller_tab()

    def _build_large_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        hint = QLabel("Scan for large files and safely delete what you no longer need.")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        path_row = QHBoxLayout()
        self.lf_path = QLineEdit(self._get_default_drive())
        self.lf_path.setReadOnly(True)
        btn_change = QPushButton("Change")
        btn_change.setObjectName("Ghost")
        btn_change.clicked.connect(self._choose_large_files_path)
        path_row.addWidget(QLabel("Scan path:"))
        path_row.addWidget(self.lf_path, 1)
        path_row.addWidget(btn_change)
        layout.addLayout(path_row)

        size_row = QHBoxLayout()
        self.lf_size_combo = QComboBox()
        self.lf_size_combo.addItems(["100 MB", "250 MB", "500 MB", "1 GB"])
        size_row.addWidget(QLabel("Minimum size:"))
        size_row.addWidget(self.lf_size_combo)
        size_row.addStretch(1)
        layout.addLayout(size_row)

        self.lf_scan_btn = QPushButton("🔍 Scan for Files")
        self.lf_scan_btn.setObjectName("Primary")
        self.lf_scan_btn.clicked.connect(self._scan_large_files)
        layout.addWidget(self.lf_scan_btn)

        self.lf_table = QTableWidget(0, 4)
        self.lf_table.setHorizontalHeaderLabels(["Size", "Name", "Path", "Action"])
        self.lf_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.lf_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.lf_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.lf_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.lf_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lf_table.setAlternatingRowColors(True)
        self.lf_table.verticalHeader().setVisible(False)
        self.lf_table.setShowGrid(False)
        layout.addWidget(self.lf_table, 1)

        self.tools_tabs.addTab(tab, "Large Files")

    def _build_startup_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        hint = QLabel("Manage apps that start with Windows to speed up boot time.")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        refresh = QPushButton("🔄 Refresh Startup List")
        refresh.setObjectName("Primary")
        refresh.clicked.connect(self._refresh_startup)
        layout.addWidget(refresh)

        self.startup_table = QTableWidget(0, 3)
        self.startup_table.setHorizontalHeaderLabels(["Program Name", "Path", "Action"])
        self.startup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.startup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.startup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.startup_table.setAlternatingRowColors(True)
        self.startup_table.verticalHeader().setVisible(False)
        self.startup_table.setShowGrid(False)
        layout.addWidget(self.startup_table, 1)

        self.tools_tabs.addTab(tab, "Startup")
        self._refresh_startup()

    def _build_duplicates_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        hint = QLabel("Find identical files and clean up safe duplicates.")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        path_row = QHBoxLayout()
        self.dup_path = QLineEdit(self._get_default_pictures())
        self.dup_path.setReadOnly(True)
        btn_change = QPushButton("Change")
        btn_change.setObjectName("Ghost")
        btn_change.clicked.connect(self._choose_duplicates_path)
        path_row.addWidget(QLabel("Folder:"))
        path_row.addWidget(self.dup_path, 1)
        path_row.addWidget(btn_change)
        layout.addLayout(path_row)

        self.dup_scan_btn = QPushButton("🔍 Scan Duplicates")
        self.dup_scan_btn.setObjectName("Primary")
        self.dup_scan_btn.clicked.connect(self._scan_duplicates)
        layout.addWidget(self.dup_scan_btn)

        self.dup_tree = QTreeWidget()
        self.dup_tree.setHeaderLabels(["Duplicate Groups"])
        self.dup_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.dup_tree.setRootIsDecorated(False)
        self.dup_tree.setAlternatingRowColors(True)
        layout.addWidget(self.dup_tree, 1)

        delete_selected = QPushButton("Delete Selected")
        delete_selected.setObjectName("Danger")
        delete_selected.clicked.connect(self._delete_selected_duplicates)
        layout.addWidget(delete_selected)

        self.tools_tabs.addTab(tab, "Duplicates")

    def _build_uninstaller_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        hint = QLabel("Review installed apps and launch uninstallers quickly.")
        hint.setObjectName("Muted")
        layout.addWidget(hint)

        self.app_scan_btn = QPushButton("🔍 Scan Installed Apps")
        self.app_scan_btn.setObjectName("Primary")
        self.app_scan_btn.clicked.connect(self._load_apps)
        layout.addWidget(self.app_scan_btn)

        self.apps_table = QTableWidget(0, 2)
        self.apps_table.setHorizontalHeaderLabels(["Application", "Action"])
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.apps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.apps_table.setAlternatingRowColors(True)
        self.apps_table.verticalHeader().setVisible(False)
        self.apps_table.setShowGrid(False)
        layout.addWidget(self.apps_table, 1)

        self.tools_tabs.addTab(tab, "Uninstaller")

    def set_tab_index(self, index):
        self.tools_tabs.setCurrentIndex(index)

    # Handlers
    def _choose_large_files_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan")
        if path:
            self.lf_path.setText(path)

    def _parse_size_mb(self, label):
        text = label.strip().upper()
        try:
            if text.endswith("GB"):
                return int(text[:-2].strip()) * 1024
            if text.endswith("MB"):
                return int(text[:-2].strip())
            return int(text)
        except ValueError:
            return 100

    def _scan_large_files(self):
        if self.is_scanning_large:
            return

        scan_path = self.lf_path.text()
        if not scan_path or not os.path.exists(scan_path):
            QMessageBox.warning(self, "Invalid Path", "Select a valid folder or drive to scan.")
            return

        self.is_scanning_large = True
        self.lf_scan_btn.setEnabled(False)
        self.lf_scan_btn.setText("Scanning...")
        self.lf_table.setRowCount(0)

        min_size_mb = self._parse_size_mb(self.lf_size_combo.currentText())

        self.lf_thread = QThread()
        self.lf_worker = LargeFilesWorker(self.analyzer, scan_path, min_size_mb)
        self.lf_worker.moveToThread(self.lf_thread)
        self.lf_thread.started.connect(self.lf_worker.run)
        self.lf_worker.finished.connect(self._on_large_files_finished)
        self.lf_worker.finished.connect(self.lf_thread.quit)
        self.lf_worker.finished.connect(self.lf_worker.deleteLater)
        self.lf_thread.finished.connect(self.lf_thread.deleteLater)
        self.lf_thread.start()

    def _on_large_files_finished(self, files):
        self.is_scanning_large = False
        self.lf_scan_btn.setEnabled(True)
        self.lf_scan_btn.setText("🔍 Scan for Files")

        self.lf_table.setRowCount(0)
        for path, size in files[:50]:
            row = self.lf_table.rowCount()
            self.lf_table.insertRow(row)
            self.lf_table.setItem(row, 0, QTableWidgetItem(format_size(size)))
            self.lf_table.setItem(row, 1, QTableWidgetItem(os.path.basename(path)))
            self.lf_table.setItem(row, 2, QTableWidgetItem(os.path.dirname(path)))
            btn = QPushButton("Delete")
            btn.setObjectName("Danger")
            btn.clicked.connect(lambda _, p=path: self._confirm_delete_file(p))
            self.lf_table.setCellWidget(row, 3, btn)

    def _confirm_delete_file(self, filepath):
        if not filepath:
            return
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Move to Recycle Bin?\n\n{filepath}"
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.analyzer.delete_file(filepath)
        if ok:
            QMessageBox.information(self, "Delete Complete", msg)
            self._scan_large_files() # Refresh
        else:
            QMessageBox.warning(self, "Delete Failed", msg)
            
    def _refresh_startup(self):
        self.startup_table.setRowCount(0)
        items = self.analyzer.get_startup_items()
        if not items:
            return
        for item in items:
            row = self.startup_table.rowCount()
            self.startup_table.insertRow(row)
            self.startup_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.startup_table.setItem(row, 1, QTableWidgetItem(item["path"]))
            btn = QPushButton("Disable")
            btn.setObjectName("Danger")
            btn.clicked.connect(lambda _, i=item: self._disable_startup(i))
            self.startup_table.setCellWidget(row, 2, btn)

    def _disable_startup(self, item):
        confirm = QMessageBox.question(
            self, "Confirm", f"Remove '{item['name']}' from startup?"
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.analyzer.remove_startup_item(item)
        if ok:
            QMessageBox.information(self, "Startup Updated", msg)
            self._refresh_startup()
        else:
            QMessageBox.warning(self, "Failed to Remove", msg)

    def _choose_duplicates_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder for Duplicate Scan")
        if path:
            self.dup_path.setText(path)

    def _scan_duplicates(self):
        if self.is_scanning_dupes:
            return

        scan_path = self.dup_path.text()
        if not scan_path or not os.path.isdir(scan_path):
            QMessageBox.warning(self, "Invalid Folder", "Select a valid folder to scan.")
            return

        self.is_scanning_dupes = True
        self.dup_scan_btn.setEnabled(False)
        self.dup_scan_btn.setText("Scanning...")
        self.dup_tree.clear()

        self.dup_thread = QThread()
        self.dup_worker = DuplicatesWorker(self.analyzer, scan_path)
        self.dup_worker.moveToThread(self.dup_thread)
        self.dup_thread.started.connect(self.dup_worker.run)
        self.dup_worker.finished.connect(self._on_duplicates_finished)
        self.dup_worker.finished.connect(self.dup_thread.quit)
        self.dup_worker.finished.connect(self.dup_worker.deleteLater)
        self.dup_thread.finished.connect(self.dup_thread.deleteLater)
        self.dup_thread.start()

    def _on_duplicates_finished(self, dupes):
        self.is_scanning_dupes = False
        self.dup_scan_btn.setEnabled(True)
        self.dup_scan_btn.setText("🔍 Scan Duplicates")
        self.dup_tree.clear()

        if not dupes:
            item = QTreeWidgetItem(["No duplicates found."])
            item.setFlags(Qt.ItemIsEnabled)
            self.dup_tree.addTopLevelItem(item)
            return

        for _, paths in dupes.items():
            group = QTreeWidgetItem([f"Match Found ({len(paths)} copies)"])
            self.dup_tree.addTopLevelItem(group)
            for path in paths:
                child = QTreeWidgetItem([path])
                group.addChild(child)

    def _delete_selected_duplicates(self):
        items = self.dup_tree.selectedItems()
        if not items:
            QMessageBox.information(self, "No Selection", "Select duplicate files to delete.")
            return

        targets = []
        for item in items:
            if item.parent() is None:
                continue
            targets.append(item.text(0))

        if not targets:
            QMessageBox.information(self, "No Files Selected", "Select duplicate files (not group headers).")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Move {len(targets)} file(s) to Recycle Bin?"
        )
        if confirm != QMessageBox.Yes:
            return

        for path in targets:
            self.analyzer.delete_file(path)
        self._scan_duplicates()

    def _load_apps(self):
        if self.is_loading_apps:
            return

        self.is_loading_apps = True
        self.app_scan_btn.setEnabled(False)
        self.app_scan_btn.setText("Scanning...")
        self.apps_table.setRowCount(0)

        self.apps_thread = QThread()
        self.apps_worker = AppsWorker(self.analyzer)
        self.apps_worker.moveToThread(self.apps_thread)
        self.apps_thread.started.connect(self.apps_worker.run)
        self.apps_worker.finished.connect(self._on_apps_loaded)
        self.apps_worker.finished.connect(self.apps_thread.quit)
        self.apps_worker.finished.connect(self.apps_worker.deleteLater)
        self.apps_thread.finished.connect(self.apps_thread.deleteLater)
        self.apps_thread.start()

    def _on_apps_loaded(self, apps):
        self.is_loading_apps = False
        self.app_scan_btn.setEnabled(True)
        self.app_scan_btn.setText("🔍 Scan Installed Apps")

        self.apps_table.setRowCount(0)
        for app in apps:
            row = self.apps_table.rowCount()
            self.apps_table.insertRow(row)
            self.apps_table.setItem(row, 0, QTableWidgetItem(app["name"]))
            btn = QPushButton("Uninstall")
            btn.setObjectName("Danger")
            btn.clicked.connect(lambda _, a=app: self._confirm_uninstall(a))
            self.apps_table.setCellWidget(row, 1, btn)

    def _confirm_uninstall(self, app):
        if not app or not app.get("uninstall"):
            QMessageBox.warning(self, "Uninstall Failed", "No uninstall command was found for this app.")
            return
        confirm = QMessageBox.question(
            self, "Confirm Uninstall", f"Launch uninstaller for '{app.get('name', 'this app')}'?"
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.analyzer.uninstall_program(app["uninstall"])
        if ok:
            QMessageBox.information(self, "Uninstaller Launched", msg)
        else:
            QMessageBox.warning(self, "Uninstall Failed", msg)

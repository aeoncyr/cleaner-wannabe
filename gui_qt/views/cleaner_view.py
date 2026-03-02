from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QCheckBox,
    QComboBox,
    QProgressBar,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QPlainTextEdit,
    QSplitter,
    QMessageBox,
    QHeaderView,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QFont, QColor

from core.utils import format_size
from gui_qt.theme import FONT_DISPLAY, FONT_BODY
from gui_qt.widgets.illustrations import CatIllustration
from gui_qt.workers import ScanWorker, CleanWorker

class CleanerView(QWidget):
    def __init__(self, scanner, cleaner):
        super().__init__()
        self.scanner = scanner
        self.cleaner = cleaner
        
        self.scan_results = {}
        self.clean_targets = {}
        self.is_scanning = False
        self.is_cleaning = False

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

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(
            self._page_header(
                "System Cleaner",
                "Select what to clean, review safely, then reclaim space.",
            )
        )

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(20, 16, 20, 16)
        hero_layout.setSpacing(16)
        hero_shadow = QGraphicsDropShadowEffect(hero)
        hero_shadow.setBlurRadius(24)
        hero_shadow.setOffset(0, 6)
        hero_shadow.setColor(QColor(90, 62, 43, 50))
        hero.setGraphicsEffect(hero_shadow)

        hero_art = CatIllustration()
        hero_layout.addWidget(hero_art)

        hero_text = QVBoxLayout()
        hero_title = QLabel("Time to Clean Up!")
        hero_title.setFont(QFont(FONT_DISPLAY, 18, QFont.Bold))
        hero_subtitle = QLabel(
            "We'll highlight safe cleanups and keep your system comfy."
        )
        hero_subtitle.setObjectName("Muted")
        hero_subtitle.setWordWrap(True)

        self.hero_total_label = QLabel("Total junk found: --")
        self.hero_total_label.setObjectName("HeroPill")
        self.hero_meta_label = QLabel("Run a scan to see what can be cleaned.")
        self.hero_meta_label.setObjectName("Muted")
        self.hero_meta_label.setWordWrap(True)

        hero_text.addWidget(hero_title)
        hero_text.addWidget(hero_subtitle)
        hero_text.addSpacing(6)
        hero_text.addWidget(self.hero_total_label)
        hero_text.addWidget(self.hero_meta_label)
        hero_text.addStretch(1)
        hero_layout.addLayout(hero_text, 1)

        layout.addWidget(hero)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)

        options_panel = QFrame()
        options_panel.setObjectName("Card")

        os_shadow = QGraphicsDropShadowEffect(options_panel)
        os_shadow.setBlurRadius(20)
        os_shadow.setOffset(0, 4)
        os_shadow.setColor(QColor(0, 0, 0, 8))
        options_panel.setGraphicsEffect(os_shadow)

        options_layout = QVBoxLayout(options_panel)
        options_layout.setContentsMargins(16, 16, 16, 16)
        options_layout.setSpacing(10)

        options_title = QLabel("Scan Options")
        options_title.setFont(QFont(FONT_BODY, 12, QFont.Bold))
        options_layout.addWidget(options_title)
        options_hint = QLabel("Choose categories and safety filters.")
        options_hint.setObjectName("Muted")
        options_layout.addWidget(options_hint)

        self.options_scroll = QScrollArea()
        self.options_scroll.setWidgetResizable(True)
        options_inner = QWidget()
        options_inner_layout = QVBoxLayout(options_inner)
        options_inner_layout.setContentsMargins(0, 0, 0, 0)
        options_inner_layout.setSpacing(6)

        self.option_checks = {}
        for cat in self.scanner.categories.keys():
            cb = QCheckBox(cat)
            cb.setChecked(True)
            self.option_checks[cat] = cb
            options_inner_layout.addWidget(cb)
        options_inner_layout.addStretch(1)
        self.options_scroll.setWidget(options_inner)
        options_layout.addWidget(self.options_scroll, 1)

        controls = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.setObjectName("Ghost")
        btn_all.clicked.connect(self._select_all_options)
        btn_none = QPushButton("Select None")
        btn_none.setObjectName("Ghost")
        btn_none.clicked.connect(self._select_none_options)
        controls.addWidget(btn_all)
        controls.addWidget(btn_none)
        options_layout.addLayout(controls)

        self.safe_mode_check = QCheckBox("Safe Mode (Recycle Bin)")
        self.safe_mode_check.setChecked(True)
        self.safe_mode_check.setStyleSheet("color: #5a463b;")
        options_layout.addWidget(self.safe_mode_check)

        options_layout.addWidget(QLabel("Safety Filters"))
        self.age_combo = QComboBox()
        self.age_combo.addItems(["Any time", "1 day", "7 days", "30 days"])
        options_layout.addWidget(self.age_combo)
        age_hint = QLabel("Only clean files older than the selected age.")
        age_hint.setObjectName("Muted")
        options_layout.addWidget(age_hint)

        self.scan_btn = QPushButton("Analyze Now")
        self.scan_btn.setObjectName("Primary")
        self.scan_btn.clicked.connect(self.start_scan)
        options_layout.addWidget(self.scan_btn)

        self.scan_progress = QProgressBar()
        self.scan_progress.setRange(0, 100)
        self.scan_progress.setValue(0)
        options_layout.addWidget(self.scan_progress)
        self.scan_status = QLabel("Ready to scan")
        self.scan_status.setObjectName("Muted")
        options_layout.addWidget(self.scan_status)

        results_panel = QFrame()
        results_panel.setObjectName("Card")

        rs_shadow = QGraphicsDropShadowEffect(results_panel)
        rs_shadow.setBlurRadius(20)
        rs_shadow.setOffset(0, 4)
        rs_shadow.setColor(QColor(0, 0, 0, 8))
        results_panel.setGraphicsEffect(rs_shadow)

        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(16, 16, 16, 16)
        results_layout.setSpacing(10)

        results_title = QLabel("Scan Summary")
        results_title.setFont(QFont(FONT_BODY, 12, QFont.Bold))
        results_layout.addWidget(results_title)
        self.summary_tree = QTreeWidget()
        self.summary_tree.setHeaderLabels(["Category", "Items", "Size", "Skipped"])
        self.summary_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.summary_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.summary_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.summary_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.summary_tree.setRootIsDecorated(False)
        self.summary_tree.setIndentation(0)
        self.summary_tree.setAlternatingRowColors(True)
        self.summary_tree.setUniformRowHeights(True)
        self.summary_tree.itemChanged.connect(self._update_clean_totals)
        self.summary_tree.itemDoubleClicked.connect(self._open_category_details)
        results_layout.addWidget(self.summary_tree)

        self.summary_total = QLabel(f"Selected: 0 items ({format_size(0)})")
        self.summary_total.setObjectName("Muted")
        results_layout.addWidget(self.summary_total)

        log_title = QLabel("Activity Log")
        log_title.setFont(QFont(FONT_BODY, 12, QFont.Bold))
        results_layout.addWidget(log_title)
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        results_layout.addWidget(self.log_box, 1)

        self.clean_btn = QPushButton("Clean Files")
        self.clean_btn.setObjectName("PrimaryPill")
        self.clean_btn.setEnabled(False)
        self.clean_btn.clicked.connect(self.start_clean)
        self.clean_btn.setMinimumHeight(44)
        clean_shadow = QGraphicsDropShadowEffect(self.clean_btn)
        clean_shadow.setBlurRadius(24)
        clean_shadow.setOffset(0, 8)
        clean_shadow.setColor(QColor(90, 62, 43, 90))
        self.clean_btn.setGraphicsEffect(clean_shadow)
        results_layout.addWidget(self.clean_btn)

        splitter.addWidget(options_panel)
        splitter.addWidget(results_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, 1)

        self._show_scan_summary_empty()

    def _select_all_options(self):
        for cb in self.option_checks.values():
            cb.setChecked(True)

    def _select_none_options(self):
        for cb in self.option_checks.values():
            cb.setChecked(False)

    def _parse_age_days(self, text):
        if not text or "any" in text.lower():
            return 0
        try:
            return int(text.split()[0])
        except Exception:
            return 0

    def _append_log(self, text):
        self.log_box.appendPlainText(text)

    def _set_scan_status(self, text, progress=None):
        self.scan_status.setText(text)
        if progress is not None:
            self.scan_progress.setValue(int(progress * 100))

    def _show_scan_summary_empty(self, title="No Scan Results"):
        self.summary_tree.clear()
        item = QTreeWidgetItem([title, "", "", ""])
        item.setFlags(Qt.ItemIsEnabled)
        self.summary_tree.addTopLevelItem(item)
        self.summary_total.setText(f"Selected: 0 items ({format_size(0)})")
        self.clean_btn.setEnabled(False)
        self._set_hero_summary(None, None, "Run a scan to see what can be cleaned.")

    def _set_hero_summary(self, total_size, total_items, status):
        if hasattr(self, "hero_total_label"):
            if total_size is None:
                self.hero_total_label.setText("Total junk found: --")
            else:
                self.hero_total_label.setText(
                    f"Total junk found: {format_size(total_size)}"
                )
        if hasattr(self, "hero_meta_label") and status:
            self.hero_meta_label.setText(status)
        elif hasattr(self, "hero_meta_label") and total_items is not None:
            self.hero_meta_label.setText(
                f"{total_items} items ready for a gentle cleanup."
            )

    def _populate_summary_tree(self):
        self.summary_tree.blockSignals(True)
        self.summary_tree.clear()
        for cat, data in self.scan_results.items():
            files = data.get("files", [])
            size = data.get("size", 0)
            skipped = data.get("skipped_recent", 0)
            item = QTreeWidgetItem(
                [cat, str(len(files)), format_size(size), str(skipped) if skipped else ""]
            )
            item.setData(0, Qt.UserRole, cat)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked if files else Qt.Unchecked)
            self.summary_tree.addTopLevelItem(item)
        self.summary_tree.blockSignals(False)
        self._update_clean_totals()

    def _get_selected_scan_results(self):
        selected = {}
        for i in range(self.summary_tree.topLevelItemCount()):
            item = self.summary_tree.topLevelItem(i)
            cat = item.data(0, Qt.UserRole)
            if not cat:
                continue
            if item.checkState(0) == Qt.Checked:
                selected[cat] = self.scan_results.get(cat, {})
        return selected

    def _update_clean_totals(self):
        selected = self._get_selected_scan_results()
        total_size = sum(d.get("size", 0) for d in selected.values())
        total_files = sum(len(d.get("files", [])) for d in selected.values())
        self.summary_total.setText(f"Selected: {total_files} items ({format_size(total_size)})")
        self.clean_btn.setEnabled(bool(total_size) and not self.is_scanning and not self.is_cleaning)

    def _open_category_details(self, item, _column):
        cat = item.data(0, Qt.UserRole)
        if not cat:
            return
        data = self.scan_results.get(cat, {})
        items = data.get("items", [])
        if not items:
            items = [{"path": p, "size": None} for p in data.get("files", [])]

        dlg = QMessageBox(self)
        dlg.setWindowTitle(f"{cat} Details")
        preview = "\n".join(
            f"{format_size(i.get('size')) if i.get('size') is not None else '':>10}  {i.get('path', '')}"
            for i in items[:200]
        )
        if len(items) > 200:
            preview += f"\n... Showing first 200 items of {len(items)} total."
        dlg.setText(preview or "No items to display.")
        dlg.exec()

    def start_scan(self):
        if self.is_scanning:
            return

        selected = [k for k, cb in self.option_checks.items() if cb.isChecked()]
        if not selected:
            QMessageBox.information(self, "Nothing Selected", "Select at least one scan category.")
            return

        self.is_scanning = True
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)
        self.scan_progress.setValue(0)
        self._set_scan_status("Scanning...")
        self.log_box.clear()
        self._append_log("--- Scanning System ---")
        self._show_scan_summary_empty("Scanning...")
        self._set_hero_summary(None, None, "Scanning... preparing a cozy cleanup plan.")

        min_age_days = self._parse_age_days(self.age_combo.currentText())

        self.scan_thread = QThread()
        self.scan_worker = ScanWorker(self.scanner, selected, min_age_days)
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.finished.connect(self.scan_worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)
        self.scan_thread.start()

    def _on_scan_progress(self, idx, total, cat):
        if total:
            self._set_scan_status(f"Scanning {cat} ({idx}/{total})", idx / total)

    def _on_scan_finished(self, results, min_age_days):
        self.is_scanning = False
        self.scan_btn.setEnabled(True)
        self.scan_results = results

        total_size = 0
        total_files = 0
        skipped_recent = 0
        skipped_recent_size = 0
        report_lines = []
        errors = []

        for cat, data in self.scan_results.items():
            size = data.get("size", 0)
            files = data.get("files", [])
            skipped = data.get("skipped_recent", 0)
            skipped_recent += skipped
            skipped_recent_size += data.get("skipped_recent_size", 0)
            total_size += size
            total_files += len(files)
            summary = f"[{cat}] Found {len(files)} items ({format_size(size)})"
            if skipped:
                summary += f" • Skipped {skipped} recent"
            report_lines.append(summary)
            if data.get("error"):
                errors.append(f"[{cat}] {data.get('error')}")

        self._append_log("\n".join(report_lines))
        self._append_log(f"\nTotal Junk: {format_size(total_size)} ({total_files} items)")
        if min_age_days:
            if skipped_recent:
                self._append_log(
                    f"Safety Filter: Skipped {skipped_recent} recent items "
                    f"({format_size(skipped_recent_size)}) newer than {min_age_days} day(s)."
                )
            else:
                self._append_log(
                    f"Safety Filter: Only files older than {min_age_days} day(s) were included."
                )

        if errors:
            self._append_log("\nWarnings:")
            for err in errors:
                self._append_log(f"- {err}")

        if total_size > 0:
            self._set_scan_status("Scan complete", 1)
            self._set_hero_summary(total_size, total_files, None)
            self._populate_summary_tree()
        else:
            self._set_scan_status("No junk found", 0)
            self._set_hero_summary(None, None, "All clear. Your system looks tidy.")
            self._show_scan_summary_empty()

    def start_clean(self):
        if self.is_cleaning:
            return

        if not self.scan_results:
            QMessageBox.information(self, "Nothing to Clean", "Run a scan first.")
            return

        targets = self._get_selected_scan_results()
        if not targets:
            QMessageBox.information(self, "Nothing Selected", "Select at least one category from the summary.")
            return

        total_size = sum(d.get("size", 0) for d in targets.values())
        total_files = sum(len(d.get("files", [])) for d in targets.values())
        if total_size <= 0:
            QMessageBox.information(self, "Nothing to Clean", "No junk was found in the last scan.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Clean",
            f"Clean {total_files} selected items ({format_size(total_size)})?",
        )
        if confirm != QMessageBox.Yes:
            return

        self.is_cleaning = True
        self.clean_targets = targets
        self.clean_btn.setEnabled(False)
        self.scan_btn.setEnabled(False)
        self._set_scan_status("Cleaning...", 0)
        self._append_log("\n--- Cleaning ---")
        self._set_hero_summary(None, None, "Cleaning in progress... stay comfy.")

        self.clean_thread = QThread()
        self.clean_worker = CleanWorker(self.cleaner, targets, self.safe_mode_check.isChecked())
        self.clean_worker.moveToThread(self.clean_thread)
        self.clean_thread.started.connect(self.clean_worker.run)
        self.clean_worker.log.connect(self._append_log)
        self.clean_worker.progress.connect(self._on_clean_progress)
        self.clean_worker.finished.connect(self._on_clean_finished)
        self.clean_worker.finished.connect(self.clean_thread.quit)
        self.clean_worker.finished.connect(self.clean_worker.deleteLater)
        self.clean_thread.finished.connect(self.clean_thread.deleteLater)
        self.clean_thread.start()

    def _on_clean_progress(self, idx, total, cat, _count, _size):
        if total:
            self._set_scan_status(f"Cleaning {cat} ({idx}/{total})", idx / total)

    def _on_clean_finished(self, total_items, total_size, errors):
        self.is_cleaning = False
        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(False)
        self._set_scan_status("Cleaning complete", 1)
        self._append_log(f"\nDone! Freed {format_size(total_size)} ({total_items} items).")
        self.scan_results = {}
        self.clean_targets = {}
        self._set_hero_summary(None, None, "Cleanup complete. Enjoy the extra space.")
        self._show_scan_summary_empty()

        if errors:
            self._append_log("\nErrors:")
            for err in errors:
                self._append_log(f"- {err}")


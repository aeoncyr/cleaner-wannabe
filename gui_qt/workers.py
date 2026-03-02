from PySide6.QtCore import QObject, Signal
from core.utils import format_size


class ScanWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(dict, int)

    def __init__(self, scanner, selected, min_age_days):
        super().__init__()
        self.scanner = scanner
        self.selected = selected
        self.min_age_days = min_age_days

    def run(self):
        def _progress(idx, total, cat, _data):
            self.progress.emit(idx, total, cat)

        results = self.scanner.scan_selected(
            self.selected, progress_cb=_progress, min_age_days=self.min_age_days
        )
        self.finished.emit(results, self.min_age_days)


class CleanWorker(QObject):
    progress = Signal(int, int, str, int, int)
    log = Signal(str)
    finished = Signal(int, int, list)

    def __init__(self, cleaner, targets, use_recycle):
        super().__init__()
        self.cleaner = cleaner
        self.targets = targets
        self.use_recycle = use_recycle

    def run(self):
        ok, msg = self.cleaner.run_safety_checks()
        if not ok:
            self.log.emit(f"Restore point warning: {msg}")

        total_items = 0
        total_size = 0
        errors = []

        total_cats = len(self.targets)
        for idx, (cat, data) in enumerate(self.targets.items(), start=1):
            count, size, errs = self.cleaner.clean_category(cat, data, self.use_recycle)
            total_items += count
            total_size += size
            if errs:
                errors.extend(errs)
            self.log.emit(f"[{cat}] Cleaned {count} items ({format_size(size)})")
            self.progress.emit(idx, total_cats, cat, count, size)

        self.finished.emit(total_items, total_size, errors)


class LargeFilesWorker(QObject):
    finished = Signal(list)

    def __init__(self, analyzer, path, min_size_mb):
        super().__init__()
        self.analyzer = analyzer
        self.path = path
        self.min_size_mb = min_size_mb

    def run(self):
        files = self.analyzer.find_large_files(self.path, min_size_mb=self.min_size_mb)
        self.finished.emit(files)


class DuplicatesWorker(QObject):
    finished = Signal(dict)

    def __init__(self, analyzer, path):
        super().__init__()
        self.analyzer = analyzer
        self.path = path

    def run(self):
        dupes = self.analyzer.find_duplicates(self.path)
        self.finished.emit(dupes)


class AppsWorker(QObject):
    finished = Signal(list)

    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer

    def run(self):
        apps = self.analyzer.get_installed_programs()
        self.finished.emit(apps)

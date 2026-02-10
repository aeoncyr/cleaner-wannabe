import customtkinter as ctk
import threading
import psutil
import os
import datetime
import tkinter.filedialog as filedialog
from core.scanner import Scanner
from core.cleaner import Cleaner
from core.analyzer import Analyzer
from core.utils import format_size, is_admin
import tkinter.messagebox as messagebox

# --- Theme Configuration ---
THEME = {
    "bg_main": "#1a1a2e",       # Deep Navy
    "bg_sidebar": "#16213e",    # Slightly lighter navy
    "bg_card": "#16213e",       # Card background
    "primary": "#3A7CA5",       # Professional Blue
    "primary_hover": "#2c5d7c",
    "text": "#E0E1DD",          # Off-white
    "text_muted": "#8d99ae",
    "danger": "#e63946",
    "success": "#2a9d8f",
    "warning": "#e9c46a",
    "font_family": "Segoe UI"   # Standard functional font
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") # Fallback

# --- Custom Components ---

class HealthCard(ctk.CTkFrame):
    """A visual card for the dashboard status"""
    def __init__(self, master, title, icon, value, color=THEME["primary"]):
        super().__init__(master, fg_color=THEME["bg_card"], corner_radius=15, border_width=1, border_color="#252a40")
        self.grid_columnconfigure(0, weight=1)
        
        self.icon_label = ctk.CTkLabel(self, text=icon, font=(THEME["font_family"], 30))
        self.icon_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.title_label = ctk.CTkLabel(self, text=title, font=(THEME["font_family"], 14), text_color=THEME["text_muted"])
        self.title_label.grid(row=1, column=0, sticky="w", padx=20)
        
        self.value_label = ctk.CTkLabel(self, text=value, font=(THEME["font_family"], 24, "bold"), text_color=THEME["text"])
        self.value_label.grid(row=2, column=0, sticky="w", padx=20, pady=(5, 10))
        
        self.progress = ctk.CTkProgressBar(self, height=6, progress_color=color)
        self.progress.set(0)
        self.progress.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

    def update_data(self, value_text, progress_float, color=None):
        self.value_label.configure(text=value_text)
        self.progress.set(progress_float)
        if color:
             self.progress.configure(progress_color=color)

class NavButton(ctk.CTkFrame):
    """Sidebar navigation button with active state styling and fixed alignment"""
    def __init__(self, master, text, icon, command, is_active=False):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.command = command
        self.is_active = is_active
        self.text = text
        self.icon = icon
        
        # Layout
        # Layout
        self.grid_columnconfigure(0, weight=0) # Auto sizing for column
        self.grid_columnconfigure(1, weight=1) # Text column
        
        # Icon Label (Fixed width widget + Left aligned with padding)
        # width=60 ensures consistent reserved space. anchor="w" aligns icon left in that space.
        self.icon_lbl = ctk.CTkLabel(self, text=icon, font=(THEME["font_family"], 20), width=60, anchor="w")
        self.icon_lbl.grid(row=0, column=0, pady=12, padx=(20, 0))
        
        # Text Label
        self.text_lbl = ctk.CTkLabel(self, text=text, font=(THEME["font_family"], 15, "bold" if is_active else "normal"), anchor="w")
        self.text_lbl.grid(row=0, column=1, pady=12, sticky="ew")
        
        # Bindings for hover and click
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", lambda e: command())
        
        self.icon_lbl.bind("<Enter>", self.on_enter)
        self.icon_lbl.bind("<Leave>", self.on_leave)
        self.icon_lbl.bind("<Button-1>", lambda e: command())
        
        self.text_lbl.bind("<Enter>", self.on_enter)
        self.text_lbl.bind("<Leave>", self.on_leave)
        self.text_lbl.bind("<Button-1>", lambda e: command())
        
        self.update_appearance()

    def on_enter(self, event):
        if not self.is_active:
            self.configure(fg_color="#1f2b4d")
            self.icon_lbl.configure(fg_color="#1f2b4d")
            self.text_lbl.configure(fg_color="#1f2b4d")

    def on_leave(self, event):
        if not self.is_active:
            self.configure(fg_color="transparent")
            self.icon_lbl.configure(fg_color="transparent")
            self.text_lbl.configure(fg_color="transparent")

    def configure(self, **kwargs):
        if "text_color" in kwargs:
            self.text_lbl.configure(text_color=kwargs.pop("text_color"))
        if "font" in kwargs:
            self.text_lbl.configure(font=kwargs.pop("font"))
        super().configure(**kwargs)
        # Propagate bg color to children if needed (Frame usually handles bg)
        # But labels are transparent by default? CustomTkinter labels might have their own bg.
        if "fg_color" in kwargs:
             color = kwargs["fg_color"]
             self.icon_lbl.configure(fg_color=color)
             self.text_lbl.configure(fg_color=color)

    def update_appearance(self):
        bg = THEME["bg_main"] if self.is_active else "transparent"
        fg = THEME["primary"] if self.is_active else THEME["text_muted"]
        font = (THEME["font_family"], 15, "bold" if self.is_active else "normal")
        
        self.super_configure(fg_color=bg)
        self.icon_lbl.configure(fg_color=bg, text_color=fg)
        self.text_lbl.configure(fg_color=bg, text_color=fg, font=font)

    def super_configure(self, **kwargs):
        super().configure(**kwargs)

    # Helper to match expected interface from set_active_nav
    def set_active(self, active):
        self.is_active = active
        self.update_appearance()

# --- Main Application ---

class CleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Cleaner Wannabe")
        self.geometry("1000x700")
        self.configure(fg_color=THEME["bg_main"])
        
        # Core Modules
        self.scanner = Scanner()
        self.cleaner = Cleaner()
        self.analyzer = Analyzer()
        
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # State
        self.current_frame = None
        self.drives = self.get_available_drives()
        self.selected_drive = ctk.StringVar(value="C:\\")
        self.scan_results = {}
        self.is_scanning = False
        self.is_cleaning = False
        self.is_scanning_dupes = False
        self.is_scanning_large = False
        self.is_loading_apps = False
        
        # UI Initialization
        self.init_sidebar()
        self.init_main_area()
        self.show_dashboard()

    def get_available_drives(self):
        drives = []
        try:
            for partition in psutil.disk_partitions():
                if 'fixed' in partition.opts or 'removable' in partition.opts:
                    drives.append(partition.device)
        except Exception:
            drives.append("C:\\")
        if not drives:
            drives.append("C:\\")
        return sorted(set(drives))

    def init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=THEME["bg_sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Fixed width
        
        # Logo (Aligned with NavButtons)
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(40, 20))
        
        logo_frame.grid_columnconfigure(0, weight=0)
        logo_frame.grid_columnconfigure(1, weight=1)
        
        # Icon (Fixed width widget + Left aligned to match nav)
        logo_icon = ctk.CTkLabel(logo_frame, text="✨", font=("Segoe UI", 24), width=60, anchor="w", text_color=THEME["primary"])
        logo_icon.grid(row=0, column=0, padx=(20, 0))
        
        # Navigation
        self.nav_btns = {}
        
        self.nav_btns["dashboard"] = NavButton(self.sidebar, "Overview", "🏠", lambda: self.show_dashboard())
        self.nav_btns["dashboard"].pack(fill="x")
        
        self.nav_btns["cleaner"] = NavButton(self.sidebar, "Cleaner", "🧹", lambda: self.show_cleaner())
        self.nav_btns["cleaner"].pack(fill="x")
        
        self.nav_btns["tools"] = NavButton(self.sidebar, "Tools", "🛠️", lambda: self.show_tools())
        self.nav_btns["tools"].pack(fill="x")
        
        # Bottom Status
        status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        
        admin_text = "Admin Access" if is_admin() else "User Mode"
        admin_color = THEME["success"] if is_admin() else THEME["warning"]
        
        ctk.CTkLabel(status_frame, text="🛡️ Security Status", font=("Segoe UI", 12, "bold"), text_color=THEME["text_muted"]).pack(anchor="w")
        ctk.CTkLabel(status_frame, text=admin_text, font=("Segoe UI", 12), text_color=admin_color).pack(anchor="w")

    def set_active_nav(self, key):
        for k, btn in self.nav_btns.items():
            btn.set_active(k == key)

    def init_main_area(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
    def clear_main(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def _append_log(self, text):
        if hasattr(self, "log_box") and self.log_box.winfo_exists():
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")

    def _set_scan_status(self, text, progress=None):
        if hasattr(self, "scan_status") and self.scan_status.winfo_exists():
            self.scan_status.configure(text=text)
        if progress is not None and hasattr(self, "scan_progress") and self.scan_progress.winfo_exists():
            self.scan_progress.set(progress)

    def _safe_config(self, widget, **kwargs):
        try:
            if widget and widget.winfo_exists():
                widget.configure(**kwargs)
        except Exception:
            pass

    def _select_all_options(self):
        for var in self.check_vars.values():
            var.set(True)

    def _select_none_options(self):
        for var in self.check_vars.values():
            var.set(False)

    def _confirm_and_delete(self, filepath, row=None):
        if not filepath:
            return
        if not messagebox.askyesno("Confirm Delete", f"Move to Recycle Bin?\n\n{filepath}"):
            return
        ok, msg = self.analyzer.delete_file(filepath)
        if ok:
            if row is not None and row.winfo_exists():
                row.destroy()
            messagebox.showinfo("Delete Complete", msg)
        else:
            messagebox.showerror("Delete Failed", msg)

    def _confirm_uninstall(self, app):
        if not app or not app.get("uninstall"):
            messagebox.showerror("Uninstall Failed", "No uninstall command was found for this app.")
            return
        if not messagebox.askyesno("Confirm Uninstall", f"Launch uninstaller for '{app.get('name', 'this app')}'?"):
            return
        ok, msg = self.analyzer.uninstall_program(app["uninstall"])
        if ok:
            messagebox.showinfo("Uninstaller Launched", msg)
        else:
            messagebox.showerror("Uninstall Failed", msg)

    def _parse_size_mb(self, label):
        if not label:
            return 100
        text = label.strip().upper()
        try:
            if text.endswith("GB"):
                return int(text[:-2].strip()) * 1024
            if text.endswith("MB"):
                return int(text[:-2].strip())
            return int(text)
        except ValueError:
            return 100

    def _choose_dup_path(self):
        path = filedialog.askdirectory(title="Select Folder for Duplicate Scan")
        if path:
            self.dup_path_var.set(path)

    def _choose_lf_path(self):
        path = filedialog.askdirectory(title="Select Folder to Scan")
        if path:
            self.lf_path_var.set(path)
            self._update_lf_hero()

    def _update_lf_hero(self):
        if not hasattr(self, "lf_path_var"):
            return
        path = self.lf_path_var.get()
        drive_root = os.path.splitdrive(path)[0] + "\\" if path else ""
        free_text = "Free space unknown"
        percent = 0
        if drive_root and os.path.exists(drive_root):
            try:
                usage = psutil.disk_usage(drive_root)
                percent = usage.percent
                free_text = f"{format_size(usage.free)} free on {drive_root}"
            except Exception:
                pass

        if hasattr(self, "lf_hero_title") and self.lf_hero_title.winfo_exists():
            self.lf_hero_title.configure(text=f"Scan Path: {path}")
        if hasattr(self, "lf_hero_subtitle") and self.lf_hero_subtitle.winfo_exists():
            self.lf_hero_subtitle.configure(text=free_text)
        if hasattr(self, "lf_hero_bar") and self.lf_hero_bar.winfo_exists():
            self.lf_hero_bar.set(percent / 100 if percent else 0)

    def _update_lf_scan_label(self, _=None):
        if hasattr(self, "lf_scan_btn") and self.lf_scan_btn.winfo_exists():
            self.lf_scan_btn.configure(text=f"🔍 Scan for Files > {self.lf_size_var.get()}")

    # --- Views ---

    def show_dashboard(self):
        self.set_active_nav("dashboard")
        self.clear_main()
        
        # Greeting
        hour = datetime.datetime.now().hour
        greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 18 else "Good Evening"
        
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(header, text=f"{greeting}, User", font=("Segoe UI", 32, "bold"), text_color=THEME["text"]).pack(side="left")
        
        # Drive Selector
        drive_frame = ctk.CTkFrame(header, fg_color=THEME["bg_card"], corner_radius=10)
        drive_frame.pack(side="right")
        ctk.CTkLabel(drive_frame, text="Monitor:", font=("Segoe UI", 12), text_color=THEME["text_muted"]).pack(side="left", padx=10)
        self.drive_menu = ctk.CTkOptionMenu(drive_frame, values=self.drives, variable=self.selected_drive, 
                                            fg_color=THEME["bg_sidebar"], button_color=THEME["primary"],
                                            command=self.update_dashboard_stats)
        self.drive_menu.pack(side="left", padx=(0, 10), pady=10)

        # Stats Grid
        self.stats_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_grid.pack(fill="x")
        self.stats_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        
        self.cpu_card = HealthCard(self.stats_grid, "CPU Load", "🧠", "0%", color=THEME["primary"])
        self.cpu_card.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        
        self.ram_card = HealthCard(self.stats_grid, "Memory", "💾", "0%", color="#845ec2")
        self.ram_card.grid(row=0, column=1, padx=7, sticky="ew")
        
        self.disk_card = HealthCard(self.stats_grid, "Storage", "💿", "0%", color="#ffc75f")
        self.disk_card.grid(row=0, column=2, padx=(15, 0), sticky="ew")
        
        # Quick Actions Row
        actions = ctk.CTkFrame(self.main_container, fg_color="transparent")
        actions.pack(fill="x", pady=30)
        
        ctk.CTkLabel(actions, text="Quick Actions", font=("Segoe UI", 16, "bold"), text_color=THEME["text_muted"]).pack(anchor="w", pady=(0, 10))
        
        action_grid = ctk.CTkFrame(actions, fg_color="transparent")
        action_grid.pack(fill="x")
        action_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="b")
        
        self._create_action_card(action_grid, 0, "🧹 Quick Clean", "Scan & Clean Junk", THEME["primary"], self.show_cleaner)
        self._create_action_card(action_grid, 1, "🔍 Large Files", "Free up Space", "#845ec2", lambda: self.show_tools() or self.tools_tabs.set("Large Files"))
        self._create_action_card(action_grid, 2, "🚀 Boost Startup", "Improve Boot Time", "#ffc75f", lambda: self.show_tools() or self.tools_tabs.set("Startup"))

        self.update_dashboard_stats()

    def _create_action_card(self, parent, col, title, subtitle, color, command):
        card = ctk.CTkButton(parent, text="", height=80, fg_color=THEME["bg_card"], 
                             hover_color="#1f2b4d", corner_radius=15, border_width=1, 
                             border_color="#252a40", command=command)
        card.grid(row=0, column=col, sticky="ew", padx=10)
        
        # overlay labels on button (container logic is tricky with buttons, so using master=parent and placing over)
        # Actually safer to make the button the container content? No, CTkButton text alignment is limited.
        # Let's simple button text for now or complex Frame with bind.
        # Going with simple styling for stability.
        card.configure(text=f"{title}\n{subtitle}", font=("Segoe UI", 16, "bold"))
        
    def update_dashboard_stats(self, _=None):
        if not hasattr(self, 'cpu_card') or not self.cpu_card.winfo_exists():
            return

        try:
            # CPU
            cpu = psutil.cpu_percent()
            self.cpu_card.update_data(f"{cpu}%", cpu / 100)

            # RAM
            ram = psutil.virtual_memory()
            self.ram_card.update_data(f"{ram.percent}%", ram.percent / 100)

            # Disk
            drive = self.selected_drive.get()
            if os.path.exists(drive):
                disk = psutil.disk_usage(drive)
                self.disk_card.update_data(f"{disk.percent}% Used", disk.percent / 100)
                self.disk_card.title_label.configure(text=f"Storage ({drive})")
        except Exception:
            pass
        finally:
            if hasattr(self, 'cpu_card') and self.cpu_card.winfo_exists():
                self.after(2000, self.update_dashboard_stats)

    def show_cleaner(self):
        self.set_active_nav("cleaner")
        self.clear_main()
        
        ctk.CTkLabel(self.main_container, text="System Cleaner", font=("Segoe UI", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Two columns: Options | Log
        content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content.pack(fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        
        # Left: Options
        options_panel = ctk.CTkFrame(content, fg_color=THEME["bg_card"], corner_radius=15)
        options_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(options_panel, text="Scan Options", font=("Segoe UI", 16, "bold")).pack(padx=20, pady=20, anchor="w")
        
        self.check_vars = {}
        for cat in self.scanner.categories.keys():
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(options_panel, text=cat, variable=var, 
                                 font=("Segoe UI", 14), text_color=THEME["text"],
                                 fg_color=THEME["primary"], hover_color=THEME["primary_hover"])
            cb.pack(pady=10,padx=20, anchor="w")
            self.check_vars[cat] = var

        controls = ctk.CTkFrame(options_panel, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(10, 0))
        ctk.CTkButton(
            controls,
            text="Select All",
            height=32,
            fg_color=THEME["bg_sidebar"],
            hover_color="#1f2b4d",
            command=self._select_all_options
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(
            controls,
            text="Select None",
            height=32,
            fg_color=THEME["bg_sidebar"],
            hover_color="#1f2b4d",
            command=self._select_none_options
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))
            
        # Safe Mode Switch
        ctk.CTkFrame(options_panel, height=2, fg_color="#252a40").pack(fill="x", pady=20, padx=20)
        
        self.safe_mode = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(options_panel, text="Safe Mode (Recycle Bin)", variable=self.safe_mode, 
                      progress_color=THEME["success"], button_color="white").pack(padx=20, anchor="w")
        
        self.scan_btn = ctk.CTkButton(options_panel, text="Analyze Now", height=45, corner_radius=10, 
                                      fg_color=THEME["primary"], font=("Segoe UI", 15, "bold"),
                                      command=self.start_scan)
        self.scan_btn.pack(fill="x", padx=20, pady=(30, 10))

        self.scan_progress = ctk.CTkProgressBar(options_panel, height=8, progress_color=THEME["primary"])
        self.scan_progress.set(0)
        self.scan_progress.pack(fill="x", padx=20, pady=(0, 6))
        self.scan_status = ctk.CTkLabel(options_panel, text="Ready to scan", text_color=THEME["text_muted"])
        self.scan_status.pack(padx=20, anchor="w", pady=(0, 10))
        
        # Right: Results
        results_panel = ctk.CTkFrame(content, fg_color=THEME["bg_card"], corner_radius=15)
        results_panel.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(results_panel, text="Activity Log", font=("Segoe UI", 16, "bold")).pack(padx=20, pady=20, anchor="w")
        
        self.log_box = ctk.CTkTextbox(results_panel, font=("Consolas", 12), fg_color="#1a1a2e", text_color=THEME["text_muted"])
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.clean_btn = ctk.CTkButton(results_panel, text="🧹 Run Cleaner", height=50, corner_radius=10,
                                      fg_color=THEME["danger"], font=("Segoe UI", 16, "bold"), state="disabled",
                                      command=self.start_clean)
        self.clean_btn.pack(fill="x", padx=20, pady=20)

    def start_scan(self):
        if self.is_scanning:
            return

        selected = [k for k, v in self.check_vars.items() if v.get()]
        if not selected:
            messagebox.showinfo("Nothing Selected", "Select at least one scan category.")
            return

        self.is_scanning = True
        self.scan_btn.configure(state="disabled")
        self.clean_btn.configure(state="disabled")
        self.scan_progress.set(0)
        self._set_scan_status("Scanning...")

        self.log_box.delete("0.0", "end")
        self._append_log("--- Scanning System ---")
        
        threading.Thread(target=self._scan_thread, args=(selected,), daemon=True).start()

    def _scan_thread(self, selected):
        def _progress(idx, total, cat, _data):
            if total <= 0:
                return
            self.after(0, lambda: self._set_scan_status(f"Scanning {cat} ({idx}/{total})", idx / total))

        self.scan_results = self.scanner.scan_selected(selected, progress_cb=_progress)

        total_size = 0
        total_files = 0
        report_lines = []
        errors = []

        for cat, data in self.scan_results.items():
            size = data.get('size', 0)
            files = data.get('files', [])
            total_size += size
            total_files += len(files)
            report_lines.append(f"[{cat}] Found {len(files)} items ({format_size(size)})")
            if data.get('error'):
                errors.append(f"[{cat}] {data.get('error')}")

        report = "\n".join(report_lines)
        self.after(0, lambda: self._on_scan_finish(report, total_size, total_files, errors))

    def _on_scan_finish(self, report, total_size, total_files, errors):
        self.is_scanning = False
        self._safe_config(self.scan_btn, state="normal")

        self._append_log(report)
        self._append_log(f"\nTotal Junk: {format_size(total_size)} ({total_files} items)")

        if errors:
            self._append_log("\nWarnings:")
            for err in errors:
                self._append_log(f"- {err}")

        if total_size > 0:
            self._safe_config(self.clean_btn, state="normal")
            self._set_scan_status("Scan complete", 1)
        else:
            self._safe_config(self.clean_btn, state="disabled")
            self._set_scan_status("No junk found", 0)

    def start_clean(self):
        if self.is_cleaning:
            return

        if not self.scan_results:
            messagebox.showinfo("Nothing to Clean", "Run a scan first.")
            return

        total_size = sum(d.get('size', 0) for d in self.scan_results.values())
        total_files = sum(len(d.get('files', [])) for d in self.scan_results.values())
        if total_size <= 0:
            messagebox.showinfo("Nothing to Clean", "No junk was found in the last scan.")
            return

        confirm = messagebox.askyesno(
            "Confirm Clean",
            f"Clean {total_files} items ({format_size(total_size)})?"
        )
        if not confirm:
            return

        self.is_cleaning = True
        self.clean_btn.configure(state="disabled")
        self.scan_btn.configure(state="disabled")
        self._set_scan_status("Cleaning...", 0)
        self._append_log("\n--- Cleaning ---")

        threading.Thread(target=self._clean_thread, daemon=True).start()

    def _clean_thread(self):
        ok, msg = self.cleaner.run_safety_checks()
        total_cleaned = 0
        total_items = 0
        errors = []
        use_recycle = self.safe_mode.get()

        if not ok:
            self.after(0, lambda: self._append_log(f"Restore point warning: {msg}"))

        total_cats = len(self.scan_results)
        for idx, (cat, data) in enumerate(self.scan_results.items(), start=1):
            count, size, errs = self.cleaner.clean_category(cat, data, use_recycle)
            total_items += count
            total_cleaned += size
            if errs:
                errors.extend(errs)

            self.after(0, lambda c=cat, ct=count, sz=size: self._append_log(
                f"[{c}] Cleaned {ct} items ({format_size(sz)})"
            ))
            if total_cats:
                self.after(0, lambda i=idx, t=total_cats, c=cat: self._set_scan_status(
                    f"Cleaning {c} ({i}/{t})", i / t
                ))

        self.after(0, lambda: self._on_clean_finish(total_items, total_cleaned, errors))

    def _on_clean_finish(self, total_items, total_cleaned, errors):
        self.is_cleaning = False
        self._safe_config(self.scan_btn, state="normal")
        self._safe_config(self.clean_btn, state="disabled")
        self._set_scan_status("Cleaning complete", 1)
        self._append_log(f"\nDone! Freed {format_size(total_cleaned)} ({total_items} items).")
        self.scan_results = {}

        if errors:
            self._append_log("\nErrors:")
            for err in errors:
                self._append_log(f"- {err}")

    def show_tools(self):
        self.set_active_nav("tools")
        self.clear_main()
        
        ctk.CTkLabel(self.main_container, text="Power Tools", font=("Segoe UI", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Tools Grid
        grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_rowconfigure(0, weight=1)
        
        self.tools_tabs = ctk.CTkTabview(grid, fg_color=THEME["bg_card"], corner_radius=15, 
                                         segmented_button_fg_color=THEME["bg_main"],
                                         segmented_button_selected_color=THEME["primary"],
                                         text_color=THEME["text"])
        self.tools_tabs.pack(fill="both", expand=True)
        
        self.tools_tabs.add("Large Files")
        self.tools_tabs.add("Startup")
        self.tools_tabs.add("Duplicates")
        self.tools_tabs.add("Uninstaller")
        
        self._setup_large_files(self.tools_tabs.tab("Large Files"))
        self._setup_startup(self.tools_tabs.tab("Startup"))
        self._setup_duplicates(self.tools_tabs.tab("Duplicates"))
        self._setup_uninstaller(self.tools_tabs.tab("Uninstaller"))

    def _setup_startup(self, parent):
        # Header
        ctk.CTkLabel(parent, text="Manage programs that start with Windows", text_color=THEME["text_muted"]).pack(pady=(10, 5))
        
        # Action
        ctk.CTkButton(parent, text="🔄 Refresh Startup List", height=40, font=("Segoe UI", 14, "bold"),
                      command=self._refresh_startup, fg_color=THEME["primary"]).pack(fill="x", pady=10)
                      
        self.startup_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.startup_list.pack(fill="both", expand=True)
        self._refresh_startup()

    def _refresh_startup(self):
        for w in self.startup_list.winfo_children(): w.destroy()
        items = self.analyzer.get_startup_items()
        
        if not items:
            self._show_empty_state(self.startup_list, "No Startup Items", "Your boot sequence is clean.")
            return
            
        # Header
        header = ctk.CTkFrame(self.startup_list, height=30, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Program Name", font=("Segoe UI", 12, "bold"), text_color=THEME["text_muted"]).pack(side="left", padx=15)

        for item in items:
            row = ctk.CTkFrame(self.startup_list, fg_color=THEME["bg_card"], corner_radius=8)
            row.pack(fill="x", pady=4, padx=5)
            
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(info, text=item['name'], font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=item['path'], font=("Segoe UI", 11), text_color=THEME["text_muted"], anchor="w").pack(fill="x")
            
            ctk.CTkButton(row, text="Disable", width=80, fg_color=THEME["danger"], height=30,
                          command=lambda i=item: self._delete_startup(i)).pack(side="right", padx=15)

    def _delete_startup(self, item):
        if messagebox.askyesno("Confirm", f"Remove '{item['name']}'?"):
             ok, msg = self.analyzer.remove_startup_item(item)
             if ok:
                 messagebox.showinfo("Startup Updated", msg)
                 self._refresh_startup()
             else:
                 messagebox.showerror("Failed to Remove", msg)

    def _setup_duplicates(self, parent):
        ctk.CTkLabel(parent, text="Scan a folder for identical files", text_color=THEME["text_muted"]).pack(pady=10)
        default_root = os.environ.get('USERPROFILE') or os.path.expanduser("~")
        default_pics = os.path.join(default_root, 'Pictures')
        if not os.path.isdir(default_pics):
            default_pics = default_root

        self.dup_path_var = ctk.StringVar(value=default_pics)

        path_row = ctk.CTkFrame(parent, fg_color="transparent")
        path_row.pack(fill="x", padx=10)
        ctk.CTkLabel(path_row, text="Folder:", text_color=THEME["text_muted"]).pack(side="left")
        ctk.CTkLabel(path_row, textvariable=self.dup_path_var, anchor="w").pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(path_row, text="Change", width=90, fg_color=THEME["bg_sidebar"],
                      hover_color="#1f2b4d", command=self._choose_dup_path).pack(side="right")

        self.dup_scan_btn = ctk.CTkButton(parent, text="🔍 Scan Duplicates", height=40, font=("Segoe UI", 14, "bold"),
                                          command=self._scan_duplicates, fg_color=THEME["primary"])
        self.dup_scan_btn.pack(fill="x", pady=10)
                      
        self.dup_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.dup_list.pack(fill="both", expand=True)
        self._show_empty_state(self.dup_list, "Find Duplicates", "Choose a folder to scan for duplicates.")

    def _scan_duplicates(self):
        if self.is_scanning_dupes:
            return

        scan_path = self.dup_path_var.get()
        if not scan_path or not os.path.isdir(scan_path):
            messagebox.showerror("Invalid Folder", "Select a valid folder to scan.")
            return

        self.is_scanning_dupes = True
        self.dup_scan_btn.configure(state="disabled", text="Scanning...")
        self._show_empty_state(self.dup_list, "Scanning...", "Hashing files to find matches...")
        threading.Thread(target=self._dup_scan_thread, args=(scan_path,), daemon=True).start()
    
    def _dup_scan_thread(self, scan_path):
        dupes = self.analyzer.find_duplicates(scan_path)
        self.after(0, lambda: self._on_dup_scan_finish(dupes))

    def _on_dup_scan_finish(self, dupes):
        self.is_scanning_dupes = False
        self._safe_config(self.dup_scan_btn, state="normal", text="🔍 Scan Duplicates")
        self._show_duplicates(dupes)

    def _show_duplicates(self, dupes):
        for w in self.dup_list.winfo_children():
            w.destroy()
        if not dupes:
            self._show_empty_state(self.dup_list, "No Duplicates", "Your files are unique!")
            return

        for _, paths in dupes.items():
            group = ctk.CTkFrame(self.dup_list, fg_color=THEME["bg_card"], corner_radius=10)
            group.pack(fill="x", pady=8, padx=5)

            header = ctk.CTkFrame(group, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(
                header,
                text=f"Match Found ({len(paths)} copies)",
                font=("Segoe UI", 12, "bold"),
                text_color=THEME["warning"]
            ).pack(side="left")

            for p in paths:
                row = ctk.CTkFrame(group, fg_color="transparent")
                row.pack(fill="x", pady=2)

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=10, pady=6)
                ctk.CTkLabel(info, text=os.path.basename(p), font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
                ctk.CTkLabel(info, text=os.path.dirname(p), text_color=THEME["text_muted"], anchor="w").pack(fill="x")

                ctk.CTkButton(
                    row,
                    text="Delete",
                    width=70,
                    fg_color=THEME["danger"],
                    height=24,
                    command=lambda f=p, r=row: self._confirm_and_delete(f, r)
                ).pack(side="right", padx=10)

    def _setup_large_files(self, parent):
        # 1. Drive Stats Hero
        hero = ctk.CTkFrame(parent, fg_color=THEME["bg_card"], corner_radius=10)
        hero.pack(fill="x", pady=(0, 10))

        self.lf_path_var = ctk.StringVar(value=self.selected_drive.get())

        self.lf_hero_title = ctk.CTkLabel(hero, text="Scan Path:", font=("Segoe UI", 16, "bold"))
        self.lf_hero_title.pack(anchor="w", padx=15, pady=(10, 0))
        self.lf_hero_subtitle = ctk.CTkLabel(hero, text="", text_color=THEME["text_muted"])
        self.lf_hero_subtitle.pack(anchor="w", padx=15, pady=(0, 5))

        self.lf_hero_bar = ctk.CTkProgressBar(hero, height=10, progress_color=THEME["primary"])
        self.lf_hero_bar.set(0)
        self.lf_hero_bar.pack(fill="x", padx=15, pady=(0, 15))
        self._update_lf_hero()

        # 2. Action Area
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", pady=10)
        
        path_row = ctk.CTkFrame(action_frame, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(path_row, text="Scan path:", text_color=THEME["text_muted"]).pack(side="left")
        ctk.CTkLabel(path_row, textvariable=self.lf_path_var, anchor="w").pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(path_row, text="Change", width=90, fg_color=THEME["bg_sidebar"],
                      hover_color="#1f2b4d", command=self._choose_lf_path).pack(side="right")

        size_row = ctk.CTkFrame(action_frame, fg_color="transparent")
        size_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(size_row, text="Minimum size:", text_color=THEME["text_muted"]).pack(side="left")
        self.lf_size_var = ctk.StringVar(value="100 MB")
        ctk.CTkOptionMenu(
            size_row,
            values=["100 MB", "250 MB", "500 MB", "1 GB"],
            variable=self.lf_size_var,
            fg_color=THEME["bg_sidebar"],
            button_color=THEME["primary"],
            command=self._update_lf_scan_label
        ).pack(side="left", padx=8)

        self.lf_scan_btn = ctk.CTkButton(
            action_frame,
            text="🔍 Scan for Files > 100 MB",
            height=50,
            fg_color=THEME["primary"],
            font=("Segoe UI", 15, "bold"),
            command=self._scan_large_files
        )
        self.lf_scan_btn.pack(fill="x")

        # 3. Results Area
        self.lf_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.lf_list.pack(fill="both", expand=True)
        
        # Empty State
        self._show_empty_state(self.lf_list, "Ready to Scan", "Click the button above to analyze the selected path.")

    def _show_empty_state(self, parent, title, subtitle):
        for w in parent.winfo_children(): w.destroy()
        
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(expand=True, pady=40)
        
        ctk.CTkLabel(container, text="📂", font=("Segoe UI", 48)).pack(pady=(0, 10))
        ctk.CTkLabel(container, text=title, font=("Segoe UI", 18, "bold"), text_color=THEME["text_muted"]).pack()
        ctk.CTkLabel(container, text=subtitle, text_color=THEME["text_muted"]).pack()

    def _scan_large_files(self):
        if self.is_scanning_large:
            return

        scan_path = self.lf_path_var.get()
        if not scan_path or not os.path.exists(scan_path):
            messagebox.showerror("Invalid Path", "Select a valid folder or drive to scan.")
            return

        self.is_scanning_large = True
        self.lf_scan_btn.configure(state="disabled", text="Scanning...")
        self._show_empty_state(self.lf_list, "Scanning...", "Please wait while we analyze the selected path.")
        min_size_mb = self._parse_size_mb(self.lf_size_var.get())
        threading.Thread(target=self._full_large_file_scan, args=(scan_path, min_size_mb), daemon=True).start()

    def _full_large_file_scan(self, scan_path, min_size_mb):
        files = self.analyzer.find_large_files(scan_path, min_size_mb=min_size_mb)
        self.after(0, lambda: self._on_large_files_finish(files))

    def _on_large_files_finish(self, files):
        self.is_scanning_large = False
        self._safe_config(self.lf_scan_btn, state="normal")
        self._update_lf_scan_label()
        self._show_large_files(files)

    def _show_large_files(self, files):
        for w in self.lf_list.winfo_children(): w.destroy()
        if not files:
            self._show_empty_state(self.lf_list, "No Large Files Found", "No files exceeded the selected threshold.")
            return
             
        # Header
        header = ctk.CTkFrame(self.lf_list, height=30, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Size", width=80, anchor="w", font=("Segoe UI", 12, "bold"), text_color=THEME["text_muted"]).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="File", anchor="w", font=("Segoe UI", 12, "bold"), text_color=THEME["text_muted"]).pack(side="left", padx=10)

        for path, size in files[:50]:
            row = ctk.CTkFrame(self.lf_list, fg_color=THEME["bg_card"], corner_radius=8)
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row, text=f"{format_size(size)}", font=("Consolas", 12, "bold"), text_color=THEME["warning"], width=80).pack(side="left", padx=10, pady=10)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, pady=6)
            ctk.CTkLabel(info, text=os.path.basename(path), anchor="w", font=("Segoe UI", 12, "bold")).pack(fill="x")
            ctk.CTkLabel(info, text=os.path.dirname(path), anchor="w", text_color=THEME["text_muted"]).pack(fill="x")
            
            ctk.CTkButton(row, text="Delete", width=60, height=30, fg_color=THEME["danger"], 
                          hover_color="#b91c1c", font=("Segoe UI", 12),
                          command=lambda p=path, r=row: self._confirm_and_delete(p, r)).pack(side="right", padx=10)

    def _setup_uninstaller(self, parent):
        ctk.CTkLabel(parent, text="Manage Installed Applications", text_color=THEME["text_muted"]).pack(pady=(10, 5))
        
        self.app_scan_btn = ctk.CTkButton(parent, text="🔍 Scan Installed Apps", height=40, font=("Segoe UI", 14, "bold"),
                                          command=self._load_apps, fg_color=THEME["primary"])
        self.app_scan_btn.pack(fill="x", pady=10)
                      
        self.app_list = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.app_list.pack(fill="both", expand=True)
        self._show_empty_state(self.app_list, "Uninstaller", "Scan to list installed software.")

    def _load_apps(self):
        if self.is_loading_apps:
            return

        self.is_loading_apps = True
        self._safe_config(self.app_scan_btn, state="disabled", text="Scanning...")
        self._show_empty_state(self.app_list, "Scanning...", "Reading registry for installed programs...")
        threading.Thread(target=self._load_apps_thread, daemon=True).start()

    def _load_apps_thread(self):
        apps = self.analyzer.get_installed_programs()
        self.after(0, lambda: self._on_apps_loaded(apps))

    def _on_apps_loaded(self, apps):
        self.is_loading_apps = False
        self._safe_config(self.app_scan_btn, state="normal", text="🔍 Scan Installed Apps")
        self._show_apps(apps)

    def _show_apps(self, apps):
        for w in self.app_list.winfo_children(): w.destroy()
        
        if not apps:
            self._show_empty_state(self.app_list, "No Apps Found", "Registry scan returned nothing.")
            return

        # Header
        header = ctk.CTkFrame(self.app_list, height=30, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text=f"Application ({len(apps)} found)", font=("Segoe UI", 12, "bold"), text_color=THEME["text_muted"]).pack(side="left", padx=15)

        for app in apps:
            row = ctk.CTkFrame(self.app_list, fg_color=THEME["bg_card"], corner_radius=8)
            row.pack(fill="x", pady=4, padx=5)
            
            ctk.CTkLabel(row, text=app['name'], anchor="w", font=("Segoe UI", 13, "bold")).pack(side="left", padx=15, fill="x", expand=True)
            ctk.CTkButton(row, text="Uninstall", width=80, fg_color=THEME["danger"], height=30,
                          command=lambda a=app: self._confirm_uninstall(a)).pack(side="right", padx=15, pady=5)

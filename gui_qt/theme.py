from pathlib import Path

# Elevated 'Comfy & Trusty' Palette
THEME = {
    # Backgrounds & Sibling Panels
    "bg_main": "#FAF6F0",        # Deepened warmth for main canvas
    "bg_sidebar": "#F3EBE1",     # Sidebar keeps visual separation
    "bg_panel": "#FFFFFF",       # Cards are now pure white for contrast
    "bg_hover": "#F5EFE8",       # Softer interactive hover fill
    
    # Primary Interactive Colors
    "primary": "#8B5A3C",        # Richer, deeper brand color
    "primary_hover": "#764A31",  # Darker active state
    "primary_disabled": "#D0BBAA",
    "accent": "#C99161",         # Used for highlights or illustrations
    
    # Typography
    "text": "#2D241D",           # Nearly black for maximal contrast
    "text_muted": "#756254",     # Richer mid-tone for secondary text
    "text_inverse": "#FFFFFF",   # Text on primary buttons
    
    # Status Indicators
    "success": "#7A9E66",        # Desaturated natural green
    "warning": "#C8866B",        # Warm terracotta red
    "danger": "#BD6050",         # Firmer error red
    
    # Borders & Dividers
    "border_light": "#EFE6DB",   # Subtle outlines
    "border_dark": "#DCD0C3",    # Harder structural lines
}

FONT_BODY = "Quattrocento Sans"
FONT_DISPLAY = "Hedvig Letters Sans"

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"

def asset_path(name: str) -> str:
    return str(ASSET_DIR / name)

def get_stylesheet() -> str:
    return f"""
    /* ==== GLOBAL DEFAULTS ==== */
    QMainWindow {{
        background: {THEME["bg_main"]};
    }}
    QWidget {{
        font-family: "{FONT_BODY}", "Segoe UI", sans-serif;
        color: {THEME["text"]};
        font-size: 13px;
    }}
    
    /* ==== LAYOUT PANELS ==== */
    QStackedWidget#AppBody {{
        background: {THEME["bg_main"]};
    }}
    QFrame#Sidebar {{
        background: {THEME["bg_sidebar"]};
        border-right: 1px solid {THEME["border_light"]};
    }}
    
    /* ==== TYPOGRAPHY HIERARCHY ==== */
    QLabel#Muted {{
        color: {THEME["text_muted"]};
        font-size: 12px;
    }}
    QLabel#Tagline {{
        color: {THEME["text_muted"]};
        font-size: 11px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    
    /* ==== STATUS CHIPS ==== */
    QLabel#StatusChip {{
        background: {THEME["bg_main"]};
        border: 1px solid {THEME["border_light"]};
        border-radius: 12px;
        padding: 4px 12px;
        color: {THEME["text_muted"]};
        font-weight: 500;
        font-size: 11px;
    }}
    QLabel#StatusChip[variant="success"] {{
        color: {THEME["success"]};
        border-color: rgba(122,158,102, 0.3);
        background: rgba(122,158,102, 0.05);
    }}
    QLabel#StatusChip[variant="warning"] {{
        color: {THEME["warning"]};
        border-color: rgba(200,134,107, 0.3);
        background: rgba(200,134,107, 0.05);
    }}
    
    /* ==== CARDS (Glass/Soft UI) ==== */
    QFrame#Card {{
        background: {THEME["bg_panel"]};
        border-radius: 16px;
        /* The drop shadow is handled programmatically via QGraphicsDropShadowEffect */
    }}
    QFrame#HeroCard {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #FFFFFF,
            stop:1 #FAF5F0
        );
        border-radius: 20px;
        border: 1px solid {THEME["border_light"]};
    }}
    QLabel#HeroPill {{
        background: {THEME["bg_sidebar"]};
        border: 1px solid {THEME["border_dark"]};
        border-radius: 14px;
        padding: 4px 12px;
        color: {THEME["text"]};
        font-weight: 600;
        font-size: 12px;
    }}
    
    /* ==== NAVIGATION & BUTTONS ==== */
    QPushButton#NavButton {{
        background: transparent;
        color: {THEME["text_muted"]};
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton#NavButton:hover {{
        background: {THEME["bg_hover"]};
        color: {THEME["text"]};
    }}
    QPushButton#NavButton:checked {{
        background: #FFFFFF;
        color: {THEME["primary"]};
        font-weight: 600;
        /* Emulate a soft floating active state */
        border: 1px solid {THEME["border_light"]};
    }}
    
    QPushButton#CardButton {{
        background: {THEME["bg_panel"]};
        color: {THEME["text"]};
        border: 1px solid {THEME["border_light"]};
        border-radius: 12px;
        text-align: left;
        padding: 16px;
    }}
    QPushButton#CardButton:hover {{
        border: 1px solid {THEME["primary"]};
        background: {THEME["bg_hover"]};
    }}
    QPushButton#CardButton:pressed {{
        background: {THEME["border_light"]};
    }}
    
    QPushButton#Primary, QPushButton#PrimaryPill {{
        background: {THEME["primary"]};
        color: {THEME["text_inverse"]};
        border: none;
        padding: 8px 16px;
        font-weight: 600;
    }}
    QPushButton#Primary {{
        border-radius: 8px;
    }}
    QPushButton#PrimaryPill {{
        border-radius: 999px;
        padding: 12px 24px;
    }}
    QPushButton#Primary:hover, QPushButton#PrimaryPill:hover {{
        background: {THEME["primary_hover"]};
    }}
    QPushButton#Primary:pressed, QPushButton#PrimaryPill:pressed {{
        background: #5E3D28;
    }}
    QPushButton#Primary:disabled, QPushButton#PrimaryPill:disabled {{
        background: {THEME["primary_disabled"]};
        color: #FFFFFF;
    }}
    
    QPushButton#Danger {{
        background: {THEME["bg_panel"]};
        color: {THEME["danger"]};
        border: 1px solid rgba(189,96,80,0.4);
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 500;
    }}
    QPushButton#Danger:hover {{
        background: rgba(189,96,80,0.08);
        border-color: {THEME["danger"]};
    }}
    QPushButton#Danger:pressed {{
        background: rgba(189,96,80,0.15);
    }}
    
    QPushButton#Ghost {{
        background: transparent;
        color: {THEME["text"]};
        border: 1px solid {THEME["border_dark"]};
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 500;
    }}
    QPushButton#Ghost:hover {{
        background: {THEME["bg_hover"]};
        border-color: {THEME["text_muted"]};
    }}
    
    /* ==== INPUTS ==== */
    QComboBox, QLineEdit {{
        background: {THEME["bg_panel"]};
        color: {THEME["text"]};
        border: 1px solid {THEME["border_dark"]};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    QComboBox:hover, QLineEdit:hover {{
        border: 1px solid {THEME["primary"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none; /* Can replace with a custom SVG arrow if desired */
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {THEME["text_muted"]};
        margin-right: 8px;
    }}
    
    QCheckBox {{
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {THEME["border_dark"]};
        background: {THEME["bg_panel"]};
    }}
    QCheckBox::indicator:hover {{
        border-color: {THEME["primary"]};
    }}
    QCheckBox::indicator:checked {{
        background: {THEME["primary"]};
        border: 1px solid {THEME["primary"]};
        /* A simple CSS checkmark replacement */
        image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSI0IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCA2TDEwIDE4TDUgMTMiPjwvcGF0aD48L3N2Zz4=);
    }}
    
    /* ==== DATA VIEWS (Trees & Tables) ==== */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QPlainTextEdit, QTreeWidget, QTableWidget {{
        background: {THEME["bg_panel"]};
        color: {THEME["text"]};
        border: 1px solid {THEME["border_light"]};
        border-radius: 8px;
        padding: 4px;
    }}
    
    QTreeWidget, QTableWidget {{
        alternate-background-color: {THEME["bg_main"]};
        gridline-color: transparent; /* Remove harsh table grids */
        selection-background-color: {THEME["bg_hover"]};
        selection-color: {THEME["text"]};
    }}
    QTreeWidget::item, QTableWidget::item {{
        border-bottom: 1px solid {THEME["bg_main"]}; /* Soft dividers */
        padding: 4px;
    }}
    QTreeWidget::item:selected, QTableWidget::item:selected {{
        background: {THEME["bg_hover"]};
        color: {THEME["primary"]};
        font-weight: 500;
    }}
    
    QHeaderView::section {{
        background: {THEME["bg_sidebar"]};
        color: {THEME["text_muted"]};
        padding: 8px 12px;
        border: none;
        font-variant: small-caps;
        font-weight: 600;
        font-size: 11px;
        border-bottom: 1px solid {THEME["border_dark"]};
    }}
    
    /* ==== PROGRESS BARS ==== */
    QProgressBar {{
        background: {THEME["bg_sidebar"]};
        border: none;
        border-radius: 4px; /* Thinner line */
        text-align: right;
        color: transparent; /* Hide text inside bar, handled externally */
        max-height: 8px; 
    }}
    QProgressBar::chunk {{
        background: {THEME["primary"]};
        border-radius: 4px;
    }}
    
    /* ==== TABS ==== */
    QTabWidget::pane {{
        border: 1px solid {THEME["border_light"]};
        border-radius: 12px;
        background: {THEME["bg_panel"]};
        top: -1px; /* Overlap border */
    }}
    QTabBar::tab {{
        background: transparent;
        color: {THEME["text_muted"]};
        padding: 8px 16px;
        border-radius: 6px;
        margin-right: 2px;
        font-weight: 500;
    }}
    QTabBar::tab:hover {{
        background: {THEME["bg_hover"]};
        color: {THEME["text"]};
    }}
    QTabBar::tab:selected {{
        background: {THEME["bg_panel"]};
        color: {THEME["primary"]};
        border: 1px solid {THEME["border_light"]};
        border-bottom: none; /* Seamless integration with pane */
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
    }}
    
    /* ==== SCROLLBARS (Modern Overlay Style) ==== */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px; /* Thinner */
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {THEME["border_dark"]};
        border-radius: 4px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {THEME["text_muted"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
        border: none;
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {THEME["border_dark"]};
        border-radius: 4px;
        min-width: 24px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {THEME["text_muted"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
        border: none;
        width: 0px;
    }}
    
    /* ==== POPOVERS ==== */
    QToolTip {{
        background: {THEME["bg_panel"]};
        color: {THEME["text"]};
        border: 1px solid {THEME["border_dark"]};
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 11px;
    }}
    """

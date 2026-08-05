# Central stylesheet for AutoSub. Widgets are styled by object name.
# ACCENT is exported for use in QPainter (background).
ACCENT = "#4f46e5"
ACCENT_LIGHT = "#818cf8"

MODERN_DARK = f"""
/* ===== GLOBAL ===== */
QWidget {{
    background: transparent;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Inter', Roboto, Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
}}

/* ===== PANEL CARD ===== */
QFrame#panel {{
    background-color: rgba(30, 41, 59, 0.40);
    border: 1px solid #334155;
    border-radius: 16px;
}}

/* ===== SECTION LABEL ===== */
QLabel#sectionLabel {{
    font-size: 10px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 1.2px;
    padding-left: 2px;
}}

/* ===== HEADER ===== */
QFrame#logoBadge {{
    background-color: transparent;
    border-radius: 10px;
}}

QLabel#appTitle {{
    font-size: 18px;
    font-weight: 700;
    color: #f8fafc;
}}

QLabel#tagline {{
    font-size: 12px;
    color: #64748b;
}}

/* ===== INPUTS (dropdowns) ===== */
QComboBox {{
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0 12px;
    font-size: 13px;
}}

QComboBox:hover {{
    border-color: #4f46e5;
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #94a3b8;
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #0f172a;
    color: #f1f5f9;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
    outline: none;
}}

/* ===== GENERATE BUTTON ===== */
QPushButton#generateBtn {{
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
}}

QPushButton#generateBtn:hover {{
    background-color: #6366f1;
}}

QPushButton#generateBtn:pressed {{
    background-color: #4338ca;
}}

QPushButton#generateBtn:disabled {{
    background-color: #334155;
    color: #64748b;
}}

/* ===== EXPORT FORMAT SEGMENT ===== */
QPushButton#formatBtn {{
    background-color: #334155;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
}}

QPushButton#formatBtn:hover {{
    background-color: #475569;
}}

QPushButton#formatBtnActive {{
    background-color: #4f46e5;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
}}

/* ===== EXPORT SUBTITLES (outlined) ===== */
QPushButton#exportBtn {{
    background-color: transparent;
    border: 1.5px solid #4f46e5;
    color: #818cf8;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#exportBtn:hover {{
    background-color: rgba(79, 70, 229, 0.12);
}}

QPushButton#exportBtn:pressed {{
    background-color: rgba(79, 70, 229, 0.22);
}}

QPushButton#exportBtn:disabled {{
    border-color: #334155;
    color: #64748b;
}}

/* ===== TEXT EDIT (preview) ===== */
QTextEdit {{
    background-color: #090d16;
    color: #e2e8f0;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: #4f46e5;
}}

QTextEdit:focus {{
    border-color: #334155;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: #0f172a;
    color: #94a3b8;
    border-top: 1px solid #1e293b;
    padding: 6px;
    font-size: 11px;
}}

QStatusBar::item {{
    border: none;
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #334155;
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #475569;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

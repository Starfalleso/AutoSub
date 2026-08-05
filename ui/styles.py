# Central stylesheet for AutoSub. Uses object names (e.g. #card, #generateBtn)
# to style specific widgets. ACCENT is exported for use in QPainter (background).
ACCENT = "#6366f1"
ACCENT_LIGHT = "#818cf8"
ACCENT_DARK = "#4f46e5"
ACCENT_2 = "#8b5cf6"

MODERN_DARK = f"""
/* ===== GLOBAL ===== */
QWidget {{
    background: transparent;
    color: #e4e4e7;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px;
}}

QLabel {{
    background: transparent;
}}

/* ===== CARD ===== */
QFrame#card {{
    background-color: rgba(24, 24, 29, 0.72);
    border: 1px solid rgba(63, 63, 70, 0.45);
    border-radius: 16px;
}}

/* ===== SECTION LABEL ===== */
QLabel#sectionTitle {{
    font-size: 11px;
    font-weight: 700;
    color: #71717a;
    letter-spacing: 1.2px;
    padding-left: 4px;
}}

/* ===== HEADER ===== */
QLabel#appTitle {{
    font-size: 24px;
    font-weight: 800;
    color: #fafafa;
    letter-spacing: -0.5px;
}}

QLabel#appTitleAccent {{
    font-size: 24px;
    font-weight: 800;
    color: {ACCENT_LIGHT};
    letter-spacing: -0.5px;
}}

QLabel#tagline {{
    font-size: 12px;
    color: #71717a;
    letter-spacing: 0.3px;
}}

/* ===== LOGO BADGE ===== */
QFrame#logoBadge {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {ACCENT}, stop:1 {ACCENT_2});
    border-radius: 14px;
}}

QLabel#logoText {{
    color: white;
    font-size: 16px;
    font-weight: 800;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: #27272a;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: #3f3f46;
    border-color: #52525b;
}}

QPushButton:pressed {{
    background-color: #18181b;
}}

QPushButton:disabled {{
    background-color: rgba(24, 24, 27, 0.6);
    color: #52525b;
    border-color: #27272a;
}}

QPushButton#browseBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT_LIGHT});
    border: none;
    color: white;
    font-weight: 700;
}}

QPushButton#browseBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_LIGHT}, stop:1 #a5b4fc);
}}

QPushButton#browseBtn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_DARK}, stop:1 {ACCENT});
}}

QPushButton#generateBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {ACCENT}, stop:1 {ACCENT_2});
    border: none;
    color: white;
    font-weight: 700;
    font-size: 14px;
    border-radius: 12px;
}}

QPushButton#generateBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {ACCENT_LIGHT}, stop:1 #a78bfa);
}}

QPushButton#generateBtn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {ACCENT_DARK}, stop:1 #7c3aed);
}}

QPushButton#generateBtn:disabled {{
    background: rgba(63, 63, 70, 0.6);
    color: #52525b;
}}

QPushButton#saveBtn {{
    background-color: rgba(24, 24, 27, 0.7);
    border: 1px solid #3f3f46;
    color: #e4e4e7;
    font-weight: 600;
}}

QPushButton#saveBtn:hover {{
    background-color: #27272a;
    border-color: {ACCENT};
    color: white;
}}

/* ===== COMBO BOX ===== */
QComboBox {{
    background-color: rgba(24, 24, 27, 0.8);
    color: #e4e4e7;
    border: 1px solid #3f3f46;
    border-radius: 10px;
    padding: 0 12px;
    font-size: 13px;
}}

QComboBox:hover {{
    border-color: #52525b;
}}

QComboBox:focus {{
    border-color: {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #a1a1aa;
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: #1c1c21;
    color: #e4e4e7;
    selection-background-color: {ACCENT};
    selection-color: white;
    border: 1px solid #3f3f46;
    border-radius: 10px;
    padding: 6px;
    outline: none;
}}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: rgba(39, 39, 42, 0.6);
    height: 8px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT}, stop:1 {ACCENT_2});
    border-radius: 4px;
}}

/* ===== TEXT EDIT ===== */
QTextEdit {{
    background-color: rgba(12, 12, 16, 0.85);
    color: #e4e4e7;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 12px;
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: {ACCENT};
}}

QTextEdit:focus {{
    border-color: #3f3f46;
}}

/* ===== STATUS LABELS ===== */
QLabel#status {{
    color: #a1a1aa;
    font-size: 12px;
}}

QLabel#statusSuccess {{
    color: #34d399;
    font-weight: 600;
    font-size: 12px;
}}

QLabel#statusError {{
    color: #f87171;
    font-weight: 600;
    font-size: 12px;
}}

/* ===== DROP ZONE ===== */
QFrame#dropZone {{
    border: 2px dashed #3f3f46;
    border-radius: 16px;
    background-color: rgba(24, 24, 29, 0.5);
}}

QFrame#dropZone:hover {{
    border-color: {ACCENT};
    background-color: rgba(99, 102, 241, 0.08);
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: rgba(12, 12, 16, 0.8);
    color: #71717a;
    border-top: 1px solid #18181b;
    padding: 6px;
    font-size: 12px;
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #3f3f46;
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #52525b;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ===== FILE CHIP ===== */
QFrame#fileChip {{
    background-color: rgba(99, 102, 241, 0.10);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 10px;
}}

QLabel#fileName {{
    color: #e4e4e7;
    font-size: 12px;
    font-weight: 600;
}}
"""

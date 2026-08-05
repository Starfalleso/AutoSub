"""
AutoSub - Main window.

Builds the PyQt6 UI matching the design mockup:
  * GradientBackground  - paints the dark-navy backdrop
  * TranscriptionWorker - runs faster-whisper on a background QThread
  * FileDropZone        - clickable / drag & drop file target
  * MainWindow          - layout + handlers

Flow: drop/browse a file -> click Generate Subtitles -> worker transcribes in
the background -> preview fills in -> choose format and Export.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit,
    QFileDialog, QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QDragEnterEvent, QDropEvent, QPainter,
    QLinearGradient, QRadialGradient, QColor, QMouseEvent, QIcon
)

from core.transcriber import Transcriber
from core.subtitle import (
    save, segments_to_srt, segments_to_vtt, segments_to_txt,
)
from ui.styles import MODERN_DARK, ACCENT
from paths import resource_path


# ===== Constants =========================================================
SUPPORTED_FORMATS = (
    "Video/Audio Files (*.mp4 *.avi *.mkv *.mov *.webm *.mp3 *.wav *.flac *.ogg *.m4a *.wma);;"
    "All Files (*)"
)

MODEL_OPTIONS = [
    ("tiny", "Tiny (39M)"),
    ("base", "Base (74M)"),
    ("small", "Small (244M)"),
    ("medium", "Medium (769M)"),
    ("large-v3-turbo", "Large Turbo (756M)"),
    ("large-v3", "Large V3 (1.5B)"),
]

LANGUAGE_OPTIONS = [
    ("auto", "Auto (Detect)"),
    ("en", "English"), ("es", "Spanish"), ("fr", "French"),
    ("de", "German"), ("it", "Italian"), ("pt", "Portuguese"),
    ("nl", "Dutch"), ("ru", "Russian"), ("zh", "Chinese"),
    ("ja", "Japanese"), ("ko", "Korean"), ("ar", "Arabic"),
    ("hi", "Hindi"), ("tr", "Turkish"), ("pl", "Polish"),
    ("sv", "Swedish"), ("no", "Norwegian"), ("da", "Danish"),
    ("fi", "Finnish"), ("el", "Greek"), ("cs", "Czech"),
    ("ro", "Romanian"), ("hu", "Hungarian"), ("th", "Thai"),
    ("vi", "Vietnamese"), ("id", "Indonesian"), ("ms", "Malay"),
    ("tl", "Filipino"), ("uk", "Ukrainian"),
]

COMPUTE_OPTIONS = [
    ("int8", "int8 (CPU / CUDA)"),
    ("float16", "float16 (GPU)"),
    ("float32", "float32"),
]

FORMAT_OPTIONS = ["srt", "vtt", "txt"]


# ===== Background widget =================================================
class GradientBackground(QWidget):
    """Custom widget that paints the flat dark-navy backdrop."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        vertical = QLinearGradient(0, 0, 0, self.height())
        vertical.setColorAt(0, QColor("#0b0f19"))
        vertical.setColorAt(1, QColor("#070a12"))
        painter.fillRect(self.rect(), vertical)

        accent = QColor(ACCENT)
        accent.setAlpha(22)
        radial = QRadialGradient(
            QPointF(self.width() * 0.12, 0),
            self.width() * 0.7
        )
        radial.setColorAt(0, accent)
        radial.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), radial)


# ===== Background worker thread ==========================================
class TranscriptionWorker(QThread):
    progress = pyqtSignal(float, float, str)
    finished = pyqtSignal(list, str, float)
    error = pyqtSignal(str)

    def __init__(self, audio_path: str, model_size: str, language: str, compute_type: str):
        super().__init__()
        self.audio_path = audio_path
        self.model_size = model_size
        self.language = language
        self.compute_type = compute_type

    def run(self):
        try:
            transcriber = Transcriber(model_size=self.model_size, compute_type=self.compute_type)
            transcriber.load_model()

            def on_progress(current, total, lang):
                self.progress.emit(current, total, lang)

            segments, lang, duration = transcriber.transcribe(
                self.audio_path,
                language=self.language,
                progress_callback=on_progress
            )
            self.finished.emit(segments, lang, duration)
        except Exception as e:
            self.error.emit(str(e))


# ===== Drag & drop / click target ========================================
class FileDropZone(QFrame):
    file_dropped = pyqtSignal(str)   # file chosen (dropped or clicked)

    def __init__(self):
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setFixedHeight(130)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        icon = QLabel("\U0001F3AC")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon)

        title = QLabel("Drop video or audio file here")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 13px; color: #e2e8f0; font-weight: 600;")
        layout.addWidget(title)

        hint = QLabel("MP4, MP3, WAV, MKV, WebM")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 11px; color: #64748b;")
        layout.addWidget(hint)

        browse_pill = QLabel("or Browse Files")
        browse_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        browse_pill.setStyleSheet(
            "background-color: rgba(79, 70, 229, 0.20);"
            "color: #818cf8; font-size: 11px; font-weight: 600;"
            "border-radius: 6px; padding: 5px 12px; margin-top: 6px;"
        )
        layout.addWidget(browse_pill)

        # Clicking the zone also opens the browser.
        self._browse_area = browse_pill

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.file_dropped.emit("__BROWSE__")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                "QFrame#dropZone { border: 1.5px dashed #818cf8;"
                " background-color: rgba(79, 70, 229, 0.14);"
                " border-radius: 12px; }"
            )

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)


# ===== Helper ============================================================
def _shadow(widget, blur=30, dy=6, color=QColor(0, 0, 0, 80)):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(color)
    widget.setGraphicsEffect(effect)


# ===== Main window =======================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoSub")
        self.setMinimumSize(820, 660)
        self.resize(1000, 700)

        self.audio_path = None
        self.transcribed_segments = []
        self.worker = None
        self.export_format = "srt"

        self.setup_ui()
        self.apply_style()

    # ------------------------------------------------------------------
    def setup_ui(self):
        background = GradientBackground()
        self.setCentralWidget(background)

        main_layout = QVBoxLayout(background)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 16)

        # ---- Header (logo + title) -----------------------------------
        header = QHBoxLayout()
        header.setSpacing(12)

        logo_badge = QFrame()
        logo_badge.setObjectName("logoBadge")
        logo_badge.setFixedSize(36, 36)
        logo_layout = QVBoxLayout(logo_badge)
        logo_layout.setContentsMargins(5, 5, 5, 5)
        logo_icon = QLabel()
        logo_icon.setPixmap(QIcon(resource_path("assets/app_icon.svg")).pixmap(26, 26))
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_icon)
        header.addWidget(logo_badge)

        title_block = QVBoxLayout()
        title_block.setSpacing(0)
        title_label = QLabel("AutoSub")
        title_label.setObjectName("appTitle")
        title_block.addWidget(title_label)
        tagline = QLabel("AI-Powered Subtitle Generator")
        tagline.setObjectName("tagline")
        title_block.addWidget(tagline)
        header.addLayout(title_block)

        header.addStretch(1)
        main_layout.addLayout(header)

        main_layout.addSpacing(4)

        # ---- Content: two panels -------------------------------------
        content = QHBoxLayout()
        content.setSpacing(20)

        # ===== LEFT PANEL: file + config + generate ===================
        left_panel = QFrame()
        left_panel.setObjectName("panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(16, 16, 16, 16)

        self.drop_zone = FileDropZone()
        self.drop_zone.file_dropped.connect(self._on_drop_zone)
        _shadow(self.drop_zone, blur=20, dy=4)
        left_layout.addWidget(self.drop_zone)

        self.file_label = QLabel("No file selected")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(
            "color: #64748b; font-size: 11px;"
            "padding: 2px 0 8px 0;"
        )
        left_layout.addWidget(self.file_label)

        self._add_section(left_layout, "MODEL", self._build_combo(MODEL_OPTIONS, 4), "model_combo")
        self._add_section(left_layout, "LANGUAGE", self._build_combo(LANGUAGE_OPTIONS, 0), "lang_combo")
        self._add_section(left_layout, "COMPUTE DEVICE", self._build_combo(COMPUTE_OPTIONS, 0), "compute_combo")

        left_layout.addStretch(1)

        self.generate_btn = QPushButton("Generate Subtitles")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setFixedHeight(44)
        self.generate_btn.clicked.connect(self.generate_subtitles)
        self.generate_btn.setEnabled(False)
        left_layout.addWidget(self.generate_btn)

        content.addWidget(left_panel, 5)

        # ===== RIGHT PANEL: preview + export ==========================
        right_panel = QFrame()
        right_panel.setObjectName("panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(16, 16, 16, 16)

        preview_title = QLabel("TRANSCRIPTION PREVIEW")
        preview_title.setObjectName("sectionLabel")
        right_layout.addWidget(preview_title)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Your transcription will appear here...")
        right_layout.addWidget(self.preview_text, 1)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #334155; background-color: #334155; max-height: 1px;")
        right_layout.addWidget(divider)

        # Export bar: format selector + export button.
        export_bar = QHBoxLayout()
        export_bar.setSpacing(10)

        fmt_label = QLabel("Export Format:")
        fmt_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        export_bar.addWidget(fmt_label)

        self.format_btns = {}
        for fmt in FORMAT_OPTIONS:
            btn = QPushButton(fmt.upper())
            btn.setFixedHeight(24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, f=fmt: self._set_format(f))
            self.format_btns[fmt] = btn
            export_bar.addWidget(btn)

        export_bar.addStretch(1)

        self.export_btn = QPushButton("Export Subtitles")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setFixedSize(140, 34)
        self.export_btn.clicked.connect(self.export_file)
        self.export_btn.setEnabled(False)
        export_bar.addWidget(self.export_btn)

        right_layout.addLayout(export_bar)

        _shadow(right_panel, blur=30, dy=6)
        content.addWidget(right_panel, 8)

        main_layout.addLayout(content, 1)

        # ---- Status bar with ready dot ------------------------------
        self._set_format("srt")
        dot = QLabel("\u25CF")
        dot.setStyleSheet("color: #22c55e; font-size: 10px;")
        self.status_message = QLabel("System Ready")
        self.status_message.setStyleSheet("color: #94a3b8; font-size: 11px; padding-left: 6px;")
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        status_layout.addWidget(dot)
        status_layout.addWidget(self.status_message)
        status_layout.addStretch(1)
        self.statusBar().addWidget(status_bar)

    # ------------------------------------------------------------------
    def _build_combo(self, options, default_index):
        """Create a dropdown from (value, label) pairs or plain strings."""
        combo = QComboBox()
        if isinstance(options[0], tuple):
            for value, display in options:
                combo.addItem(display, value)
        else:
            combo.addItems(options)
        combo.setCurrentIndex(default_index)
        combo.setFixedHeight(40)
        return combo

    def _add_section(self, layout, label_text, combo, attr_name):
        label = QLabel(label_text)
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        setattr(self, attr_name, combo)
        layout.addWidget(combo)

    def _set_format(self, fmt: str):
        """Toggle the active format segment button."""
        self.export_format = fmt
        for key, btn in self.format_btns.items():
            if key == fmt:
                btn.setObjectName("formatBtnActive")
            else:
                btn.setObjectName("formatBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ------------------------------------------------------------------
    def _on_drop_zone(self, path: str):
        if path == "__BROWSE__":
            self.browse_file()
        else:
            self.on_file_selected(path)

    def apply_style(self):
        self.setStyleSheet(MODERN_DARK)

    # ===== Event handlers =============================================
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio/Video File", "", SUPPORTED_FORMATS
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path: str):
        self.audio_path = file_path
        filename = os.path.basename(file_path)
        self.file_label.setText(f"\U0001F4C2  {filename}")
        self.file_label.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: 600;")
        self.generate_btn.setEnabled(True)
        self.status_message.setText(filename)

    def generate_subtitles(self):
        if not self.audio_path:
            return

        model_data = self.model_combo.currentData()
        language = self.lang_combo.currentData()
        compute_type = self.compute_combo.currentData()

        self.generate_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.preview_text.clear()
        self.status_message.setText("Loading model...")

        self.worker = TranscriptionWorker(self.audio_path, model_data, language, compute_type)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # ===== Worker slots ===============================================
    def on_progress(self, current: float, total: float, language: str):
        if total > 0:
            percent = min(int((current / total) * 100), 100)
            self.status_message.setText(
                f"Transcribing... {self.format_time(current)} / {self.format_time(total)} ({percent}%)"
            )

    def on_finished(self, segments: list, language: str, duration: float):
        self.transcribed_segments = segments

        preview = segments_to_srt(segments)
        self.preview_text.setPlainText(preview)

        self.generate_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.status_message.setText(f"Done \u2014 {language} \u00b7 {len(segments)} segments")

    def on_error(self, error_msg: str):
        self.status_message.setText("Error")
        self.preview_text.setPlainText(f"Error:\n{error_msg}")
        self.generate_btn.setEnabled(True)

    def export_file(self):
        if not self.transcribed_segments:
            return

        fmt = self.export_format
        ext_map = {"srt": "SRT", "vtt": "VTT", "txt": "TXT"}
        base = os.path.splitext(os.path.basename(self.audio_path))[0]
        default_name = f"{base}.{fmt}"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Subtitles",
            default_name,
            f"{ext_map[fmt]} Files (*.{fmt});;All Files (*)"
        )
        if file_path:
            save(self.transcribed_segments, file_path, fmt)
            self.status_message.setText(f"Saved: {os.path.basename(file_path)}")

    @staticmethod
    def format_time(seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

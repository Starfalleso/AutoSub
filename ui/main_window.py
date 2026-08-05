"""
AutoSub - Main window.

This module builds the entire PyQt6 UI for AutoSub:
  * GradientBackground   - paints the animated-looking gradient backdrop
  * TranscriptionWorker  - runs faster-whisper on a background QThread
  * FileDropZone         - drag & drop target for audio/video files
  * MainWindow           - wires everything together (layout + handlers)

Flow: user drops a file -> clicks "Generate" -> TranscriptionWorker runs in
the background -> progress/finished signals update the UI -> preview shows
the resulting SRT text -> user can export to a .srt file.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QProgressBar,
    QTextEdit, QFileDialog, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import (
    QDragEnterEvent, QDropEvent, QPainter,
    QLinearGradient, QRadialGradient, QColor, QBrush
)

from core.transcriber import Transcriber
from core.subtitle import save_srt, segments_to_srt
from ui.styles import MODERN_DARK, ACCENT


# ===== Constants =========================================================
# File filter shown in the native "Browse Files" dialog.
SUPPORTED_FORMATS = (
    "Video/Audio Files (*.mp4 *.avi *.mkv *.mov *.webm *.mp3 *.wav *.flac *.ogg *.m4a *.wma);;"
    "All Files (*)"
)

# (whisper model id, friendly label) used to populate the Model dropdown.
MODEL_OPTIONS = [
    ("tiny", "Tiny (39M)"),
    ("base", "Base (74M)"),
    ("small", "Small (244M)"),
    ("medium", "Medium (769M)"),
    ("large-v3-turbo", "Large Turbo (756M)"),
    ("large-v3", "Large V3 (1.5B)"),
]

# Human-friendly languages for the Language dropdown.
LANGUAGE_OPTIONS = [
    "Auto",
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Dutch", "Russian", "Chinese", "Japanese", "Korean", "Arabic",
    "Hindi", "Turkish", "Polish", "Swedish", "Norwegian", "Danish",
    "Finnish", "Greek", "Czech", "Romanian", "Hungarian", "Thai",
    "Vietnamese", "Indonesian", "Malay", "Filipino", "Ukrainian",
]

# (compute id, label). int8 is the safe CPU default.
COMPUTE_OPTIONS = [
    ("int8", "int8"),
    ("float16", "float16"),
    ("float32", "float32"),
]


# ===== Background widget =================================================
class GradientBackground(QWidget):
    """Custom widget that paints the dark gradient + corner glows."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Vertical dark gradient (top -> bottom).
        top = QColor("#0c0c14")
        bottom = QColor("#070709")
        vertical = QLinearGradient(0, 0, 0, self.height())
        vertical.setColorAt(0, top)
        vertical.setColorAt(1, bottom)
        painter.fillRect(self.rect(), vertical)

        # Soft indigo glow in the top-left corner.
        accent = QColor(ACCENT)
        accent.setAlpha(28)
        radial = QRadialGradient(
            QPointF(self.width() * 0.15, 0),
            self.width() * 0.7
        )
        radial.setColorAt(0, accent)
        radial.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), radial)

        # Faint violet glow in the bottom-right corner.
        accent2 = QColor("#8b5cf6")
        accent2.setAlpha(16)
        radial2 = QRadialGradient(
            QPointF(self.width(), self.height()),
            self.width() * 0.7
        )
        radial2.setColorAt(0, accent2)
        radial2.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), radial2)


# ===== Background worker thread ==========================================
class TranscriptionWorker(QThread):
    """Runs transcription off the UI thread so the window stays responsive."""
    progress = pyqtSignal(float, float, str)   # (current seconds, total seconds, language)
    finished = pyqtSignal(list, str, float)    # (segments, detected language, duration)
    error = pyqtSignal(str)                    # error message

    def __init__(self, audio_path: str, model_size: str, language: str, compute_type: str):
        super().__init__()
        self.audio_path = audio_path
        self.model_size = model_size
        self.language = language
        self.compute_type = compute_type

    def run(self):
        """Thread entry point. Builds the transcriber and emits signals."""
        try:
            transcriber = Transcriber(model_size=self.model_size, compute_type=self.compute_type)
            transcriber.load_model()

            # Bridge the library's progress callback to a Qt signal.
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


# ===== Drag & drop target ================================================
class FileDropZone(QFrame):
    """Clickable frame that also accepts dragged files."""
    file_dropped = pyqtSignal(str)   # emits the absolute path of the dropped file

    def __init__(self):
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)          # enable drag & drop
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Vertical stack: icon, prompt, supported formats hint.
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel("\U0001F3AC")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 30px;")
        layout.addWidget(icon_label)

        text_label = QLabel("Drop a video or audio file here")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 13px; color: #a1a1aa; font-weight: 600;")
        layout.addWidget(text_label)

        hint_label = QLabel("MP4, MP3, WAV, MKV and more")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("font-size: 11px; color: #52525b;")
        layout.addWidget(hint_label)

    # --- Drag & drop event handlers -------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        # Highlight the zone when a valid file is dragged over it.
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                "QFrame#dropZone { border: 2px solid #818cf8;"
                " background-color: rgba(99, 102, 241, 0.14); border-radius: 16px; }"
            )

    def dragLeaveEvent(self, event):
        # Remove the highlight when the drag leaves the zone.
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        # Extract the first dropped file path and notify the main window.
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.file_dropped.emit(file_path)


# ===== Helper ============================================================
def _shadow(widget, blur=30, dy=6, color=QColor(0, 0, 0, 90)):
    """Attach a soft drop shadow to a widget for a 'floating' look."""
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
        self.setMinimumSize(780, 640)
        self.resize(920, 700)

        # App state
        self.audio_path = None            # currently selected file
        self.transcribed_segments = []    # segments from the last run
        self.worker = None                # active TranscriptionWorker

        self.setup_ui()
        self.apply_style()

    # ------------------------------------------------------------------
    def setup_ui(self):
        """Builds every widget and lays them out in the window."""
        background = GradientBackground()
        background.setObjectName("centralWidget")
        self.setCentralWidget(background)

        # Root layout for the whole window.
        outer = QVBoxLayout(background)
        outer.setContentsMargins(0, 0, 0, 0)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(36, 28, 36, 28)
        outer.addLayout(main_layout)

        # ---- Header (logo + title + tagline) --------------------------
        header = QHBoxLayout()
        header.setSpacing(14)

        # Gradient "AS" logo badge with a glowing shadow.
        logo_badge = QFrame()
        logo_badge.setObjectName("logoBadge")
        logo_badge.setFixedSize(44, 44)
        logo_layout = QVBoxLayout(logo_badge)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_text = QLabel("AS")
        logo_text.setObjectName("logoText")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_text)
        _shadow(logo_badge, blur=26, dy=4, color=QColor(99, 102, 241, 120))
        header.addWidget(logo_badge)

        # "AutoSub" title + tagline stacked vertically.
        title_block = QVBoxLayout()
        title_block.setSpacing(0)
        title_label = QLabel(
            '<span style="color:#818cf8; font-size:24px; font-weight:800;">Auto</span>'
            '<span style="color:#fafafa; font-size:24px; font-weight:800;">Sub</span>'
        )
        title_label.setContentsMargins(0, 0, 0, 0)
        title_block.addWidget(title_label)
        tagline = QLabel("AI-powered subtitle generator")
        tagline.setObjectName("tagline")
        title_block.addWidget(tagline)
        header.addLayout(title_block)

        header.addStretch(1)   # push header content to the left
        main_layout.addLayout(header)

        main_layout.addSpacing(8)

        # ---- Two-pane content area (left controls, right preview) -----
        panes_layout = QHBoxLayout()
        panes_layout.setSpacing(16)
        panes_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(14)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Drop zone (drag & drop).
        self.drop_zone = FileDropZone()
        self.drop_zone.file_dropped.connect(self.on_file_selected)
        _shadow(self.drop_zone, blur=24, dy=5)
        left_layout.addWidget(self.drop_zone)

        # File chip + Browse button share one row.
        file_row = QHBoxLayout()
        file_row.setSpacing(10)

        # Chip that shows the selected filename (hidden until a file is picked).
        self.file_chip = QFrame()
        self.file_chip.setObjectName("fileChip")
        self.file_chip.setVisible(False)
        file_chip_layout = QHBoxLayout(self.file_chip)
        file_chip_layout.setContentsMargins(12, 8, 12, 8)
        file_chip_layout.setSpacing(8)
        file_icon = QLabel("\U0001F4C2")
        file_icon.setStyleSheet("font-size: 14px;")
        file_chip_layout.addWidget(file_icon)
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileName")
        file_chip_layout.addWidget(self.file_label, 1)
        file_chip_layout.addStretch(1)
        file_row.addWidget(self.file_chip, 1)

        # Browse button (opens native file dialog).
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.setFixedWidth(132)
        self.browse_btn.setFixedHeight(40)
        self.browse_btn.clicked.connect(self.browse_file)
        file_row.addWidget(self.browse_btn)

        left_layout.addLayout(file_row)

        # Options card: Model / Language / Compute dropdowns.
        options_card = QFrame()
        options_card.setObjectName("card")
        options_layout = QVBoxLayout(options_card)
        options_layout.setSpacing(10)
        options_layout.setContentsMargins(18, 18, 18, 18)

        # Model dropdown.
        model_label = QLabel("MODEL")
        model_label.setObjectName("sectionTitle")
        options_layout.addWidget(model_label)
        self.model_combo = QComboBox()
        for value, display in MODEL_OPTIONS:
            self.model_combo.addItem(display, value)
        self.model_combo.setCurrentIndex(4)   # default: large-v3-turbo
        self.model_combo.setFixedHeight(40)
        options_layout.addWidget(self.model_combo)

        # Language dropdown.
        lang_label = QLabel("LANGUAGE")
        lang_label.setObjectName("sectionTitle")
        options_layout.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANGUAGE_OPTIONS)
        self.lang_combo.setFixedHeight(40)
        options_layout.addWidget(self.lang_combo)

        # Compute type dropdown.
        compute_label = QLabel("COMPUTE")
        compute_label.setObjectName("sectionTitle")
        options_layout.addWidget(compute_label)
        self.compute_combo = QComboBox()
        for value, display in COMPUTE_OPTIONS:
            self.compute_combo.addItem(display, value)
        self.compute_combo.setFixedHeight(40)
        options_layout.addWidget(self.compute_combo)

        _shadow(options_card, blur=30, dy=6)
        left_layout.addWidget(options_card)

        # Progress bar (hidden text, thin strip).
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        left_layout.addWidget(self.progress_bar)

        # Status label (Ready / Transcribing / Done / Error).
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.status_label)

        left_layout.addStretch(1)   # push everything in the left pane upward

        # Preview card: shows the generated SRT text.
        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setSpacing(10)
        preview_layout.setContentsMargins(18, 18, 18, 18)

        # Card header ("PREVIEW").
        preview_header = QHBoxLayout()
        preview_label = QLabel("PREVIEW")
        preview_label.setObjectName("sectionTitle")
        preview_header.addWidget(preview_label)
        preview_header.addStretch(1)
        preview_layout.addLayout(preview_header)

        # Read-only text area holding the subtitle preview.
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Transcription will appear here...")
        self.preview_text.setMinimumHeight(220)
        preview_layout.addWidget(self.preview_text, 1)

        _shadow(preview_card, blur=34, dy=8)
        panes_layout.addWidget(left_widget, 1)    # left pane (stretch 1)
        panes_layout.addWidget(preview_card, 2)   # right pane (stretch 2)

        main_layout.addLayout(panes_layout, 1)

        # ---- Action buttons row ---------------------------------------
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main action: generate subtitles.
        self.generate_btn = QPushButton("Generate Subtitles")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setFixedWidth(180)
        self.generate_btn.setFixedHeight(42)
        self.generate_btn.clicked.connect(self.generate_subtitles)
        self.generate_btn.setEnabled(False)   # disabled until a file is selected
        _shadow(self.generate_btn, blur=24, dy=4, color=QColor(99, 102, 241, 100))
        buttons_layout.addWidget(self.generate_btn)

        # Secondary action: export the result to a .srt file.
        self.save_btn = QPushButton("Export SRT")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setFixedWidth(120)
        self.save_btn.setFixedHeight(42)
        self.save_btn.clicked.connect(self.save_srt_file)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addLayout(buttons_layout)

        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    def apply_style(self):
        """Apply the global stylesheet to the whole window."""
        self.setStyleSheet(MODERN_DARK)

    # ------------------------------------------------------------------
    # ===== Event handlers ==============================================

    def browse_file(self):
        """Open the native file picker and load the chosen file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio/Video File", "", SUPPORTED_FORMATS
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path: str):
        """Store the selected file and enable the Generate button."""
        self.audio_path = file_path
        filename = os.path.basename(file_path)
        self.file_label.setText(filename)
        self.file_chip.setVisible(True)
        self.generate_btn.setEnabled(True)
        self.statusBar().showMessage(filename)

    def generate_subtitles(self):
        """Kick off transcription in a background worker thread."""
        if not self.audio_path:
            return

        model_data = self.model_combo.currentData()
        language = self.lang_combo.currentText()
        compute_type = self.compute_combo.currentData()

        # Reset the UI for a new run and disable actions while busy.
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.preview_text.clear()
        self.status_label.setStyleSheet("color: #a1a1aa;")
        self.status_label.setText("Loading model...")

        # Start the background thread and wire its signals.
        self.worker = TranscriptionWorker(self.audio_path, model_data, language, compute_type)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # ===== Worker signal slots =========================================

    def on_progress(self, current: float, total: float, language: str):
        """Update the progress bar + status text as transcription advances."""
        if total > 0:
            percent = min(int((current / total) * 100), 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"Transcribing... {self.format_time(current)} / {self.format_time(total)}")

    def on_finished(self, segments: list, language: str, duration: float):
        """Show the result in the preview and enable Export."""
        self.transcribed_segments = segments
        self.progress_bar.setValue(100)
        self.status_label.setStyleSheet("color: #34d399; font-weight: 600;")
        self.status_label.setText(f"Done \u2014 {language}")

        preview = segments_to_srt(segments)
        self.preview_text.setPlainText(preview)

        self.generate_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.statusBar().showMessage(f"{len(segments)} segments")

    def on_error(self, error_msg: str):
        """Show the error, re-enable Generate, and reset progress."""
        self.status_label.setStyleSheet("color: #f87171; font-weight: 600;")
        self.status_label.setText(error_msg)
        self.generate_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("Error")

    def save_srt_file(self):
        """Prompt for a save location and write the SRT file."""
        if not self.transcribed_segments:
            return

        default_name = os.path.splitext(os.path.basename(self.audio_path))[0] + ".srt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save SRT File", default_name, "SRT Files (*.srt);;All Files (*)"
        )
        if file_path:
            save_srt(self.transcribed_segments, file_path)
            self.statusBar().showMessage(f"Saved: {os.path.basename(file_path)}")
            self.status_label.setStyleSheet("color: #34d399; font-weight: 600;")
            self.status_label.setText("Saved")

    @staticmethod
    def format_time(seconds: float) -> str:
        """Convert seconds to a m:ss display string."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

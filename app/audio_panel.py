from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QLabel, QMessageBox
from app.audio_engine import AudioEngine


class AudioPanel(QWidget):
    clip_loaded = Signal(str)

    def __init__(self, title: str, slot: int, engine: AudioEngine, parent=None):
        super().__init__(parent)
        self.title = title
        self.slot = slot
        self.engine = engine
        self.segment = None
        self.waveform = []
        self.setMinimumSize(250, 150)
        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel(f"{self.title}\nClick to load")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        path, _ = QFileDialog.getOpenFileName(
            self, f"Load {self.title}",
            "",
            "Audio Files (*.wav *.mp3)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str):
        try:
            self.segment = self.engine.load(path, slot=self.slot)
            self.waveform = self.engine.get_waveform_data(self.segment)
            duration = self.segment.duration_seconds
            self.label.setText(
                f"{self.title}\n"
                f"{int(duration // 60):02d}:{int(duration % 60):02d}"
            )
            self.clip_loaded.emit(path)
            self.update()
        except Exception as e:
            self.segment = None
            self.waveform = []
            self.label.setText(f"{self.title}\nError: {e}")
            self.clip_loaded.emit("")
            QMessageBox.warning(self, "Load Error", f"Failed to load audio:\n{e}")

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.waveform:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        painter.setPen(QColor(100, 140, 255))
        peaks = self.waveform
        n_peaks = len(peaks)
        bar_width = max(2, w / n_peaks)
        mid_y = h / 2
        for i, peak in enumerate(peaks):
            normalized = peak / 32768.0
            bar_height = normalized * (h / 2 - 10)
            x = i * bar_width
            painter.drawLine(int(x), int(mid_y - bar_height), int(x), int(mid_y + bar_height))

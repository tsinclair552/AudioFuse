from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QLabel, QMessageBox
from app.audio_engine import AudioEngine
from app.theme import PANEL_STYLE, product_shadow, INK, INK_MUTED, PRIMARY


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
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(PANEL_STYLE)
        self.setGraphicsEffect(product_shadow(self))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        self.label = QLabel(self._empty_text())
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setTextFormat(Qt.RichText)
        layout.addWidget(self.label)

    def _empty_text(self) -> str:
        return (
            f"<span style='font-size:28px; font-weight:300; color:{INK};'>"
            f"{self.title}</span><br>"
            f"<span style='font-size:14px; color:{INK_MUTED};'>Click to load</span>"
        )

    def _loaded_text(self, duration_secs: float) -> str:
        minutes = int(duration_secs // 60)
        seconds = int(duration_secs % 60)
        return (
            f"<span style='font-size:28px; font-weight:300; color:{INK};'>"
            f"{self.title}</span><br>"
            f"<span style='font-size:17px; color:{INK};'>"
            f"{minutes:02d}:{seconds:02d}</span>"
        )

    def _error_text(self, message: str) -> str:
        return (
            f"<span style='font-size:28px; font-weight:300; color:{INK};'>"
            f"{self.title}</span><br>"
            f"<span style='font-size:14px; color:red;'>{message}</span>"
        )

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        path, _ = QFileDialog.getOpenFileName(
            self, f"Load {self.title}",
            "",
            "Audio Files (*.wav *.mp3)"
        )
        if path:
            self.load_file(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(('.wav', '.mp3')):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.toLocalFile().lower().endswith(('.wav', '.mp3')):
                self.load_file(url.toLocalFile())
                event.acceptProposedAction()
                return

    def load_file(self, path: str):
        try:
            self.segment = self.engine.load(path, slot=self.slot)
            self.waveform = self.engine.get_waveform_data(self.segment)
            duration = self.segment.duration_seconds
            self.label.setText(self._loaded_text(duration))
            self.clip_loaded.emit(path)
            self.update()
        except Exception as e:
            self.segment = None
            self.waveform = []
            self.label.setText(self._error_text(str(e)))
            self.clip_loaded.emit("")
            QMessageBox.warning(self, "Load Error", f"Failed to load audio:\n{e}")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.waveform:
            w = self.width()
            h = self.height()
            painter.setPen(QColor(PRIMARY))
            peaks = self.waveform
            n_peaks = len(peaks)
            bar_width = max(2, w / n_peaks)
            mid_y = h / 2
            for i, peak in enumerate(peaks):
                normalized = peak / 32768.0
                bar_height = normalized * (h / 2 - 10)
                x = i * bar_width
                painter.drawLine(int(x), int(mid_y - bar_height), int(x), int(mid_y + bar_height))

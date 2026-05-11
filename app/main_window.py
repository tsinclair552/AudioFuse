from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox
)
from app.audio_panel import AudioPanel
from app.audio_engine import AudioEngine


class MainWindow(QMainWindow):
    def __init__(self, engine: AudioEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("AudioFuse")
        self.setMinimumSize(600, 300)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        panels_layout = QHBoxLayout()
        self.panel1 = AudioPanel("Clip 1", 1, self.engine)
        self.panel2 = AudioPanel("Clip 2", 2, self.engine)
        panels_layout.addWidget(self.panel1)
        panels_layout.addWidget(self.panel2)
        layout.addLayout(panels_layout)

        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.gap_button = QPushButton("Gap: OFF")
        self.gap_button.setCheckable(True)
        self.gap_button.clicked.connect(self._toggle_gap)
        controls_layout.addWidget(self.gap_button)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self._download)
        self.download_button.setEnabled(False)
        controls_layout.addWidget(self.download_button)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.panel1.clip_loaded.connect(self._check_ready)
        self.panel2.clip_loaded.connect(self._check_ready)

    def _toggle_gap(self, checked):
        self.gap_button.setText(f"Gap: {'ON' if checked else 'OFF'}")

    def _check_ready(self):
        ready = (self.panel1.segment is not None and self.panel2.segment is not None)
        self.download_button.setEnabled(ready)

    def _download(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Combined Clip", "",
            "WAV Audio (*.wav);;MP3 Audio (*.mp3)"
        )
        if not path:
            return
        try:
            gap = 1.0 if self.gap_button.isChecked() else 0.0
            combined = self.engine.concatenate(gap_seconds=gap)
            normalized = self.engine.normalize(combined)
            self.engine.export(normalized, path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save: {e}")

import os
import tempfile
import atexit
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox
)
from app.theme import CANVAS, ACTION_BUTTON_STYLE, GAP_BUTTON_STYLE
from app.audio_panel import AudioPanel
from app.audio_engine import AudioEngine


class MainWindow(QMainWindow):
    def __init__(self, engine: AudioEngine):
        super().__init__()
        self.engine = engine
        self.preview_player = QMediaPlayer(self)
        self.preview_audio = QAudioOutput(self)
        self.preview_player.setAudioOutput(self.preview_audio)
        self._preview_temp = None
        atexit.register(self._cleanup_temp)
        self.setWindowTitle("AudioFuse")
        self.setMinimumSize(600, 300)
        self._setup_ui()
        self.preview_player.playbackStateChanged.connect(self._on_preview_state_changed)

    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background-color: {CANVAS};")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 32, 32, 32)

        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(24)
        self.panel1 = AudioPanel("Clip 1", 1, self.engine)
        self.panel2 = AudioPanel("Clip 2", 2, self.engine)
        panels_layout.addWidget(self.panel1)
        panels_layout.addWidget(self.panel2)
        layout.addLayout(panels_layout)

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 24, 0, 0)
        controls_layout.addStretch()

        self.gap_button = QPushButton("Gap: OFF")
        self.gap_button.setCheckable(True)
        self.gap_button.setCursor(Qt.PointingHandCursor)
        self.gap_button.clicked.connect(self._toggle_gap)
        controls_layout.addWidget(self.gap_button)

        self.preview_button = QPushButton("Preview")
        self.preview_button.setCursor(Qt.PointingHandCursor)
        self.preview_button.clicked.connect(self._toggle_preview)
        self.preview_button.setEnabled(False)
        controls_layout.addWidget(self.preview_button)

        self.download_button = QPushButton("Download")
        self.download_button.setCursor(Qt.PointingHandCursor)
        self.download_button.clicked.connect(self._download)
        self.download_button.setEnabled(False)
        controls_layout.addWidget(self.download_button)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.preview_button.setStyleSheet(ACTION_BUTTON_STYLE)
        self.download_button.setStyleSheet(ACTION_BUTTON_STYLE)
        self.gap_button.setStyleSheet(GAP_BUTTON_STYLE)

        self.panel1.clip_loaded.connect(self._check_ready)
        self.panel2.clip_loaded.connect(self._check_ready)
        self.panel1.clip_loaded.connect(self._stop_preview)
        self.panel2.clip_loaded.connect(self._stop_preview)

    def _toggle_gap(self, checked):
        self.gap_button.setText(f"Gap: {'ON' if checked else 'OFF'}")

    def _check_ready(self):
        ready = (self.panel1.segment is not None and self.panel2.segment is not None)
        self.download_button.setEnabled(ready)
        self.preview_button.setEnabled(ready)

    def _stop_preview(self):
        if self.preview_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.preview_player.stop()

    def _toggle_preview(self):
        if self.preview_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.preview_player.stop()
            return
        try:
            self._cleanup_temp()
            gap = 1.0 if self.gap_button.isChecked() else 0.0
            combined = self.engine.concatenate(gap_seconds=gap)
            normalized = self.engine.normalize(combined)
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            self.engine.export(normalized, tmp.name)
            self._preview_temp = tmp.name
            self.preview_player.setSource(QUrl.fromLocalFile(tmp.name))
            self.preview_player.play()
            self.preview_button.setText("Stop")
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Failed to preview:\n{e}")
            self.preview_button.setText("Preview")

    def _on_preview_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.preview_button.setText("Preview")
            self._cleanup_temp()

    def _download(self):
        self._stop_preview()
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

    def _cleanup_temp(self):
        if self._preview_temp:
            try:
                os.unlink(self._preview_temp)
            except FileNotFoundError:
                pass
            self._preview_temp = None

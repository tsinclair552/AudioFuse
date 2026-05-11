# AudioFuse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a desktop app that takes two audio clips and combines them with optional silence gap and peak normalization.

**Architecture:** PySide6 UI with two side-by-side audio panels, pydub audio engine for loading/concatenating/normalizing/exporting WAV+MP3.

**Tech Stack:** Python 3.10+, PySide6, pydub, ffmpeg, pytest

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `app/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)

- [ ] **Step 1: Create requirements.txt**

```
PySide6>=6.5
pydub>=0.25
```

- [ ] **Step 2: Create empty init files**

`app/__init__.py` — empty file
`tests/__init__.py` — empty file

- [ ] **Step 3: Create directory structure**

```bash
mkdir -p app tests
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "chore: scaffold project structure"
```

---

### Task 2: AudioEngine — core audio processing

**Files:**
- Create: `app/audio_engine.py`
- Create: `tests/test_audio_engine.py`

AudioEngine is a thin wrapper around pydub. It handles loading, concatenating, normalizing, and exporting audio.

- [ ] **Step 1: Create test file with test helpers**

```python
import os
import tempfile
import struct
import wave
import pytest
from app.audio_engine import AudioEngine


def _generate_sine_wav(path: str, duration_ms: int = 2000, frequency: int = 440, sample_rate: int = 44100):
    """Generate a simple sine wave WAV file for testing."""
    n_samples = int(sample_rate * duration_ms / 1000)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        sample = int(32767 * 0.5 * (__import__('math').sin(2 * __import__('math').pi * frequency * t)))
        samples.append(sample)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f'<{len(samples)}h', *samples))


@pytest.fixture
def engine():
    return AudioEngine()


@pytest.fixture
def wav_files():
    paths = []
    for i in range(2):
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        _generate_sine_wav(path, duration_ms=1000, frequency=440 + i * 110)
        paths.append(path)
    yield paths
    for p in paths:
        os.unlink(p)
```

- [ ] **Step 2: Write failing load test**

```python
def test_load_wav(engine, wav_files):
    segment = engine.load(wav_files[0])
    assert segment is not None
    assert segment.duration_seconds == 1.0
```

Run: `pytest tests/test_audio_engine.py::test_load_wav -v`
Expected: FAIL with `ModuleNotFoundError` or `AttributeError`

- [ ] **Step 3: Write minimal AudioEngine implementation**

```python
from pydub import AudioSegment


class AudioEngine:
    def load(self, path: str) -> AudioSegment:
        return AudioSegment.from_file(path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_audio_engine.py::test_load_wav -v`
Expected: PASS

- [ ] **Step 5: Write concatenation tests**

```python
def test_concatenate_no_gap(engine, wav_files):
    engine.load(wav_files[0])
    engine.load(wav_files[1])
    result = engine.concatenate()
    assert result.duration_seconds == pytest.approx(2.0, rel=0.01)


def test_concatenate_with_gap(engine, wav_files):
    engine.load(wav_files[0])
    engine.load(wav_files[1])
    result = engine.concatenate(gap_seconds=1.0)
    assert result.duration_seconds == pytest.approx(3.0, rel=0.01)
```

- [ ] **Step 6: Implement concatenate with silence support**

```python
class AudioEngine:
    def __init__(self):
        self.clip1: AudioSegment | None = None
        self.clip2: AudioSegment | None = None

    def load(self, path: str) -> AudioSegment:
        segment = AudioSegment.from_file(path)
        if self.clip1 is None:
            self.clip1 = segment
        else:
            self.clip2 = segment
        return segment

    def concatenate(self, gap_seconds: float = 0) -> AudioSegment:
        if self.clip1 is None or self.clip2 is None:
            raise ValueError("Both clips must be loaded before concatenation")
        if gap_seconds > 0:
            silence = AudioSegment.silent(duration=int(gap_seconds * 1000))
            return self.clip1 + silence + self.clip2
        return self.clip1 + self.clip2

    @staticmethod
    def ffmpeg_available() -> bool:
        import subprocess
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def normalize(self, segment: AudioSegment) -> AudioSegment:
        return segment.normalize()

    def export(self, segment: AudioSegment, path: str):
        segment.export(path, format=path.split('.')[-1])
```

- [ ] **Step 7: Run all tests**

Run: `pytest tests/test_audio_engine.py -v`
Expected: All 3 tests PASS

- [ ] **Step 8: Write normalize test**

```python
def test_normalize(engine, wav_files):
    engine.load(wav_files[0])
    engine.load(wav_files[1])
    combined = engine.concatenate()
    normalized = engine.normalize(combined)
    assert normalized.duration_seconds == pytest.approx(2.0, rel=0.01)
    # Normalized segment should have max_dBFS close to 0
    assert normalized.max_dBFS > -1.0  # within 1 dB of 0
```

- [ ] **Step 9: Run tests again**

Run: `pytest tests/test_audio_engine.py -v`
Expected: All 4 tests PASS

- [ ] **Step 10: Write waveform data extraction method**

Add to AudioEngine:

```python
    def get_waveform_data(self, segment: AudioSegment, max_points: int = 500) -> list[int]:
        raw = segment.get_array_of_samples()
        chunk_size = max(1, len(raw) // max_points)
        peaks = []
        for i in range(0, len(raw), chunk_size):
            chunk = raw[i:i + chunk_size]
            peaks.append(max(abs(s) for s in chunk))
        return peaks
```

- [ ] **Step 11: Run all tests**

Run: `pytest tests/test_audio_engine.py -v`
Expected: All 4 tests still PASS

- [ ] **Step 12: Commit**

```bash
git add -A && git commit -m "feat: add AudioEngine with load/concatenate/normalize/export"
```

---

### Task 3: AudioPanel — custom waveform widget

**Files:**
- Create: `app/audio_panel.py`

AudioPanel is a QWidget that shows a click-to-load zone, a waveform visualization, and a duration label.

- [ ] **Step 1: Write AudioPanel implementation**

```python
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QLabel


class AudioPanel(QWidget):
    clip_loaded = Signal(str)

    def __init__(self, title: str, engine, parent=None):
        super().__init__(parent)
        self.title = title
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
        path, _ = QFileDialog.getOpenFileName(
            self, f"Load {self.title}",
            "",
            "Audio Files (*.wav *.mp3)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str):
        self.segment = self.engine.load(path)
        self.waveform = self.engine.get_waveform_data(self.segment)
        duration = self.segment.duration_seconds
        self.label.setText(
            f"{self.title}\n"
            f"{int(duration // 60):02d}:{int(duration % 60):02d}"
        )
        self.clip_loaded.emit(path)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.waveform:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        painter.setPen(QColor(100, 140, 255))
        bar_width = max(2, w / len(self.waveform))
        mid_y = h / 2
        for i, peak in enumerate(self.waveform):
            normalized = peak / 32768.0
            bar_height = normalized * (h / 2 - 10)
            x = i * bar_width
            painter.drawLine(int(x), int(mid_y - bar_height), int(x), int(mid_y + bar_height))
```

- [ ] **Step 2: Verify file exists and is syntactically valid**

Run: `python -c "import ast; ast.parse(open('app/audio_panel.py').read()); print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: add AudioPanel widget with waveform rendering"
```

---

### Task 4: MainWindow — app layout and orchestration

**Files:**
- Create: `app/main_window.py`

MainWindow arranges two AudioPanels side-by-side with a toolbar containing the Gap toggle and Download button.

- [ ] **Step 1: Write MainWindow**

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox
)
from app.audio_panel import AudioPanel


class MainWindow(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.gap_enabled = False
        self.setWindowTitle("AudioFuse")
        self.setMinimumSize(600, 300)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        panels_layout = QHBoxLayout()
        self.panel1 = AudioPanel("Clip 1", self.engine)
        self.panel2 = AudioPanel("Clip 2", self.engine)
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
        self.gap_enabled = checked
        self.gap_button.setText(f"Gap: {'ON' if checked else 'OFF'}")

    def _check_ready(self, _=None):
        ready = (self.panel1.segment is not None and self.panel2.segment is not None)
        self.download_button.setEnabled(ready)

    def _download(self):
        gap = 1.0 if self.gap_enabled else 0.0
        combined = self.engine.concatenate(gap_seconds=gap)
        normalized = self.engine.normalize(combined)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Combined Clip", "",
            "WAV Audio (*.wav);;MP3 Audio (*.mp3)"
        )
        if path:
            try:
                self.engine.export(normalized, path)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save: {e}")
```

- [ ] **Step 2: Verify file is syntactically valid**

Run: `python -c "import ast; ast.parse(open('app/main_window.py').read()); print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: add MainWindow with layout and controls"
```

---

### Task 5: Entry point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write main.py**

```python
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from app.audio_engine import AudioEngine
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    engine = AudioEngine()
    if not engine.ffmpeg_available():
        QMessageBox.critical(
            None, "Missing Dependency",
            "ffmpeg is required but not found.\n\n"
            "Install it:\n"
            "  macOS: brew install ffmpeg\n"
            "  Linux: apt install ffmpeg\n"
            "  Windows: choco install ffmpeg"
        )
        sys.exit(1)
    window = MainWindow(engine)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "import ast; ast.parse(open('main.py').read()); print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: add application entry point"
```

---

### Task 6: Integration check and final verification

**Files:**
- Modify: none (verification only)

- [ ] **Step 1: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All 4+ tests PASS

- [ ] **Step 2: Verify imports resolve**

Run: `python -c "from app.audio_engine import AudioEngine; from app.audio_panel import AudioPanel; from app.main_window import MainWindow; print('All imports OK')"`
Expected: All imports OK (Note: may need `export QT_QPA_PLATFORM=offscreen` in headless environments)

- [ ] **Step 3: Final commit**

```bash
git add -A && git commit -m "chore: finalize AudioFuse implementation"
```

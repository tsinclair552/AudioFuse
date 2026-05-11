# Apple UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply Apple Design System surface polish (colors, typography, pill buttons, product shadow, spacing) to the AudioFuse desktop app via Qt stylesheets.

**Architecture:** Create a shared `theme.py` with color constants and stylesheet strings, then apply centrally in `main_window.py` and per-widget in `audio_panel.py`. All styling is cosmetic — no behavior changes.

**Tech Stack:** PySide6, Qt stylesheets, QGraphicsDropShadowEffect

**Files to Modify:**
- `app/theme.py` (create)
- `app/main_window.py` (modify)
- `app/audio_panel.py` (modify)

---

### Task 1: Create theme constants module

**Files:**
- Create: `app/theme.py`

- [ ] **Step 1: Create `app/theme.py` with Apple design tokens**

```python
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PySide6.QtGui import QColor


CANVAS = "#ffffff"
PARCHMENT = "#f5f5f7"
INK = "#1d1d1f"
INK_MUTED = "#7a7a7a"
PRIMARY = "#0066cc"
PRIMARY_HOVER = "#0055aa"
PRIMARY_PRESSED = "#004488"
PRIMARY_DISABLED = "#b3d4f0"
HAIRLINE = "#e0e0e0"


def product_shadow(parent: QWidget) -> QGraphicsDropShadowEffect:
    effect = QGraphicsDropShadowEffect(parent)
    effect.setBlurRadius(30)
    effect.setOffset(3, 5)
    effect.setColor(QColor(0, 0, 0, 55))
    return effect


MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {CANVAS};
    }}
"""

PANEL_STYLE = f"""
    AudioPanel {{
        background-color: {PARCHMENT};
        border: 1px solid {HAIRLINE};
        border-radius: 18px;
    }}
    AudioPanel QLabel {{
        background: transparent;
        border: none;
    }}
"""

GAP_BUTTON_STYLE = f"""
    QPushButton {{
        background: transparent;
        border: 1px solid {PRIMARY};
        color: {PRIMARY};
        border-radius: 9999px;
        padding: 8px 22px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {PRIMARY};
        color: white;
    }}
    QPushButton:pressed {{
        background: {PRIMARY_PRESSED};
        color: white;
    }}
"""

ACTION_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 9999px;
        padding: 8px 22px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {PRIMARY_PRESSED};
    }}
    QPushButton:disabled {{
        background-color: {PRIMARY_DISABLED};
        color: white;
    }}
"""
```

- [ ] **Step 2: Commit**

```bash
git add app/theme.py
git commit -m "feat: add Apple design token constants and stylesheet strings"
```

---

### Task 2: Restyle MainWindow

**Files:**
- Modify: `app/main_window.py`

- [ ] **Step 1: Update imports and apply stylesheet in `app/main_window.py`**

Add import:
```python
from app.theme import MAIN_WINDOW_STYLE, ACTION_BUTTON_STYLE, GAP_BUTTON_STYLE, product_shadow
```

- [ ] **Step 2: Set object names for buttons and apply stylesheets in `_setup_ui`**

In `_setup_ui`, after creating the buttons, apply styles:

```python
def _setup_ui(self):
    central = QWidget()
    self.setCentralWidget(central)
    self.setStyleSheet(MAIN_WINDOW_STYLE)
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

    # Apply button stylesheets
    self.preview_button.setStyleSheet(ACTION_BUTTON_STYLE)
    self.download_button.setStyleSheet(ACTION_BUTTON_STYLE)
    self.gap_button.setStyleSheet(GAP_BUTTON_STYLE)
```

Add the `Qt` import:
```python
from PySide6.QtCore import Qt, QUrl
```

Also add hover effect to gap button text for checked state:
```python
def _toggle_gap(self, checked):
    self.gap_button.setText(f"Gap: {'ON' if checked else 'OFF'}")
```

- [ ] **Step 3: Verify it runs without error**

```bash
python -c "from app.main_window import MainWindow; print('OK')"
```

Expected: prints "OK" with no error

- [ ] **Step 4: Commit**

```bash
git add app/main_window.py
git commit -m "feat: apply Apple stylesheet to main window and buttons"
```

---

### Task 3: Restyle AudioPanel

**Files:**
- Modify: `app/audio_panel.py`

- [ ] **Step 1: Apply parchment background, rounded border, shadow, and waveform color to `AudioPanel`**

New contents of `app/audio_panel.py`:

```python
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QLabel, QMessageBox
from app.audio_engine import AudioEngine
from app.theme import PANEL_STYLE, product_shadow, INK, INK_MUTED, PRIMARY
from app.theme import PARCHMENT, HAIRLINE


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
```

- [ ] **Step 2: Verify syntax**

```bash
python -c "from app.audio_panel import AudioPanel; print('OK')"
```

Expected: prints "OK" with no error

- [ ] **Step 3: Verify full app launches**

```bash
python -c "
import sys
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
from app.main_window import MainWindow
from app.audio_engine import AudioEngine
engine = AudioEngine()
win = MainWindow(engine)
win.show()
print('App launched successfully')
"
```

Expected: prints "App launched successfully" with no error

- [ ] **Step 4: Commit**

```bash
git add app/audio_panel.py
git commit -m "feat: apply Apple styling to audio panels (parchment, shadow, waveform color)"
```

---

### Task 4: Rebuild frozen .app and verify

**Files:**
- Modify: `AudioFuse.spec` (temporarily set `console=True` for testing)

- [ ] **Step 1: Rebuild with PyInstaller**

```bash
rm -rf dist build && pyinstaller --clean AudioFuse.spec
```

Expected: Build succeeds, .app at `dist/AudioFuse.app`

- [ ] **Step 2: Launch .app from terminal and confirm no crash, styled UI appears**

```bash
"dist/AudioFuse.app/Contents/MacOS/AudioFuse" &
sleep 3
kill %1 2>/dev/null; wait 2>/dev/null
```

Expected: App window appears with parchment panels, blue pill buttons, product shadow

- [ ] **Step 3: Revert `console=False` in spec** if it was set to True

- [ ] **Step 4: Commit final changes**

```bash
git add AudioFuse.spec
git commit -m "fix: rebuild frozen .app with Apple UI polish"
```

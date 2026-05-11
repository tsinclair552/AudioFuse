# AudioFuse Preview & Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Preview button for hearing combined clip before download, and package as a double-clickable macOS `.app`.

**Architecture:** Preview reuses existing AudioEngine pipeline + QMediaPlayer playback. Packaging uses PyInstaller with bundled ffmpeg.

**Tech Stack:** PySide6.QtMultimedia, PyInstaller

---

### Task 1: Preview Button

**Files:**
- Modify: `app/main_window.py`

Preview button plays the combined clip via QMediaPlayer before download.

- [ ] **Step 1: Add imports and playback state to MainWindow**

Add to top of `app/main_window.py`:

```python
import tempfile
import atexit
import os
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
```

- [ ] **Step 2: Add playback state to `__init__`**

After `self.engine = engine`, add:

```python
self.preview_player = QMediaPlayer()
self.preview_audio = QAudioOutput()
self.preview_player.setAudioOutput(self.preview_audio)
self._preview_temp = None
```

- [ ] **Step 3: Add Preview button to `_setup_ui`**

After `self.gap_button` block and before `self.download_button`, add:

```python
self.preview_button = QPushButton("Preview")
self.preview_button.clicked.connect(self._toggle_preview)
self.preview_button.setEnabled(False)
controls_layout.addWidget(self.preview_button)
```

And connect clip_loaded to enable/disable it (same gate as download):

```python
self.panel1.clip_loaded.connect(self._check_ready)
self.panel2.clip_loaded.connect(self._check_ready)
```

Update `_check_ready` to also gate preview:

```python
def _check_ready(self):
    ready = (self.panel1.segment is not None and self.panel2.segment is not None)
    self.download_button.setEnabled(ready)
    self.preview_button.setEnabled(ready)
```

- [ ] **Step 4: Add `_toggle_preview` method**

```python
def _toggle_preview(self):
    if self.preview_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
        self.preview_player.stop()
        self.preview_button.setText("Preview")
        self._cleanup_temp()
        return
    try:
        self._cleanup_temp()
        gap = 1.0 if self.gap_button.isChecked() else 0.0
        combined = self.engine.concatenate(gap_seconds=gap)
        normalized = self.engine.normalize(combined)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self.engine.export(normalized, tmp.name)
        self._preview_temp = tmp.name
        self.preview_player.setSource(QUrl.fromLocalFile(tmp.name))
        self.preview_player.play()
        self.preview_button.setText("Stop")
    except Exception as e:
        QMessageBox.warning(self, "Preview Error", f"Failed to preview:\n{e}")
        self.preview_button.setText("Preview")
```

- [ ] **Step 5: Add `_cleanup_temp` and register cleanup on exit**

```python
def _cleanup_temp(self):
    if self._preview_temp:
        try:
            os.unlink(self._preview_temp)
        except OSError:
            pass
        self._preview_temp = None
```

Also call cleanup when stopping playback or loading new clips. In `_toggle_preview`, stop already cleans up. For clip change, add to panel's clip_loaded handling — but since the button will be re-enabled, the old preview is stale. Add a slot to stop preview when clips change:

Actually, simpler: connect both panels' `clip_loaded` to stop any playing preview:

In `_setup_ui`, after existing clip_loaded connections:

```python
self.panel1.clip_loaded.connect(self._stop_preview)
self.panel2.clip_loaded.connect(self._stop_preview)
```

```python
def _stop_preview(self):
    if self.preview_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
        self.preview_player.stop()
        self.preview_button.setText("Preview")
        self._cleanup_temp()
```

Also connect Download to stop preview:

In `_download`, at the start:

```python
def _download(self):
    self._stop_preview()
    ...
```

- [ ] **Step 6: Verify syntax**

Run: `python -c "import ast; ast.parse(open('app/main_window.py').read()); print('OK')"`
Expected: OK

- [ ] **Step 7: Run tests**

Run: `pytest tests/ -v`
Expected: 8/8 PASS

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: add Preview button with QtMultimedia playback"
```

---

### Task 2: PyInstaller Packaging

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add pyinstaller to requirements.txt**

Append to `requirements.txt`:

```
pyinstaller>=6.0
```

- [ ] **Step 2: Build the app**

```bash
pip install pyinstaller
pyinstaller --name "AudioFuse" --windowed --add-binary "$(which ffmpeg):." main.py
```

Expected: `dist/AudioFuse.app` created, double-clickable

- [ ] **Step 3: Verify the app launches**

Open the .app:
```bash
open dist/AudioFuse.app
```
Expected: AudioFuse window appears (may need to test manually on GUI)

- [ ] **Step 4: Add .app build artifacts to .gitignore**

Append to `.gitignore`:

```
dist/
build/
*.spec
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add PyInstaller packaging with bundled ffmpeg"
```

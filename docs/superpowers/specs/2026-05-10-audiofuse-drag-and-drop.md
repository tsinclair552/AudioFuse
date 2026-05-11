# AudioFuse — Drag & Drop Design

## Overview

Add drag-and-drop file loading to AudioFuse's clip panels, allowing users to drag WAV/MP3 files from Finder onto the panels instead of using the file dialog.

## Changes

### AudioPanel (`app/audio_panel.py`)

- Call `setAcceptDrops(True)` in `__init__`
- Override `dragEnterEvent`: accept if drop contains file URLs with `.wav` or `.mp3` extension
- Override `dropEvent`: extract file path from QUrl, call existing `load_file()`
- Reuses existing error handling in `load_file()` (try/except, user dialog)

### No Changes Needed

- AudioEngine — unchanged
- MainWindow — unchanged
- Tests — no new tests needed (UI drag-and-drop is manual-test-only)

## Implementation

~15 lines added to `app/audio_panel.py`:

```python
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
```

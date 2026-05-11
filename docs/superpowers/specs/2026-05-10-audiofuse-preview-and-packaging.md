# AudioFuse — Preview & Packaging Design

## Overview

Two additions to the AudioFuse desktop app: a Preview button to hear the combined clip before downloading, and PyInstaller packaging for a double-clickable macOS `.app`.

## Preview Button

### UI

Preview button sits in the controls toolbar between Gap and Download:

```
[Gap: OFF]  [Preview]  [Download]
```

- Disabled until both clips are loaded (same gate as Download)
- Click to play the combined clip; click again to stop playback
- Button text toggles between "Preview" and "Stop" during playback

### Implementation

- **No changes to AudioEngine** — reuses existing `concatenate()` + `normalize()` pipeline
- **Temp file approach:** combined audio is exported to a temp WAV file via `tempfile.NamedTemporaryFile`, played with `QMediaPlayer` + `QAudioOutput`
- Temp file is cleaned up on app exit

### Data Flow

1. User clicks Preview
2. `engine.concatenate(gap_seconds)` → `engine.normalize()` → `engine.export()` to temp WAV
3. `QMediaPlayer.setSource(QUrl.fromLocalFile(temp_path))` → plays
4. If user clicks Preview again during playback → stop + clean up
5. If clips change (user loads new files) → stop playback, discard temp

### New Dependencies

- `PySide6.QtMultimedia` — already part of PySide6, no pip install needed

## Packaging

### Tool

PyInstaller — the standard Python desktop app packager. Creates a standalone macOS `.app` bundle.

### What's Bundled

- Python interpreter and runtime
- PySide6 (Qt libraries)
- pydub
- ffmpeg binary (found via `which ffmpeg` at build time)
- All application code (`main.py`, `app/` package)

### Build

```bash
# Build once:
pip install pyinstaller
pyinstaller --name "AudioFuse" --windowed --add-binary "$(which ffmpeg):." main.py

# Output: dist/AudioFuse.app
```

The `--windowed` flag suppresses the terminal window on macOS.

### Dependencies Added

- `pyinstaller` to `requirements.txt`

### Optional (out of scope for now)

- Custom `.icns` app icon
- Code signing for distribution
- `.dmg` installer
- Automated CI build

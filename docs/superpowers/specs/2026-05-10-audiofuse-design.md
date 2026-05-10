# AudioFuse — Design Specification

## Overview

Desktop application that takes two audio clips as input and combines them into a single output clip, with an optional silent gap between them.

## Tech Stack

- **UI Framework:** PySide6
- **Audio Processing:** pydub (wraps ffmpeg for WAV + MP3 support)
- **Language:** Python 3.10+
- **Testing:** pytest

## Architecture

### Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `AudioEngine` | `app/audio_engine.py` | Thin pydub wrapper — `load()`, `concatenate()`, `normalize()`, `export()` |
| `AudioPanel` | `app/audio_panel.py` | Custom QWidget — file drop zone, waveform preview (QPainter), duration label |
| `MainWindow` | `app/main_window.py` | QMainWindow — HBox layout with two AudioPanels, bottom toolbar |
| `main.py` | `main.py` | Entry point, QApplication setup |

### Data Flow

1. User clicks a panel → file dialog opens → selects WAV or MP3
2. `AudioEngine.load(path)` → pydub `AudioSegment` stored in memory
3. `AudioPanel` displays waveform (downsampled amplitude peaks drawn with QPainter) + duration
4. When both clips loaded:
   - **Gap toggle off:** `AudioEngine.concatenate(clip1, clip2)` → combined segment with no gap
   - **Gap toggle on:** `AudioEngine.concatenate(clip1, clip2, gap_seconds=1)` → 1s silence inserted
5. Combined segment is peak-normalized to 0dB via `AudioEngine.normalize()`
6. **Download button:** save dialog → `AudioEngine.export(segment, path)` → file written to chosen location

### UI Layout

```
+------------------------------------------+
|  AudioFuse                                |
+---------------------------+---------------+
|  Clip 1                   |  Clip 2       |
|  [Click to load]          |  [Click]      |
|  [waveform]               |  [waveform]   |
|  0:00 / 0:00              |  0:00 / 0:00 |
+---------------------------+---------------+
|     [Gap toggle]     [ Download ]         |
+------------------------------------------+
```

- **Gap toggle:** when active, inserts 1 second of silence between the two clips in the combined output
- **Download button:** disabled until both clips are loaded

## Project Structure

```
AudioFuse/
├── main.py
├── app/
│   ├── __init__.py
│   ├── main_window.py
│   ├── audio_panel.py
│   └── audio_engine.py
├── tests/
│   └── test_audio_engine.py
└── requirements.txt
```

## Error Handling

- **Unsupported format:** message box, "Please select a WAV or MP3 file"
- **Corrupted file:** catch pydub exception, show friendly error
- **ffmpeg not installed:** detect at startup, show setup instructions dialog
- **Download with missing clip:** Download button disabled until both clips loaded

## Testing

- `pytest` for `AudioEngine`: load WAV/MP3, concatenate, silence insertion, normalization, export
- Manual testing for UI interactions (file dialogs, waveform repaint, button states)

## Future Considerations (out of scope)

- Drag-and-drop file loading
- Waveform zoom/scrub
- Additional audio formats
- LUFS loudness normalization

# AudioFuse Drag & Drop Implementation Plan

**Goal:** Add drag-and-drop file loading to AudioPanel widgets.

**Files:** Modify `app/audio_panel.py`

### Steps

- [ ] **Step 1: Add drag-and-drop event handlers**

Add after `mousePressEvent` in `app/audio_panel.py`:

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

- [ ] **Step 2: Verify syntax**

Run: `python -c "import ast; ast.parse(open('app/audio_panel.py').read()); print('OK')"`

- [ ] **Step 3: Verify tests pass**

Run: `pytest tests/ -v`

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: add drag-and-drop file loading to panels"
```

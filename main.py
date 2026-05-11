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

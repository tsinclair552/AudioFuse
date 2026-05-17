import os
import sys
import subprocess

from pydub import AudioSegment


class AudioEngine:
    def __init__(self):
        self.clip1: AudioSegment | None = None
        self.clip2: AudioSegment | None = None
        self._configure_ffmpeg_path()

    @staticmethod
    def _ffmpeg_path() -> str | None:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS, "ffmpeg")
            if os.path.isfile(path):
                return path
        return subprocess.run(["which", "ffmpeg"], capture_output=True, text=True).stdout.strip() or None

    def _configure_ffmpeg_path(self):
        path = self._ffmpeg_path()
        if path:
            AudioSegment.converter = path
            bindir = os.path.dirname(path)
            if bindir not in os.environ.get("PATH", "").split(os.pathsep):
                os.environ["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")

    def load(self, path: str, slot: int = 1) -> AudioSegment:
        segment = AudioSegment.from_file(path)
        if slot == 1:
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
        try:
            subprocess.run([AudioSegment.converter or "ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def normalize(self, segment: AudioSegment) -> AudioSegment:
        return segment.normalize()

    def export(self, segment: AudioSegment, path: str):
        segment.export(path, format=path.split('.')[-1])

    def get_waveform_data(self, segment: AudioSegment, max_points: int = 500) -> list[int]:
        raw = segment.get_array_of_samples()
        chunk_size = max(1, len(raw) // max_points)
        peaks = []
        for i in range(0, len(raw), chunk_size):
            chunk = raw[i:i + chunk_size]
            peaks.append(max(abs(s) for s in chunk))
        return peaks

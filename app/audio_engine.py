import subprocess

from pydub import AudioSegment


class AudioEngine:
    def __init__(self):
        self.clip1: AudioSegment | None = None
        self.clip2: AudioSegment | None = None

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
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
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

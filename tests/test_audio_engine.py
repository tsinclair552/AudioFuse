import os
import subprocess
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


def _generate_sine_mp3(path: str, duration_ms: int = 2000, frequency: int = 440, sample_rate: int = 44100):
    """Generate a simple sine wave MP3 file for testing using ffmpeg."""
    wav_path = path.replace('.mp3', '.wav')
    _generate_sine_wav(wav_path, duration_ms, frequency, sample_rate)
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-b:a", "128k", path],
        capture_output=True, check=True
    )
    os.unlink(wav_path)


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


def test_load_wav(engine, wav_files):
    segment = engine.load(wav_files[0])
    assert segment is not None
    assert segment.duration_seconds == 1.0


@pytest.fixture
def mp3_file():
    fd, path = tempfile.mkstemp(suffix='.mp3')
    os.close(fd)
    _generate_sine_mp3(path, duration_ms=1000, frequency=440)
    yield path
    os.unlink(path)


def test_load_mp3(engine, mp3_file):
    segment = engine.load(mp3_file)
    assert segment is not None
    assert segment.duration_seconds == pytest.approx(1.0, rel=0.01)


def test_concatenate_no_gap(engine, wav_files):
    engine.load(wav_files[0], slot=1)
    engine.load(wav_files[1], slot=2)
    result = engine.concatenate()
    assert result.duration_seconds == pytest.approx(2.0, rel=0.01)


def test_concatenate_with_gap(engine, wav_files):
    engine.load(wav_files[0], slot=1)
    engine.load(wav_files[1], slot=2)
    result = engine.concatenate(gap_seconds=1.0)
    assert result.duration_seconds == pytest.approx(3.0, rel=0.01)


def test_export_wav(engine, wav_files, tmp_path):
    engine.load(wav_files[0], slot=1)
    engine.load(wav_files[1], slot=2)
    combined = engine.concatenate()
    out = tmp_path / "combined.wav"
    engine.export(combined, str(out))
    assert out.exists()
    assert out.stat().st_size > 0


def test_get_waveform_data(engine, wav_files):
    segment = engine.load(wav_files[0])
    data = engine.get_waveform_data(segment)
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(p, int) for p in data)


def test_ffmpeg_available(engine):
    result = engine.ffmpeg_available()
    assert isinstance(result, bool)


def test_concatenate_raises_without_clips(engine):
    with pytest.raises(ValueError, match="Both clips must be loaded"):
        engine.concatenate()


def test_normalize(engine, wav_files):
    engine.load(wav_files[0], slot=1)
    engine.load(wav_files[1], slot=2)
    combined = engine.concatenate()
    normalized = engine.normalize(combined)
    assert normalized.duration_seconds == pytest.approx(2.0, rel=0.01)
    assert normalized.max_dBFS > -1.0

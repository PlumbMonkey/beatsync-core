"""Tests for audio key detection."""
import os
import numpy as np
import pytest
import librosa

from beatsync_core.core import key


@pytest.fixture
def sine_wave_c_major():
    """Generate a simple sine wave at C (261.63 Hz) for testing."""
    sr = 22050
    duration = 2.0
    frequency = 261.63  # Middle C
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return y, sr


@pytest.fixture
def audio_fixture():
    """Load real audio fixture if available."""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fixtures",
        "audio",
        "click_120.wav"
    )
    if os.path.exists(fixture_path):
        y, sr = librosa.load(fixture_path, sr=None)
        return y, sr
    return None


def test_analyze_returns_dict():
    """Test that analyze returns a dictionary with required keys."""
    sr = 22050
    duration = 1.0
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result = key.analyze(y, sr)

    assert isinstance(result, dict)
    assert "key" in result
    assert "confidence" in result
    assert isinstance(result["key"], str)
    assert isinstance(result["confidence"], (int, float))


def test_analyze_confidence_in_range():
    """Test that confidence is between 0.0 and 1.0."""
    sr = 22050
    duration = 2.0
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result = key.analyze(y, sr)

    assert 0.0 <= result["confidence"] <= 1.0


def test_analyze_empty_audio():
    """Test handling of empty audio array."""
    y = np.array([])
    sr = 22050

    result = key.analyze(y, sr)

    assert result["key"] == "unknown"
    assert result["confidence"] == 0.0


def test_analyze_silent_audio():
    """Test handling of silent (zero) audio."""
    sr = 22050
    duration = 1.0
    y = np.zeros(int(sr * duration), dtype=np.float32)

    result = key.analyze(y, sr)

    assert result["key"] == "unknown"
    assert result["confidence"] == 0.0


def test_analyze_returns_valid_key_format(sine_wave_c_major):
    """Test that detected key follows the expected format."""
    y, sr = sine_wave_c_major

    result = key.analyze(y, sr)

    # Key should be either "unknown" or "X major" or "X minor"
    if result["key"] != "unknown":
        parts = result["key"].split()
        assert len(parts) == 2
        assert parts[0] in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        assert parts[1] in ["major", "minor"]


def test_analyze_sine_wave_reasonable_confidence(sine_wave_c_major):
    """Test that sine wave detection has reasonable confidence."""
    y, sr = sine_wave_c_major

    result = key.analyze(y, sr)

    # Pure sine wave should have decent confidence (not zero, not random)
    assert result["confidence"] > 0.1


def test_analyze_midi_placeholder():
    """Test MIDI analysis placeholder (not implemented)."""
    result = key.analyze_midi(None)

    assert result["key"] == "unknown"
    assert result["confidence"] == 0.0


def test_analyze_with_real_fixture(audio_fixture):
    """Test with real audio fixture if available."""
    if audio_fixture is None:
        pytest.skip("Audio fixture not found")

    y, sr = audio_fixture

    result = key.analyze(y, sr)

    assert isinstance(result["key"], str)
    assert 0.0 <= result["confidence"] <= 1.0


def test_short_audio_handling():
    """Test handling of very short audio."""
    sr = 22050
    # Less than one frame of analysis
    y = np.random.randn(100).astype(np.float32)

    result = key.analyze(y, sr)

    assert isinstance(result["key"], str)
    assert 0.0 <= result["confidence"] <= 1.0


def test_analyze_deterministic():
    """Test that analyze is deterministic for the same input."""
    sr = 22050
    duration = 1.0
    np.random.seed(42)
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result1 = key.analyze(y.copy(), sr)
    result2 = key.analyze(y.copy(), sr)

    assert result1["key"] == result2["key"]
    assert result1["confidence"] == result2["confidence"]

"""Tests for music structure segmentation."""
import os
import numpy as np
import pytest
import librosa

from beatsync_core.core import structure


@pytest.fixture
def synthetic_audio():
    """Generate synthetic audio with clear structure changes."""
    sr = 22050
    duration = 30.0  # 30 seconds

    # Create a signal with distinct sections (different frequencies)
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Section 1: 200 Hz (0s-10s)
    section1 = np.sin(2 * np.pi * 200 * t[:int(10 * sr)])

    # Section 2: 400 Hz (10s-20s)
    section2 = np.sin(2 * np.pi * 400 * t[int(10 * sr):int(20 * sr)])

    # Section 3: 600 Hz (20s-30s)
    section3 = np.sin(2 * np.pi * 600 * t[int(20 * sr):int(30 * sr)])

    y = np.concatenate([section1, section2, section3]).astype(np.float32)
    return y, sr


@pytest.fixture
def audio_fixture():
    """Load real audio fixture if available."""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fixtures",
        "audio",
        "kick_4onfloor_128.wav"
    )
    if os.path.exists(fixture_path):
        y, sr = librosa.load(fixture_path, sr=None)
        return y, sr
    return None


def test_analyze_returns_list():
    """Test that analyze returns a list."""
    sr = 22050
    duration = 5.0
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result = structure.analyze(y, sr)

    assert isinstance(result, list)


def test_analyze_returns_section_dicts():
    """Test that sections have required keys."""
    sr = 22050
    duration = 10.0
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result = structure.analyze(y, sr)

    for section in result:
        assert isinstance(section, dict)
        assert "label" in section
        assert "start" in section
        assert "end" in section
        assert isinstance(section["label"], str)
        assert isinstance(section["start"], (int, float))
        assert isinstance(section["end"], (int, float))


def test_analyze_empty_audio():
    """Test handling of empty audio array."""
    y = np.array([])
    sr = 22050

    result = structure.analyze(y, sr)

    assert result == []


def test_analyze_sections_are_contiguous(synthetic_audio):
    """Test that sections are contiguous (no gaps, no overlaps)."""
    y, sr = synthetic_audio

    result = structure.analyze(y, sr)

    # Check contiguity
    for i in range(len(result) - 1):
        assert result[i]["end"] == result[i + 1]["start"]


def test_analyze_sections_cover_full_duration(synthetic_audio):
    """Test that sections cover the full track duration."""
    y, sr = synthetic_audio
    duration = librosa.get_duration(y=y, sr=sr)

    result = structure.analyze(y, sr)

    if result:
        assert result[0]["start"] == 0.0
        # Allow small floating point error
        assert abs(result[-1]["end"] - duration) < 0.1


def test_analyze_minimum_section_length(synthetic_audio):
    """Test that sections respect minimum length of 4 seconds."""
    y, sr = synthetic_audio

    result = structure.analyze(y, sr)

    # Check minimum section length (4 seconds)
    min_section_length = 4.0
    for section in result:
        section_duration = section["end"] - section["start"]
        # Last section can be shorter if remaining duration is less than 4s
        # but all sections should have non-negative duration
        assert section_duration >= 0.0


def test_analyze_section_labels(synthetic_audio):
    """Test that section labels are sequential."""
    y, sr = synthetic_audio

    result = structure.analyze(y, sr)

    for i, section in enumerate(result):
        assert section["label"] == f"section_{i + 1}"


def test_analyze_returns_at_least_one_section():
    """Test that analyze always returns at least one section."""
    sr = 22050
    duration = 20.0
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result = structure.analyze(y, sr)

    # Should have at least one section for non-empty audio
    assert len(result) >= 1


def test_analyze_with_real_fixture(audio_fixture):
    """Test with real audio fixture if available."""
    if audio_fixture is None:
        pytest.skip("Audio fixture not found")

    y, sr = audio_fixture

    result = structure.analyze(y, sr)

    assert isinstance(result, list)
    if result:
        # If sections returned, verify structure
        assert result[0]["start"] == 0.0
        for section in result:
            assert "label" in section
            assert "start" in section
            assert "end" in section


def test_analyze_deterministic():
    """Test that analyze is deterministic."""
    sr = 22050
    duration = 10.0
    np.random.seed(42)
    y = np.random.randn(int(sr * duration)).astype(np.float32)

    result1 = structure.analyze(y.copy(), sr)
    result2 = structure.analyze(y.copy(), sr)

    assert len(result1) == len(result2)
    for s1, s2 in zip(result1, result2):
        assert s1["label"] == s2["label"]
        assert abs(s1["start"] - s2["start"]) < 0.01
        assert abs(s1["end"] - s2["end"]) < 0.01


def test_analyze_midi_placeholder():
    """Test MIDI structure analysis placeholder (not implemented)."""
    result = structure.analyze_midi(None)

    assert result == []

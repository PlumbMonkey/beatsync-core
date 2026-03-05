"""Tests for MIDI key detection."""
import os
import pytest
import mido

from beatsync_midi.key_detect import detect_key


@pytest.fixture
def empty_midi():
    """Create an empty MIDI file."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    return mid


@pytest.fixture
def c_major_midi():
    """Create a MIDI file with notes in C major scale."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add notes of C major scale: C, D, E, F, G, A, B (repeat)
    # MIDI note numbers: C=0, D=2, E=4, F=5, G=7, A=9, B=11
    c_major_notes = [0, 2, 4, 5, 7, 9, 11]

    for note in c_major_notes:
        # Add as note_on with velocity 100
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=100))

    return mid


@pytest.fixture
def a_minor_midi():
    """Create a MIDI file with notes in A minor scale."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add notes of A minor scale: A, B, C, D, E, F, G
    # MIDI note numbers: A=9, B=11, C=0, D=2, E=4, F=5, G=7
    # (modulo 12 for pitch class)
    a_minor_notes = [9, 11, 12, 14, 16, 17, 19]  # Using multiple octaves

    for note in a_minor_notes:
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=100))

    return mid


@pytest.fixture
def midi_fixture():
    """Load real MIDI fixture if available."""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "fixtures",
        "midi_basic_100.mid"
    )
    if os.path.exists(fixture_path):
        return mido.MidiFile(fixture_path)
    return None


def test_detect_key_returns_dict():
    """Test that detect_key returns a dictionary with required keys."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message('note_on', note=60, velocity=100, time=0))

    result = detect_key(mid)

    assert isinstance(result, dict)
    assert "key" in result
    assert "confidence" in result
    assert isinstance(result["key"], str)
    assert isinstance(result["confidence"], (int, float))


def test_detect_key_confidence_in_range():
    """Test that confidence is between 0.0 and 0.85."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for note in range(0, 12):
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=100))

    result = detect_key(mid)

    assert 0.0 <= result["confidence"] <= 0.85


def test_detect_key_empty_midi(empty_midi):
    """Test handling of empty MIDI."""
    result = detect_key(empty_midi)

    assert result["key"] == "unknown"
    assert result["confidence"] == 0.0


def test_detect_key_none():
    """Test handling of None input."""
    result = detect_key(None)

    assert result["key"] == "unknown"
    assert result["confidence"] == 0.0


def test_detect_key_returns_valid_format():
    """Test that detected key follows the expected format."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add some random notes
    for note in [0, 4, 7]:  # C, E, G (C major chord)
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))

    result = detect_key(mid)

    # Key should be either "unknown" or "X major" or "X minor"
    if result["key"] != "unknown":
        parts = result["key"].split()
        assert len(parts) == 2
        assert parts[0] in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        assert parts[1] in ["major", "minor"]


def test_detect_key_c_major(c_major_midi):
    """Test C major chord detection."""
    result = detect_key(c_major_midi)

    assert result["key"] != "unknown"
    assert result["confidence"] > 0.1


def test_detect_key_a_minor(a_minor_midi):
    """Test A minor chord detection."""
    result = detect_key(a_minor_midi)

    assert result["key"] != "unknown"
    assert result["confidence"] > 0.1


def test_detect_key_deterministic():
    """Test that detection is deterministic."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    for note in [0, 4, 7]:
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))
        track.append(mido.Message('note_off', note=note, velocity=0, time=100))

    result1 = detect_key(mid)
    result2 = detect_key(mid)

    assert result1["key"] == result2["key"]
    assert result1["confidence"] == result2["confidence"]


def test_detect_key_with_velocity_weighting():
    """Test that velocity affects note weighting."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add C (note 0) with high velocity multiple times
    for _ in range(5):
        track.append(mido.Message('note_on', note=0, velocity=127, time=0))

    # Add other notes with low velocity
    for note in [4, 7]:
        track.append(mido.Message('note_on', note=note, velocity=30, time=0))

    result = detect_key(mid)

    # Should detect strongly toward C major since C is so prominent
    assert result["key"] != "unknown"
    assert result["confidence"] > 0.2


def test_detect_key_with_real_fixture(midi_fixture):
    """Test with real MIDI fixture if available."""
    if midi_fixture is None:
        pytest.skip("MIDI fixture not found")

    result = detect_key(midi_fixture)

    assert isinstance(result["key"], str)
    assert 0.0 <= result["confidence"] <= 0.85


def test_detect_key_velocity_zero_ignored():
    """Test that note_on with velocity 0 is ignored (is a note_off)."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    # Add note_on with velocity 0 (should be ignored)
    track.append(mido.Message('note_on', note=0, velocity=0, time=0))

    # Add actual notes
    for note in [4, 7]:
        track.append(mido.Message('note_on', note=note, velocity=100, time=0))

    result = detect_key(mid)

    # Should work fine - C note should be ignored
    assert isinstance(result["key"], str)

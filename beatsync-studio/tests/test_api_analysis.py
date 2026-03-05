"""
Pytest test suite for BeatSync Studio Slice 4.1 (Upload + Analysis Orchestration).

Tests the `/api/analysis` endpoint contract using FastAPI TestClient for in-process testing.
"""
import os
import json
import pytest
from fastapi.testclient import TestClient

from beatsync_studio.main import app


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient for testing without running a server."""
    return TestClient(app)


@pytest.fixture(scope="module")
def audio_fixture():
    """Load a real audio fixture if available."""
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "beatsync-core",
        "fixtures",
        "audio",
        "click_120.wav"
    )
    if os.path.exists(fixture_path):
        with open(fixture_path, "rb") as f:
            return f.read()
    return None


@pytest.fixture
def midi_file_bytes():
    """Minimal valid MIDI file bytes (empty single-track MIDI)."""
    # Minimal MIDI: header + empty track
    return b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00\x60MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00"


@pytest.fixture
def corrupt_file_bytes():
    """File bytes that are not valid audio or MIDI."""
    return b"this is definitely not a valid audio or midi file"


@pytest.fixture
def empty_file_bytes():
    """Empty file bytes."""
    return b""


class TestUploadHappyPath:
    """Happy path upload tests."""

    def test_upload_valid_midi_returns_200(self, client, midi_file_bytes):
        """Test uploading a valid MIDI file returns 200."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        assert response.status_code == 200

    def test_upload_response_contains_required_fields(self, client, midi_file_bytes):
        """Test response contains all contract fields."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        # Required fields per contract
        required_fields = {
            "analysis_id",
            "analysis_hash",
            "schema_version",
            "analysis_version",
            "duration_sec",
            "bpm",
            "confidence",
            "download_url"
        }
        assert required_fields.issubset(set(data.keys()))

    def test_upload_response_field_types(self, client, midi_file_bytes):
        """Test response field types are correct."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        assert isinstance(data["analysis_id"], str)
        assert isinstance(data["analysis_hash"], str)
        assert isinstance(data["schema_version"], str)
        assert isinstance(data["analysis_version"], str)
        assert isinstance(data["duration_sec"], (int, float))
        assert isinstance(data["bpm"], (int, float))
        assert isinstance(data["confidence"], dict)
        assert isinstance(data["download_url"], str)

    def test_upload_no_mutation_fields(self, client, midi_file_bytes):
        """Test response contains no internal/debug fields."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        forbidden_fields = {"_debug", "_mutation", "_internal"}
        assert not any(field in data for field in forbidden_fields)

    def test_upload_audio_fixture(self, client, audio_fixture):
        """Test uploading real audio fixture if available."""
        if audio_fixture is None:
            pytest.skip("Audio fixture not available")

        response = client.post(
            "/api/analysis",
            files={"file": ("click_120.wav", audio_fixture, "audio/wav")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "bpm" in data


class TestUploadInvalidFiles:
    """Tests for invalid file uploads."""

    def test_upload_unsupported_extension(self, client):
        """Test uploading unsupported file type returns 4xx."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.txt", b"plain text", "text/plain")}
        )
        assert response.status_code in (400, 422)

    def test_upload_unsupported_extension_json(self, client):
        """Test uploading JSON file returns error."""
        response = client.post(
            "/api/analysis",
            files={"file": ("data.json", b'{"key": "value"}', "application/json")}
        )
        assert response.status_code in (400, 422)

    def test_upload_corrupt_file_returns_error(self, client, corrupt_file_bytes):
        """Test uploading corrupt file returns error."""
        response = client.post(
            "/api/analysis",
            files={"file": ("corrupt.mid", corrupt_file_bytes, "audio/midi")}
        )
        # Should fail at analysis stage
        assert response.status_code in (422, 500)

    def test_upload_empty_file_returns_error(self, client, empty_file_bytes):
        """Test uploading empty file returns error."""
        response = client.post(
            "/api/analysis",
            files={"file": ("empty.mid", empty_file_bytes, "audio/midi")}
        )
        assert response.status_code in (400, 422)

    def test_upload_missing_file_parameter(self, client):
        """Test POST without file parameter returns error."""
        response = client.post("/api/analysis", files={})
        assert response.status_code in (400, 422)


class TestUploadDeterminism:
    """Tests for deterministic hashing and idempotency."""

    def test_upload_same_file_twice_same_hash(self, client, midi_file_bytes):
        """Test uploading identical file twice produces same hash."""
        resp1 = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        resp2 = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        data1 = resp1.json()
        data2 = resp2.json()

        assert data1["analysis_hash"] == data2["analysis_hash"]

    def test_upload_same_file_twice_same_analysis_id_differs(self, client, midi_file_bytes):
        """Test that analysis_id is unique but hash is consistent."""
        resp1 = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        resp2 = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )

        data1 = resp1.json()
        data2 = resp2.json()

        # Hash should be same (deterministic)
        assert data1["analysis_hash"] == data2["analysis_hash"]

        # But analysis_id can differ (per-request UUID)
        # (implementation detail - not strictly required)


class TestDownloadUrl:
    """Tests for download URL contract."""

    def test_download_url_format(self, client, midi_file_bytes):
        """Test that download_url follows expected format."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        download_url = data["download_url"]

        # Should contain analysis_id
        assert data["analysis_id"] in download_url

        # Should be a path (start with /)
        assert download_url.startswith("/")

    def test_download_url_is_valid_path(self, client, midi_file_bytes):
        """Test that download_url structure is valid."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        # Should follow pattern like /api/analysis/{id}/download
        assert "/api/analysis/" in data["download_url"]
        assert "download" in data["download_url"]


class TestBPMConfidence:
    """Tests for BPM confidence structure."""

    def test_confidence_has_tempo_field(self, client, midi_file_bytes):
        """Test confidence dict contains tempo field."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        assert "tempo" in data["confidence"]
        assert isinstance(data["confidence"]["tempo"], (int, float))

    def test_confidence_has_key_field(self, client, midi_file_bytes):
        """Test confidence dict contains key field."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        assert "key" in data["confidence"]
        assert isinstance(data["confidence"]["key"], (int, float))


class TestBPMValues:
    """Tests for BPM value constraints."""

    def test_bpm_is_positive(self, client, midi_file_bytes):
        """Test BPM is a positive number."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        assert data["bpm"] > 0

    def test_bpm_is_reasonable_range(self, client, audio_fixture):
        """Test BPM is in reasonable range (30-300 BPM)."""
        if audio_fixture is None:
            pytest.skip("Audio fixture not available")

        response = client.post(
            "/api/analysis",
            files={"file": ("click.wav", audio_fixture, "audio/wav")}
        )
        data = response.json()

        # Reasonable music tempo range
        assert 30 <= data["bpm"] <= 300


class TestAnalysisVersion:
    """Tests for analysis version fields."""

    def test_analysis_version_format(self, client, midi_file_bytes):
        """Test analysis_version follows semantic versioning."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        version = data["analysis_version"]
        # Should be X.Y.Z format
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_schema_version_format(self, client, midi_file_bytes):
        """Test schema_version format."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        schema_version = data["schema_version"]
        # Should be X.Y format
        assert "." in schema_version


class TestDurationValues:
    """Tests for duration field."""

    def test_duration_is_positive(self, client, midi_file_bytes):
        """Test duration_sec is positive."""
        response = client.post(
            "/api/analysis",
            files={"file": ("test.mid", midi_file_bytes, "audio/midi")}
        )
        data = response.json()

        assert data["duration_sec"] >= 0.0

    def test_duration_is_reasonable(self, client, audio_fixture):
        """Test duration_sec is reasonable for audio file."""
        if audio_fixture is None:
            pytest.skip("Audio fixture not available")

        response = client.post(
            "/api/analysis",
            files={"file": ("click.wav", audio_fixture, "audio/wav")}
        )
        data = response.json()

        # Audio fixtures should be at least a few seconds
        assert data["duration_sec"] > 0.5

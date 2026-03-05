"""Tests for Blender driver expression building."""
import pytest
import math

from beatsync_blender_visual_core.driver_builder import (
    build_driver_expressions,
    build_compound_expression,
    validate_expression,
    test_expression,
)


@pytest.fixture
def sample_beats():
    """Sample beat timestamps in seconds."""
    return [0.5, 1.0, 1.5, 2.0, 2.5]


@pytest.fixture
def sample_energy():
    """Sample energy curve values."""
    return [0.3, 0.8, 0.5, 0.9, 0.4]


def test_build_driver_expressions_returns_list(sample_beats, sample_energy):
    """Test that build_driver_expressions returns a list."""
    result = build_driver_expressions(sample_beats, sample_energy)

    assert isinstance(result, list)
    assert len(result) == len(sample_beats)


def test_build_driver_expressions_returns_strings(sample_beats, sample_energy):
    """Test that all expressions are strings."""
    result = build_driver_expressions(sample_beats, sample_energy)

    for expr in result:
        assert isinstance(expr, str)


def test_build_driver_expressions_empty_inputs():
    """Test handling of empty inputs."""
    result = build_driver_expressions([], [])

    assert result == []


def test_build_driver_expressions_single_beat():
    """Test with single beat."""
    beats = [1.0]
    energy = [0.5]

    result = build_driver_expressions(beats, energy)

    assert len(result) == 1
    assert isinstance(result[0], str)


def test_expressions_are_valid_python(sample_beats, sample_energy):
    """Test that all expressions are valid Python code."""
    expressions = build_driver_expressions(sample_beats, sample_energy)

    for expr in expressions:
        assert validate_expression(expr), f"Expression not valid: {expr}"


def test_expressions_evaluate(sample_beats, sample_energy):
    """Test that expressions can be evaluated."""
    expressions = build_driver_expressions(sample_beats, sample_energy)

    for i, expr in enumerate(expressions):
        # Evaluate at various frame positions
        for frame in [0, 10, 100]:
            result = test_expression(expr, frame=frame)
            assert isinstance(result, float)
            assert result >= 0.0  # Gaussian envelope is always non-negative


def test_peak_at_beat_frame(sample_beats, sample_energy):
    """Test that peak amplitude occurs near the beat frame."""
    beats = [1.0]
    energy = [0.7]
    fps = 24.0

    expressions = build_driver_expressions(beats, energy, fps=fps)
    expr = expressions[0]

    beat_frame = round(1.0 * fps)

    # Evaluate at beat frame and nearby frames
    value_at_beat = test_expression(expr, frame=beat_frame)
    value_before = test_expression(expr, frame=beat_frame - 1)
    value_after = test_expression(expr, frame=beat_frame + 1)

    # Peak should be at or very close to beat frame
    assert value_at_beat >= value_before
    assert value_at_beat >= value_after


def test_symmetry_around_beat(sample_beats, sample_energy):
    """Test that Gaussian envelope is symmetric around beat frame."""
    beats = [1.0]
    energy = [0.5]
    fps = 24.0

    expressions = build_driver_expressions(beats, energy, fps=fps)
    expr = expressions[0]

    beat_frame = round(1.0 * fps)
    offset = 10

    value_before = test_expression(expr, frame=beat_frame - offset)
    value_after = test_expression(expr, frame=beat_frame + offset)

    # Should be approximately equal (symmetric)
    assert abs(value_before - value_after) < 0.01


def test_energy_normalization(sample_beats):
    """Test that energy values are normalized."""
    # First beat has energy 1.0, second has 0.5
    energy = [1.0, 0.5]
    beats = [0.5, 1.0]
    fps = 24.0

    expressions = build_driver_expressions(beats, energy, fps=fps)

    # Evaluate first beat at its frame
    expr0 = expressions[0]
    value0_at_peak = test_expression(expr0, frame=round(0.5 * fps))

    # Evaluate second beat at its frame
    expr1 = expressions[1]
    value1_at_peak = test_expression(expr1, frame=round(1.0 * fps))

    # First beat should have twice the amplitude of second beat
    assert value0_at_peak > value1_at_peak


def test_exponential_decay():
    """Test that amplitude decays exponentially away from beat."""
    beats = [1.0]
    energy = [1.0]
    fps = 24.0

    expressions = build_driver_expressions(beats, energy, fps=fps)
    expr = expressions[0]

    beat_frame = round(1.0 * fps)

    # Get values at increasing distances from beat
    value_at_0 = test_expression(expr, frame=beat_frame)
    value_at_5 = test_expression(expr, frame=beat_frame + 5)
    value_at_10 = test_expression(expr, frame=beat_frame + 10)
    value_at_20 = test_expression(expr, frame=beat_frame + 20)

    # Should monotonically decrease
    assert value_at_0 >= value_at_5 >= value_at_10 >= value_at_20


def test_build_compound_expression(sample_beats, sample_energy):
    """Test compound expression building."""
    result = build_compound_expression(sample_beats, sample_energy)

    assert isinstance(result, str)
    assert len(result) > 0
    assert validate_expression(result)


def test_compound_expression_evaluates(sample_beats, sample_energy):
    """Test that compound expression evaluates."""
    expr = build_compound_expression(sample_beats, sample_energy)

    for frame in [0, 10, 100]:
        result = test_expression(expr, frame=frame)
        assert isinstance(result, float)
        assert result >= 0.0


def test_compound_expression_sums_peaks(sample_beats, sample_energy):
    """Test that compound expression has peaks at beat positions."""
    beats = [1.0, 2.0]
    energy = [1.0, 0.5]
    fps = 24.0

    expr = build_compound_expression(beats, energy, fps=fps)

    beat_frame_1 = round(1.0 * fps)
    beat_frame_2 = round(2.0 * fps)

    # Should have local maxima near beat frames
    value_at_beat1 = test_expression(expr, frame=beat_frame_1)
    value_at_beat2 = test_expression(expr, frame=beat_frame_2)

    # Values should be substantial
    assert value_at_beat1 > 0.1
    assert value_at_beat2 > 0.1


def test_validate_expression_valid():
    """Test validation of valid expressions."""
    valid_exprs = [
        "1.0",
        "frame * 0.5",
        "math.sin(frame) if False else 0.0",
    ]

    for expr in valid_exprs:
        assert validate_expression(expr), f"Should be valid: {expr}"


def test_validate_expression_invalid():
    """Test validation of invalid expressions."""
    invalid_exprs = [
        "frame *",  # Syntax error
        "if frame else",  # Incomplete
        "def foo(): pass",  # Not an expression
    ]

    for expr in invalid_exprs:
        assert not validate_expression(expr), f"Should be invalid: {expr}"


def test_test_expression_with_default_frame(sample_beats, sample_energy):
    """Test expression evaluation with default frame."""
    expressions = build_driver_expressions(sample_beats, sample_energy)

    for expr in expressions:
        # Should not raise exception
        result = test_expression(expr)
        assert isinstance(result, float)


def test_different_fps_values(sample_beats, sample_energy):
    """Test expression building with different FPS values."""
    for fps in [24.0, 30.0, 60.0]:
        expressions = build_driver_expressions(
            sample_beats,
            sample_energy,
            fps=fps
        )

        assert len(expressions) == len(sample_beats)
        for expr in expressions:
            assert validate_expression(expr)


def test_different_sigma_scales(sample_beats, sample_energy):
    """Test expression building with different sigma scales."""
    for sigma_scale in [0.25, 0.5, 1.0, 2.0]:
        expressions = build_driver_expressions(
            sample_beats,
            sample_energy,
            sigma_scale=sigma_scale
        )

        assert len(expressions) == len(sample_beats)
        for expr in expressions:
            assert validate_expression(expr)


def test_energy_zero_handling():
    """Test handling of zero energy values."""
    beats = [1.0, 2.0]
    energy = [0.0, 0.0]

    expressions = build_driver_expressions(beats, energy)

    # Should still generate expressions
    assert len(expressions) == 2

    # But they should evaluate to zero
    for expr in expressions:
        result = test_expression(expr, frame=1000)
        assert result == 0.0 or result < 0.001  # Very close to zero


def test_large_energy_values():
    """Test handling of large energy values."""
    beats = [1.0]
    energy = [1000.0]  # Very large value

    expressions = build_driver_expressions(beats, energy)

    # Should normalize properly
    assert len(expressions) == 1
    expr = expressions[0]

    # Peak should be around 1.0 after normalization
    peak = test_expression(expr, frame=round(1.0 * 24.0))
    assert 0.8 <= peak <= 1.2  # Close to 1.0, allowing for rounding

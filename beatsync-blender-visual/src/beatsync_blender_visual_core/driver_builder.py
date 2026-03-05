"""Smooth Blender driver expression builder using Gaussian envelopes."""
import math


def build_driver_expressions(
    beats: list,
    energy_curve: list,
    sr: int = 22050,
    fps: float = 24.0,
    sigma_scale: float = 0.5
) -> list:
    """
    Build smooth Blender driver expressions using Gaussian envelopes.

    Generates a driver expression for each beat that creates a smooth
    Gaussian envelope centered at the beat frame, with amplitude
    driven by the normalized energy curve.

    Args:
        beats: List of beat timestamps in seconds (floats).
        energy_curve: List of energy values (floats, 0.0-1.0 range).
        sr: Sampling rate of the audio (not directly used, for context).
        fps: Frames per second for the Blender timeline.
        sigma_scale: Scaling factor for the Gaussian sigma (default 0.5 beat width).

    Returns:
        List of driver expression strings, one per beat.
        Each expression is valid Python code for Blender's SCRIPTED driver type.

    Note:
        Energy values are normalized to 0.0-1.0 range. The expression
        uses frame as the context variable and evaluates to a float amplitude.
    """
    if not beats or not energy_curve:
        return []

    # Compute beat duration in frames (assuming uniform beats)
    beat_interval_frames = None
    if len(beats) > 1:
        beat_interval_seconds = beats[1] - beats[0]
        beat_interval_frames = beat_interval_seconds * fps
    else:
        beat_interval_frames = fps * 0.5  # Default to 0.5 seconds

    # Normalize energy curve to [0.0, 1.0]
    if max(energy_curve) > 0:
        energy_normalized = [e / max(energy_curve) for e in energy_curve]
    else:
        energy_normalized = [0.0] * len(energy_curve)

    expressions = []

    for i, beat_time in enumerate(beats):
        # Convert beat time to frame number
        beat_frame = round(beat_time * fps)

        # Get energy amplitude for this beat (if available)
        energy_amplitude = 1.0
        if i < len(energy_normalized):
            energy_amplitude = energy_normalized[i]
        else:
            # Interpolate or use last value
            energy_amplitude = energy_normalized[-1] if energy_normalized else 1.0

        # Compute sigma (width of Gaussian)
        # Use half beat duration for a reasonable decay
        sigma = beat_interval_frames / 2.0 * sigma_scale

        # Ensure sigma is not zero
        if sigma <= 0:
            sigma = fps * 0.25  # Default to 0.25 seconds

        # Build Gaussian envelope expression
        # Form: amplitude * exp(-((frame - beat_frame)^2) / (2 * sigma^2))
        expr = (
            f"{energy_amplitude:.4f} * "
            f"__import__('math').exp(-((frame - {beat_frame}) ** 2) / (2 * {sigma:.2f} ** 2))"
        )

        expressions.append(expr)

    return expressions


def build_compound_expression(
    beats: list,
    energy_curve: list,
    sr: int = 22050,
    fps: float = 24.0,
    sigma_scale: float = 0.5
) -> str:
    """
    Build a single compound Blender driver expression combining all beats.

    This creates one expression that sums the envelopes of all beats,
    useful for modulating multiple object properties simultaneously.

    Args:
        beats: List of beat timestamps in seconds.
        energy_curve: List of energy values (floats).
        sr: Sampling rate of the audio.
        fps: Frames per second for the Blender timeline.
        sigma_scale: Scaling factor for Gaussian sigma.

    Returns:
        A single driver expression string that sums all beat envelopes.
    """
    expressions = build_driver_expressions(
        beats=beats,
        energy_curve=energy_curve,
        sr=sr,
        fps=fps,
        sigma_scale=sigma_scale
    )

    if not expressions:
        return "0.0"

    # Combine expressions with addition (sum of all beat envelopes)
    compound = " + ".join(f"({e})" for e in expressions)

    return compound


def validate_expression(expr: str) -> bool:
    """
    Validate that a driver expression is valid Python.

    Args:
        expr: Driver expression string.

    Returns:
        True if the expression compiles successfully, False otherwise.
    """
    try:
        compile(expr, '<string>', 'eval')
        return True
    except SyntaxError:
        return False


def test_expression(expr: str, frame: int = 0) -> float:
    """
    Test a driver expression by evaluating it with a sample frame value.

    Args:
        expr: Driver expression string.
        frame: Frame number to use for evaluation (default 0).

    Returns:
        The result of evaluating the expression (should be a float).

    Raises:
        Exception if the expression cannot be evaluated.
    """
    try:
        # Provide 'frame' variable for expression evaluation
        result = eval(expr, {"__builtins__": {}}, {"frame": frame})
        return float(result)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expr}' at frame {frame}: {str(e)}")

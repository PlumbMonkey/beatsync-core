# BeatSync Blender Visual

## Structure

- `src/beatsync_blender_visual_core/`: Pure Python core logic, unit-testable, no `bpy` imports.
- `addon/beatsync_blender_visual/`: Blender add-on glue, imports `bpy` and wraps core logic.

## Development

- Install core package for development:
  ```
  pip install -e .
  ```
- Run unit tests (core only):
  ```
  pytest
  ```
- Blender integration tests must be run with Blender, not pytest alone.

## Blender Smoke Test

- Use `scripts/smoke_blender.py` to run a headless Blender integration test.

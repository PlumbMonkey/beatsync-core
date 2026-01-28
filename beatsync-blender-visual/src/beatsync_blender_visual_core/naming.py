def normalize_marker_name(name):
	"""Normalize marker names for Blender (e.g., strip/replace illegal chars)."""
	# For now, just strip whitespace and truncate to 64 chars (Blender limit)
	return name.strip()[:64]

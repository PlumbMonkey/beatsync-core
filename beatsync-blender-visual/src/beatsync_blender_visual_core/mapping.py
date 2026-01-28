def marker_json_to_blender(marker):
	"""Map a marker dict from JSON to Blender marker args."""
	# This is where you could add more mapping logic (e.g., name normalization)
	return {
		"name": marker["name"],
		"frame": marker["frame"]
	}

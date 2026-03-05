/**
 * EDL (Edit Decision List) export utility
 * Generates CMX 3600 format EDL files for DaVinci Resolve, Premiere Pro, Final Cut Pro
 */

/**
 * Format a timestamp (seconds) into EDL timecode format HH:MM:SS:FF
 *
 * @param {number} seconds - Timestamp in seconds
 * @param {number} fps - Frames per second
 * @returns {string} - Timecode in HH:MM:SS:FF format
 */
function formatTimecode(seconds, fps) {
  const totalFrames = Math.round(seconds * fps)

  const hours = Math.floor(totalFrames / (fps * 3600))
  const minutes = Math.floor((totalFrames % (fps * 3600)) / (fps * 60))
  const secs = Math.floor((totalFrames % (fps * 60)) / fps)
  const frames = totalFrames % fps

  return [
    String(hours).padStart(2, '0'),
    String(minutes).padStart(2, '0'),
    String(secs).padStart(2, '0'),
    String(frames).padStart(2, '0'),
  ].join(':')
}

/**
 * Generate CMX 3600 EDL content for beat marks
 *
 * @param {number[]} beats - Array of beat timestamps in seconds
 * @param {number} fps - Frame rate (24, 25, 29.97, or 30)
 * @param {string} title - Project title (optional)
 * @returns {string} - EDL content ready for download
 */
export function generateEdl(beats, fps = 30, title = 'BeatSync Export') {
  if (!beats || beats.length === 0) {
    return ''
  }

  // Determine drop frame mode
  const isDropFrame = fps === 29.97

  // EDL header
  const lines = [
    `TITLE: ${title}`,
    `FCM: ${isDropFrame ? 'DROP FRAME' : 'NON-DROP FRAME'}`,
    '',
  ]

  // Each beat becomes a cut event
  beats.forEach((beatTime, index) => {
    const eventNum = String(index + 1).padStart(3, '0')

    // For each beat, create a 1-frame cut
    // Source: 00:00:00:00 to 00:00:00:01 (1 frame)
    // Record: same as beat position
    const recordIn = formatTimecode(beatTime, fps)
    const recordOut = formatTimecode(beatTime + 1 / fps, fps)

    // EDL cut format
    const edlLine = `${eventNum}  AX       V     C        00:00:00:00 00:00:00:01 ${recordIn} ${recordOut}`
    lines.push(edlLine)
  })

  return lines.join('\n')
}

/**
 * Trigger download of EDL file
 *
 * @param {string} edlContent - EDL content string
 * @param {string} filename - Filename (defaults to beatsync_export.edl)
 */
export function downloadEdl(edlContent, filename = 'beatsync_export.edl') {
  const blob = new Blob([edlContent], { type: 'text/plain;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  URL.revokeObjectURL(url)
}

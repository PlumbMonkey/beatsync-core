/**
 * CSV export utility
 * Generates a CSV file with beat/bar timestamps in multiple frame rate formats
 */

/**
 * Generate CSV content for beat and bar timestamps
 *
 * @param {number[]} beats - Array of beat timestamps in seconds
 * @param {number[]} bars - Array of bar timestamps in seconds
 * @param {number} selectedFps - Selected frame rate (for primary column)
 * @returns {string} - CSV content ready for download
 */
export function generateCsv(beats, bars, selectedFps = 30) {
  // Merge beats and bars with type labels, then sort by timestamp
  const events = [
    ...beats.map(t => ({ timestamp: t, type: 'beat' })),
    ...bars.map(t => ({ timestamp: t, type: 'bar' })),
  ]
  
  // Remove duplicates in case a beat and bar occur at the same time
  // Prefer 'bar' type if there's a conflict
  const seen = new Set()
  const unique = []
  for (const event of events.sort((a, b) => a.timestamp - b.timestamp)) {
    if (!seen.has(event.timestamp)) {
      seen.add(event.timestamp)
      unique.push(event)
    } else {
      // Update to 'bar' if current is 'bar' and we haven't added it yet
      const idx = unique.findIndex(e => e.timestamp === event.timestamp)
      if (event.type === 'bar' && unique[idx].type === 'beat') {
        unique[idx].type = 'bar'
      }
    }
  }

  // Generate CSV rows with headers
  const headers = [
    'timestamp_seconds',
    'timestamp_frames_24fps',
    'timestamp_frames_25fps',
    'timestamp_frames_30fps',
    'type',
  ]

  const rows = unique.map(event => {
    const frames24 = Math.round(event.timestamp * 24)
    const frames25 = Math.round(event.timestamp * 25)
    const frames30 = Math.round(event.timestamp * 30)

    return [
      event.timestamp.toFixed(3),
      frames24,
      frames25,
      frames30,
      event.type,
    ]
  })

  // Combine headers and rows
  const csv = [
    headers.join(','),
    ...rows.map(row => row.join(',')),
  ].join('\n')

  return csv
}

/**
 * Trigger download of CSV file
 *
 * @param {string} csvContent - CSV content string
 * @param {string} filename - Filename (defaults to beatsync_export.csv)
 */
export function downloadCsv(csvContent, filename = 'beatsync_export.csv') {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
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

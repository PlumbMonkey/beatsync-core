import React, { useRef, useEffect, useState } from 'react'

/**
 * BeatTimeline Component
 * HTML5 Canvas-based visualization of beats, bars, energy curve, and sections
 * Features:
 *   - Interactive playhead marker (draggable or clickable)
 *   - Energy curve fill
 *   - Beat/bar ticks
 *   - Section labels
 */
export default function BeatTimeline({ contract, onPlayheadChange }) {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [playhead, setPlayhead] = useState(0.0)
  const [scale, setScale] = useState(1.0) // zoom for horizontal scrolling
  const [isDragging, setIsDragging] = useState(false)
  const [windowWidth, setWindowWidth] = useState(window.innerWidth)

  if (!contract) return null

  const CANVAS_HEIGHT = 160
  const PADDING_TOP = 30 // for section labels
  const PADDING_BOTTOM = 10
  const ENERGY_HEIGHT = 60 // height of energy curve area
  const BEATS_HEIGHT = 30 // height of beat marker area
  const CANVAS_FULL_HEIGHT = PADDING_TOP + ENERGY_HEIGHT + BEATS_HEIGHT + PADDING_BOTTOM

  // Update window width on resize
  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Calculate canvas width from container
  const getCanvasWidth = () => {
    if (containerRef.current) {
      return containerRef.current.offsetWidth
    }
    return Math.min(windowWidth - 40, 1200)
  }

  const canvasWidth = getCanvasWidth()
  const duration = contract.duration_seconds
  const pixelsPerSecond = canvasWidth / (duration * scale)

  // Handle click on timeline
  const handleCanvasClick = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const newPlayhead = (x / pixelsPerSecond) * scale
    const clamped = Math.max(0, Math.min(duration, newPlayhead))
    setPlayhead(clamped)
    onPlayheadChange?.(clamped)
  }

  // Handle playhead drag
  const handleMouseDown = (e) => {
    setIsDragging(true)
  }

  const handleMouseMove = (e) => {
    if (!isDragging || !canvasRef.current) return

    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const newPlayhead = (x / pixelsPerSecond) * scale
    const clamped = Math.max(0, Math.min(duration, newPlayhead))
    setPlayhead(clamped)
    onPlayheadChange?.(clamped)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, pixelsPerSecond, scale, duration])

  // Draw canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.fillStyle = '#1a1a2e'
    ctx.fillRect(0, 0, canvasWidth, CANVAS_FULL_HEIGHT)

    // Draw grid lines for time reference
    const gridInterval = calculateGridInterval(duration)
    ctx.strokeStyle = '#334155'
    ctx.lineWidth = 1
    ctx.font = '11px Inter, sans-serif'
    ctx.fillStyle = '#64748b'

    for (let t = 0; t <= duration; t += gridInterval) {
      const x = (t / duration) * canvasWidth
      ctx.beginPath()
      ctx.moveTo(x, PADDING_TOP)
      ctx.lineTo(x, PADDING_TOP + ENERGY_HEIGHT + BEATS_HEIGHT)
      ctx.stroke()

      // Time label
      const label = formatTime(t)
      const metrics = ctx.measureText(label)
      ctx.fillText(label, x - metrics.width / 2, PADDING_TOP + ENERGY_HEIGHT + BEATS_HEIGHT + 18)
    }

    // Draw Section Boundaries (full-height lines)
    if (contract.structure && contract.structure.length > 0) {
      ctx.strokeStyle = '#68d391'
      ctx.lineWidth = 2
      ctx.font = 'bold 12px Inter, sans-serif'
      ctx.fillStyle = '#68d391'

      contract.structure.forEach((section) => {
        const x = (section.start / duration) * canvasWidth
        ctx.beginPath()
        ctx.moveTo(x, PADDING_TOP)
        ctx.lineTo(x, PADDING_TOP + ENERGY_HEIGHT + BEATS_HEIGHT)
        ctx.stroke()

        // Section label
        ctx.fillText(section.label, x + 4, PADDING_TOP + 15)
      })
    }

    // Draw Energy Curve (area chart)
    if (contract.energy && contract.energy.length > 0) {
      const energyData = contract.energy

      // Normalize energy values
      const maxEnergy = Math.max(...energyData)
      const normalizedEnergy = energyData.map(v => (maxEnergy > 0 ? v / maxEnergy : 0))

      // Fill area under curve
      ctx.fillStyle = 'rgba(99, 179, 237, 0.4)'
      ctx.beginPath()
      ctx.moveTo(0, PADDING_TOP + ENERGY_HEIGHT)

      for (let i = 0; i < normalizedEnergy.length; i++) {
        const x = (i / normalizedEnergy.length) * canvasWidth
        const y = PADDING_TOP + ENERGY_HEIGHT - normalizedEnergy[i] * ENERGY_HEIGHT
        ctx.lineTo(x, y)
      }

      ctx.lineTo(canvasWidth, PADDING_TOP + ENERGY_HEIGHT)
      ctx.closePath()
      ctx.fill()

      // Stroke curve
      ctx.strokeStyle = '#63b3ed'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(0, PADDING_TOP + ENERGY_HEIGHT - normalizedEnergy[0] * ENERGY_HEIGHT)

      for (let i = 1; i < normalizedEnergy.length; i++) {
        const x = (i / normalizedEnergy.length) * canvasWidth
        const y = PADDING_TOP + ENERGY_HEIGHT - normalizedEnergy[i] * ENERGY_HEIGHT
        ctx.lineTo(x, y)
      }

      ctx.stroke()
    }

    // Draw Beat Markers (small yellow ticks)
    ctx.strokeStyle = '#f6e05e'
    ctx.lineWidth = 2

    contract.beats.forEach((beatTime) => {
      const x = (beatTime / duration) * canvasWidth
      const tickHeight = 8

      ctx.beginPath()
      ctx.moveTo(x, PADDING_TOP + ENERGY_HEIGHT)
      ctx.lineTo(x, PADDING_TOP + ENERGY_HEIGHT + tickHeight)
      ctx.stroke()
    })

    // Draw Bar Markers (tall coral/red ticks)
    ctx.strokeStyle = '#fc8181'
    ctx.lineWidth = 3

    contract.bars?.forEach((barTime) => {
      const x = (barTime / duration) * canvasWidth
      const tickHeight = 16

      ctx.beginPath()
      ctx.moveTo(x, PADDING_TOP + ENERGY_HEIGHT)
      ctx.lineTo(x, PADDING_TOP + ENERGY_HEIGHT + tickHeight)
      ctx.stroke()
    })

    // Draw Playhead (white vertical line)
    const playheadX = (playhead / duration) * canvasWidth
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(playheadX, PADDING_TOP)
    ctx.lineTo(playheadX, PADDING_TOP + ENERGY_HEIGHT + BEATS_HEIGHT)
    ctx.stroke()

    // Playhead circle at top
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(playheadX, PADDING_TOP - 8, 4, 0, Math.PI * 2)
    ctx.fill()

    // Playhead time label
    ctx.font = 'bold 12px Inter, sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.textAlign = 'center'
    const timeLabel = formatTime(playhead)
    ctx.fillText(timeLabel, playheadX, PADDING_TOP - 15)
  }, [canvasWidth, contract, playhead, scale])

  const calculateGridInterval = (duration) => {
    if (duration < 10) return 1
    if (duration < 60) return 5
    if (duration < 300) return 10
    return 30
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${String(secs).padStart(2, '0')}`
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div
        ref={containerRef}
        className="bg-slate-800 rounded-lg border border-slate-700 overflow-x-auto"
      >
        <canvas
          ref={canvasRef}
          width={canvasWidth}
          height={CANVAS_FULL_HEIGHT}
          onClick={handleCanvasClick}
          onMouseDown={handleMouseDown}
          className="cursor-pointer w-full"
        />
      </div>

      <div className="mt-2 flex justify-between items-center text-xs text-slate-400">
        <div>Click to seek • Drag playhead to move</div>
        <div>Playhead: {formatTime(playhead)}</div>
      </div>
    </div>
  )
}

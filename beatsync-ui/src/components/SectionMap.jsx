import React, { useState } from 'react'

// Color palette for sections
const SECTION_COLORS = [
  '#6366f1', // indigo
  '#8b5cf6', // violet
  '#d946ef', // fuchsia
  '#ec4899', // pink
  '#f43f5e', // rose
  '#f97316', // orange
  '#eab308', // yellow
  '#84cc16', // lime
  '#22c55e', // green
  '#10b981', // emerald
  '#14b8a6', // teal
  '#06b6d4', // cyan
  '#0ea5e9', // sky
  '#3b82f6', // blue
]

/**
 * SectionMap Component
 * Horizontal bar showing sections as colored blocks with labels
 */
export default function SectionMap({ contract }) {
  const [hoveredSection, setHoveredSection] = useState(null)

  if (!contract || !contract.structure || contract.structure.length === 0) {
    return null
  }

  const duration = contract.duration_seconds

  return (
    <div className="w-full max-w-4xl mx-auto mt-6">
      <div className="text-sm text-slate-400 mb-2">Sections</div>

      <div className="relative h-16 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        {contract.structure.map((section, idx) => {
          const color =
            SECTION_COLORS[idx % SECTION_COLORS.length]
          const startPercent = (section.start / duration) * 100
          const endPercent = (section.end / duration) * 100
          const width = endPercent - startPercent

          return (
            <div
              key={section.label}
              className="absolute h-full transition-opacity"
              style={{
                left: `${startPercent}%`,
                width: `${width}%`,
                backgroundColor: color,
                opacity: hoveredSection === section.label ? 1 : 0.7,
              }}
              onMouseEnter={() => setHoveredSection(section.label)}
              onMouseLeave={() => setHoveredSection(null)}
            >
              <div className="h-full flex items-center px-2 text-white text-xs font-semibold overflow-hidden whitespace-nowrap text-ellipsis">
                {section.label}
              </div>

              {/* Tooltip */}
              {hoveredSection === section.label && (
                <div className="absolute bottom-full left-0 mb-2 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-xs whitespace-nowrap z-10">
                  {formatTime(section.start)} – {formatTime(section.end)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${String(secs).padStart(2, '0')}`
}

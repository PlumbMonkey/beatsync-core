import React from 'react'

/**
 * ConfidenceBar Component
 * Small visual indicator for confidence values (0.0-1.0)
 */
function ConfidenceBar({ value }) {
  const percentage = Math.max(0, Math.min(100, value * 100))
  let barColor = 'bg-red-500'
  if (percentage > 80) {
    barColor = 'bg-green-500'
  } else if (percentage > 50) {
    barColor = 'bg-yellow-500'
  }

  return (
    <div className="flex items-center gap-2">
      <div className="wflex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} transition-all`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <span className="text-xs text-slate-400 w-10 text-right">
        {percentage.toFixed(0)}%
      </span>
    </div>
  )
}

/**
 * TrackMeta Component
 * Displays BPM, key, duration, and other metadata in a clean card layout
 */
export default function TrackMeta({ contract }) {
  if (!contract) return null

  // Format duration from seconds to M:SS
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${String(secs).padStart(2, '0')}`
  }

  return (
    <div className="w-full max-w-2xl mx-auto bg-slate-800 rounded-lg border border-slate-700 p-6 space-y-4">
      {/* BPM */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-slate-400 mb-2">Tempo</div>
          <p className="text-3xl font-bold text-white mb-3">
            {contract.bpm.toFixed(1)} BPM
          </p>
          <ConfidenceBar value={contract.bpm_confidence} />
        </div>

        {/* Key */}
        <div>
          <div className="text-sm text-slate-400 mb-2">Key</div>
          <p className="text-3xl font-bold text-white mb-3">{contract.key}</p>
          <ConfidenceBar value={contract.key_confidence} />
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-slate-700"></div>

      {/* Duration */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-slate-400 mb-1">Duration</div>
          <p className="text-lg font-semibold text-white">
            {formatDuration(contract.duration_seconds)}
          </p>
        </div>

        <div>
          <div className="text-sm text-slate-400 mb-1">Beats</div>
          <p className="text-lg font-semibold text-white">
            {contract.beats.length} beats
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="text-xs text-slate-500 pt-2">
        Schema v{contract.schema_version}
      </div>
    </div>
  )
}

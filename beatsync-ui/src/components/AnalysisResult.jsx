import React from 'react'
import TrackMeta from './TrackMeta'
import BeatTimeline from './BeatTimeline'
import SectionMap from './SectionMap'
import ExportPanel from './ExportPanel'

/**
 * AnalysisResult Component
 * Main container for displaying analysis results
 */
export default function AnalysisResult({
  contract,
  filename = 'beatsync_export',
  onReset,
}) {
  if (!contract) return null

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 py-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Analysis Complete</h2>
        <p className="text-sm text-slate-400">{filename}</p>
      </div>

      {/* Track Metadata */}
      <TrackMeta contract={contract} />

      {/* Beat Timeline Visualization */}
      <BeatTimeline contract={contract} />

      {/* Section Map */}
      <SectionMap contract={contract} />

      {/* Export Panel */}
      <ExportPanel contract={contract} filename={filename} />

      {/* Reset Button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onReset}
          className="py-2 px-6 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-lg transition-colors"
        >
          Analyze Another File
        </button>
      </div>
    </div>
  )
}

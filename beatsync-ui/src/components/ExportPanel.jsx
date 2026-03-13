import React, { useState } from 'react'
import { generateCsv, downloadCsv } from '../utils/exportCsv'
import { generateEdl, downloadEdl } from '../utils/exportEdl'

/**
 * ExportPanel Component
 * Provides CSV and EDL export options with frame rate selector
 */
export default function ExportPanel({ contract, filename = 'beatsync_export' }) {
  const [selectedFps, setSelectedFps] = useState(30)
  const [isExporting, setIsExporting] = useState(false)

  if (!contract) return null

  const fpsOptions = [24, 25, 29.97, 30]

  const handleExportCsv = () => {
    setIsExporting(true)
    try {
      const csv = generateCsv(
        contract.rhythm?.beats || [],
        contract.rhythm?.bars || [],
        selectedFps
      )
      downloadCsv(csv, `${filename}.csv`)
    } finally {
      setIsExporting(false)
    }
  }

  const handleExportEdl = () => {
    setIsExporting(true)
    try {
      const edl = generateEdl(
        contract.rhythm?.beats || [],
        selectedFps,
        filename
      )
      downloadEdl(edl, `${filename}.edl`)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 bg-slate-800 rounded-lg border border-slate-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Export Results</h3>

      {/* Frame Rate Selector */}
      <div className="mb-6">
        <label className="block text-sm text-slate-300 mb-2">
          Frame Rate (applies to all exports):
        </label>
        <div className="grid grid-cols-4 gap-2">
          {fpsOptions.map((fps) => (
            <button
              key={fps}
              onClick={() => setSelectedFps(fps)}
              className={`py-2 px-3 rounded text-sm font-medium transition-colors ${
                selectedFps === fps
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
              }`}
            >
              {fps} FPS
            </button>
          ))}
        </div>
      </div>

      {/* Export Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={handleExportCsv}
          disabled={isExporting}
          className="py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {isExporting ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              Exporting...
            </>
          ) : (
            <>
              <span>📊</span> Export CSV
            </>
          )}
        </button>

        <button
          onClick={handleExportEdl}
          disabled={isExporting}
          className="py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {isExporting ? (
            <>
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              Exporting...
            </>
          ) : (
            <>
              <span>🎬</span> Export EDL
            </>
          )}
        </button>
      </div>

      <p className="text-xs text-slate-400 mt-4">
        CSV: Spreadsheet with beat timestamps in multiple formats. EDL: Edit list for DaVinci
        Resolve, Premiere Pro, or Final Cut Pro.
      </p>
    </div>
  )
}

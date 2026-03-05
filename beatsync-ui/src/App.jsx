import React, { useState } from 'react'
import UploadZone from './components/UploadZone'
import AnalysisResult from './components/AnalysisResult'
import { analyzeAudio } from './api/beatsync'

/**
 * App Component
 * Main application state machine and orchestration
 * States: idle | selected | uploading | complete | error
 */
function App() {
  const [appState, setAppState] = useState('idle')
  // idle: initial state, showing upload zone
  // selected: file selected, ready to analyze
  // uploading: API call in flight
  // complete: analysis successful, showing results
  // error: analysis failed, showing error message

  const [selectedFile, setSelectedFile] = useState(null)
  const [contract, setContract] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const handleFileSelected = (file) => {
    setSelectedFile(file)
    setAppState('selected')
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setAppState('uploading')
    setErrorMessage(null)

    try {
      const result = await analyzeAudio(selectedFile)
      setContract(result)
      setAppState('complete')
    } catch (error) {
      setErrorMessage(error.message || 'Analysis failed. Please try again.')
      setAppState('error')
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setContract(null)
    setErrorMessage(null)
    setAppState('idle')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 py-6">
        <div className="max-w-6xl mx-auto px-4">
          <h1 className="text-3xl font-bold tracking-tight">BeatSync Studio</h1>
          <p className="text-sm text-slate-400 mt-1">
            Audio analysis for video editors
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          {appState === 'idle' && (
            <div className="space-y-8">
              <UploadZone onFileSelected={handleFileSelected} isLoading={false} />
              <div className="mt-12 max-w-2xl mx-auto text-center text-sm text-slate-400">
                <p className="mb-4">
                  Upload an audio file to analyze beats, bars, BPM, key, and structure.
                </p>
                <p className="text-xs">
                  Supported formats: WAV, MP3, FLAC, OGG • Maximum 100MB
                </p>
              </div>
            </div>
          )}

          {appState === 'selected' && (
            <div className="space-y-8">
              <UploadZone onFileSelected={handleFileSelected} isLoading={false} />

              <div className="flex justify-center gap-4">
                <button
                  onClick={handleAnalyze}
                  className="py-3 px-8 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Analyze
                </button>

                <button
                  onClick={handleReset}
                  className="py-3 px-8 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {appState === 'uploading' && (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-400 mb-4"></div>
              <p className="text-lg text-slate-300">Analyzing your audio...</p>
              <p className="text-sm text-slate-400 mt-2">
                This usually takes a few seconds.
              </p>
            </div>
          )}

          {appState === 'complete' && contract && (
            <AnalysisResult
              contract={contract}
              filename={selectedFile?.name || 'beatsync_export'}
              onReset={handleReset}
            />
          )}

          {appState === 'error' && errorMessage && (
            <div className="max-w-2xl mx-auto">
              <div className="bg-red-900 border border-red-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-100 mb-2">
                  Analysis Failed
                </h3>
                <p className="text-red-200 mb-4">{errorMessage}</p>

                <button
                  onClick={handleReset}
                  className="py-2 px-4 bg-red-700 hover:bg-red-600 text-white font-medium rounded transition-colors"
                >
                  Try Again
                </button>
              </div>

              <div className="mt-6">
                <UploadZone onFileSelected={handleFileSelected} isLoading={false} />
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 mt-12">
        <div className="max-w-6xl mx-auto px-4 flex justify-between items-center text-sm text-slate-400">
          <p>© 2026 Plumbmonkey Media</p>
          <a
            href="https://plumbmonkey.online"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-300 transition-colors"
          >
            plumbmonkey.online
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App

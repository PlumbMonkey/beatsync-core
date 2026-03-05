import React, { useState, useRef } from 'react'

const ACCEPTED_TYPES = ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/ogg']
const ACCEPTED_EXTENSIONS = ['.wav', '.mp3', '.flac', '.ogg']

/**
 * UploadZone Component
 * Drag-and-drop zone for audio file selection with click-to-browse fallback
 */
export default function UploadZone({ onFileSelected, isLoading }) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (isValidAudioFile(file)) {
        setSelectedFile(file)
        onFileSelected(file)
      } else {
        alert('Invalid file type. Supported: WAV, MP3, FLAC, OGG')
      }
    }
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      const file = files[0]
      if (isValidAudioFile(file)) {
        setSelectedFile(file)
        onFileSelected(file)
      } else {
        alert('Invalid file type. Supported: WAV, MP3, FLAC, OGG')
      }
    }
  }

  const isValidAudioFile = (file) => {
    // Check mime type or file extension
    if (ACCEPTED_TYPES.includes(file.type)) {
      return true
    }
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    return ACCEPTED_EXTENSIONS.includes(ext)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-400 bg-blue-500 bg-opacity-10'
            : selectedFile
            ? 'border-green-500 bg-green-500 bg-opacity-5'
            : 'border-slate-600 hover:border-slate-500 bg-slate-800'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          disabled={isLoading}
        />

        {isLoading ? (
          <div className="space-y-4">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-400"></div>
            </div>
            <p className="text-slate-300">Analyzing audio...</p>
          </div>
        ) : selectedFile ? (
          <div className="space-y-3">
            <div className="text-sm text-slate-400">Selected file</div>
            <p className="font-semibold text-white">{selectedFile.name}</p>
            <p className="text-sm text-slate-400">{formatFileSize(selectedFile.size)}</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-4xl">📁</div>
            <div>
              <p className="font-semibold text-white mb-1">Drag audio file here</p>
              <p className="text-sm text-slate-400">or click to browse</p>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              Supported: WAV, MP3, FLAC, OGG
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

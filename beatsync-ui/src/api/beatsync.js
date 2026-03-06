/**
 * BeatSync API client
 * Handles file upload and analysis requests to the FastAPI backend
 */

const API_BASE = import.meta.env.VITE_API_URL || ''

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

/**
 * Upload an audio file for analysis
 *
 * @param {File} file - The audio file to analyze
 * @returns {Promise<Object>} - The analysis contract with beats, bars, key, structure, etc.
 * @throws {ApiError} - If the upload or analysis fails
 */
export async function analyzeAudio(file) {
  if (!file) {
    throw new ApiError('No file provided', 400, 'File is required')
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch(`${API_BASE}/api/analysis`, {
      method: 'POST',
      body: formData,
      // Note: Do NOT set Content-Type header; let the browser set it with the correct boundary
    })

    if (!response.ok) {
      let errorDetails = {}
      try {
        errorDetails = await response.json()
      } catch (e) {
        // Response body is not JSON
      }

      let errorMessage = `Upload failed (${response.status})`

      if (response.status === 400) {
        errorMessage = 'Invalid file format. Supported: WAV, MP3, FLAC, OGG'
      } else if (response.status === 422) {
        errorMessage = 'File could not be analyzed. Is it a valid audio file?'
      } else if (response.status === 413) {
        errorMessage = 'File is too large. Maximum 100MB.'
      } else if (response.status === 500) {
        errorMessage = 'Server error during analysis. Please try again.'
      }

      throw new ApiError(errorMessage, response.status, errorDetails)
    }

    const contract = await response.json()
    return contract
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }

    // Network error
    if (!navigator.onLine) {
      throw new ApiError('No internet connection', 0, { offline: true })
    }

    throw new ApiError(
      `Network error: ${error.message}`,
      0,
      { original: error }
    )
  }
}

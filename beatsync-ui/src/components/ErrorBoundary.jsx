import React from 'react'

/**
 * ErrorBoundary Component
 * Catches JavaScript errors during render and displays a graceful fallback
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  resetError = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <div className="bg-red-900 border border-red-700 rounded-lg p-8">
              <h1 className="text-2xl font-bold text-red-100 mb-4">
                Something Went Wrong
              </h1>
              <p className="text-red-200 text-sm mb-6">
                An unexpected error occurred. Please try refreshing the page.
              </p>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mb-6 text-xs text-red-300 bg-red-950 p-3 rounded overflow-auto max-h-32">
                  <summary className="cursor-pointer font-mono">
                    Error Details
                  </summary>
                  <pre className="mt-2 whitespace-pre-wrap break-words">
                    {this.state.error.toString()}
                  </pre>
                </details>
              )}
              <button
                onClick={() => {
                  this.resetError()
                  window.location.href = '/'
                }}
                className="w-full py-2 px-4 bg-red-700 hover:bg-red-600 text-white font-medium rounded transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

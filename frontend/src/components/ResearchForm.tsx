import { useState } from 'react'
import { JobStatus } from '../App'
interface ResearchFormProps {
  onJobCreated: (job: JobStatus) => void
  disabled: boolean
}
const exampleQueries = [
  { label: 'Apple', query: 'Apple' },
  { label: 'NVIDIA', query: 'NVIDIA' },
  { label: 'Tesla', query: 'Tesla' },
  { label: 'Microsoft', query: 'Microsoft' },
]
export default function ResearchForm({ onJobCreated, disabled }: ResearchFormProps) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() }),
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to create research job')
      }
      const data = await response.json()
      onJobCreated({
        job_id: data.job_id,
        query: data.query,
        ticker: '',
        status: data.status,
      })
      setQuery('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }
  return (
    <div className="bg-white rounded-xl shadow-sm border border-primary-200 overflow-hidden">
      <form onSubmit={handleSubmit} className="p-6">
        <div className="relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-primary-400">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter stock name (e.g., apple)"
            disabled={disabled || loading}
            maxLength={500}
            className="w-full pl-12 pr-4 py-4 text-lg bg-primary-50 border-2 border-primary-200 rounded-lg focus:border-accent-blue focus:bg-white transition-all duration-200 placeholder:text-primary-400 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        {error && (
          <div className="mt-3 flex items-center gap-2 text-danger text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}
        <div className="mt-4 flex items-center justify-between gap-4">
          <button 
            type="submit" 
            disabled={disabled || loading || !query.trim()}
            className="px-8 py-3 bg-accent-blue hover:bg-blue-600 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer"
          >
            {loading ? (
              <>
                <div className="spinner" />
                Analyzing...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Research
              </>
            )}
          </button>
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-primary-500 self-center mr-2">Try:</span>
            {exampleQueries.map((ex, i) => (
              <button 
                key={i}
                type="button"
                onClick={() => setQuery(ex.query)}
                disabled={disabled || loading}
                className="px-3 py-1.5 text-sm bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-full transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {ex.label}
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  )
}
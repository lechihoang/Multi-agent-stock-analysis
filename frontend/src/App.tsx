import { useState } from 'react'
import ResearchForm from './components/ResearchForm'
import ResearchResult from './components/ResearchResult'
import './index.css'
export interface JobStatus {
  job_id: string
  query: string
  ticker: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  query_type?: string
  report?: string
  execution_time?: number
  error?: string
}
function App() {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [isPolling, setIsPolling] = useState(false)
  const handleResearchComplete = (result: Partial<JobStatus>) => {
    setJobStatus(prev => prev ? { ...prev, status: 'completed', ...result } : null)
    setIsPolling(false)
  }
  const handleResearchError = (error: string) => {
    setJobStatus(prev => prev ? { ...prev, status: 'failed', error } : null)
    setIsPolling(false)
  }
  return (
    <div className="min-h-screen bg-primary-50">
      <header className="bg-white border-b border-primary-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-5">
          <div>
            <h1 className="text-2xl font-heading font-semibold text-primary-900 tracking-tight">
              Stock Research Agent
            </h1>
            <p className="text-primary-500 text-sm mt-0.5">
              AI-powered financial analysis
            </p>
          </div>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="space-y-6">
          <ResearchForm 
            onJobCreated={(job) => {
              setJobStatus(null)
              setJobStatus(job)
              setIsPolling(true)
            }}
            disabled={isPolling}
          />
          {jobStatus && (
            <ResearchResult 
              jobId={jobStatus.job_id}
              query={jobStatus.query}
              isPolling={isPolling}
              onComplete={handleResearchComplete}
              onError={handleResearchError}
              onPollingChange={setIsPolling}
            />
          )}
        </div>
      </main>
    </div>
  )
}
export default App
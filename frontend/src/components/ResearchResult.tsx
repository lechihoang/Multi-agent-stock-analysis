import { useEffect, useState, useMemo, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import { JobStatus } from '../App'
import { exportToPDF } from '../utils/pdfExport'
interface RecommendationData {
  rating: string
  priceTarget: string
  suitableFor: string[]
  timeHorizon: string
  outlook: string
}
interface ResearchResultProps {
  jobId: string
  query: string
  isPolling: boolean
  onComplete: (result: Partial<JobStatus>) => void
  onError: (error: string) => void
  onPollingChange: (polling: boolean) => void
}
const statusConfig = {
  pending: { label: 'Pending', color: 'bg-warning/20 text-warning', icon: '⏳' },
  processing: { label: 'Processing', color: 'bg-accent-blue/20 text-accent-blue', icon: '⚡' },
  completed: { label: 'Completed', color: 'bg-success/20 text-success', icon: '✓' },
  failed: { label: 'Failed', color: 'bg-danger/20 text-danger', icon: '✗' },
}
function parseRecommendation(report: string): RecommendationData | null {
  const defaultData: RecommendationData = {
    rating: '',
    priceTarget: '',
    suitableFor: [],
    timeHorizon: '',
    outlook: '',
  }
  const lastSection = report.slice(-1200)
  
  const ratingMatch = lastSection.match(/(?:\*\*Rating:\*\*|Rating:|rating:|rating\*\*)\s*(buy|hold|sell|strong\s*buy|strong\s*sell|outperform|underperform|neutral)/i)
  if (ratingMatch) {
    const rating = ratingMatch[1] || ratingMatch[2]
    defaultData.rating = rating.replace(/\s+/g, ' ').trim()
  }
  
  const outlookMatch = lastSection.match(/(?:\*\*Overall Outlook:\*\*|Overall Outlook:|outlook:|outlook\*\*)\s*(bullish|bearish|neutral)/i)
  if (outlookMatch) {
    defaultData.outlook = outlookMatch[1].trim()
  }
  
  const priceMatch = lastSection.match(/(?:\*\*Price Target:\*\*|Price Target:|price target:|price target\*\*)\s*\$?(\d+(?:\.\d+)?)/i)
  if (priceMatch) {
    defaultData.priceTarget = `$${priceMatch[1]}`
  }
  
  const suitableMatch = lastSection.match(/(?:\*\*Suitable for:\*\*|Suitable for:|suitable for:|suitable for\*\*)\s*([^\n]+)/i)
  if (suitableMatch) {
    const suitableText = suitableMatch[1].trim()
    defaultData.suitableFor = suitableText
      .split(/,/)
      .map(s => s.replace(/\s*(investors?|strategies?)\s*/gi, '').trim())
      .filter(s => s.length > 0)
  }
  
  const horizonMatch = lastSection.match(/(?:\*\*Time Horizon:\*\*|Time Horizon:|time horizon:|time horizon\*\*)\s*([^\n]+)/i)
  if (horizonMatch) {
    defaultData.timeHorizon = horizonMatch[1].trim()
  }

  if (!defaultData.rating && !defaultData.outlook) return null
  return defaultData
}
const outlookConfig: Record<string, { color: string; bg: string; icon: string }> = {
  bullish: { color: 'text-success', bg: 'bg-success/10', icon: '↗' },
  bearish: { color: 'text-danger', bg: 'bg-danger/10', icon: '↘' },
  neutral: { color: 'text-warning', bg: 'bg-warning/10', icon: '→' },
}
export default function ResearchResult({
  jobId,
  query,
  isPolling,
  onComplete,
  onError,
  onPollingChange,
}: ResearchResultProps) {
  const [status, setStatus] = useState<'pending' | 'processing' | 'completed' | 'failed'>('pending')
  const [ticker, setTicker] = useState<string>('')
  const [report, setReport] = useState<string>('')
  const [executionTime, setExecutionTime] = useState<number | null>(null)
  const [error, setError] = useState<string>('')
  const [isExportingPDF, setIsExportingPDF] = useState(false)
  const reportRef = useRef<HTMLDivElement>(null)
  const recommendation = useMemo(() => {
    if (!report) return null
    return parseRecommendation(report)
  }, [report])
  useEffect(() => {
    if (!isPolling) return
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/research/${jobId}`)
        const data = await response.json()
        setStatus(data.status)
        setTicker(data.ticker || '')
        if (data.status === 'completed') {
          setReport(data.report || '')
          setExecutionTime(data.execution_time)
          onComplete({
            ticker: data.ticker,
            report: data.report,
            execution_time: data.execution_time,
          })
          onPollingChange(false)
          clearInterval(pollInterval)
        } else if (data.status === 'failed') {
          setError(data.error || 'Research failed')
          onError(data.error || 'Research failed')
          onPollingChange(false)
          clearInterval(pollInterval)
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 3000)
    return () => clearInterval(pollInterval)
  }, [jobId, isPolling, onComplete, onError, onPollingChange])
  const handleDownloadPDF = async () => {
    if (!reportRef.current) return
    setIsExportingPDF(true)
    try {
      await exportToPDF(reportRef.current, {
        filename: ticker ? `${ticker}_research_report.pdf` : 'research_report.pdf',
      })
    } catch (err) {
      console.error('PDF export error:', err)
    } finally {
      setIsExportingPDF(false)
    }
  }
  const handleCopy = () => {
    navigator.clipboard.writeText(report)
  }
  const currentStatus = statusConfig[status]
  return (
    <div className="bg-white rounded-xl shadow-sm border border-primary-200 overflow-hidden animate-fade-in">
      {}
      <div className="bg-primary-50 border-b border-primary-200 px-6 py-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-lg font-heading font-semibold text-primary-900">
              {ticker ? `Research: ${ticker}` : 'Analyzing...'}
            </h2>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            {}
            <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${currentStatus.color}`}>
              <span className="mr-1">{currentStatus.icon}</span>
              {currentStatus.label}
            </span>
            {}
            {executionTime && (
              <span className="px-3 py-1.5 bg-success/20 text-success rounded-full text-sm font-medium flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {executionTime.toFixed(1)}s
              </span>
            )}
          </div>
        </div>
        {}
        {isPolling && (status === 'pending' || status === 'processing') && (
          <div className="mt-4">
            <div className="h-2 bg-primary-200 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-accent-blue to-accent-cyan progress-animated rounded-full" style={{ width: '60%' }} />
            </div>
            <p className="text-sm text-primary-500 mt-2 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {status === 'pending' ? 'Starting analysis...' : 'Agents are researching...'}
            </p>
          </div>
        )}
      </div>
      {}
      {error && (
        <div className="p-6 bg-danger/10 border-b border-danger/20">
          <div className="flex items-center gap-3 text-danger">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium">Research Failed</p>
              <p className="text-sm opacity-80">{error}</p>
            </div>
          </div>
        </div>
      )}
      {}
      {report && (
        <div className="p-6">
          {}
          <div className="flex gap-3 mb-4">
            <button 
              onClick={handleDownloadPDF}
              disabled={isExportingPDF}
              className="px-4 py-2 bg-accent-blue hover:bg-blue-600 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg transition-colors duration-200 flex items-center gap-2 cursor-pointer disabled:cursor-not-allowed"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              {isExportingPDF ? 'Exporting...' : 'Export PDF'}
            </button>
            <button 
              onClick={handleCopy}
              className="px-4 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center gap-2 cursor-pointer"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
          </div>
          {}
          <div 
            ref={reportRef}
            className="
            prose prose-sm max-w-none 
            prose-headings:font-heading prose-headings:text-primary-900
            prose-p:text-primary-700 leading-relaxed
            prose-strong:text-primary-900
            prose-a:text-accent-blue
            prose-code:bg-primary-100 prose-code:text-primary-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none
            prose-pre:bg-primary-900 prose-pre:text-primary-100
            prose-blockquote:border-l-accent-blue prose-blockquote:text-primary-600 prose-blockquote:bg-primary-50 prose-blockquote:py-2 prose-blockquote:px-4 prose-blockquote:rounded-r
            prose-ul:space-y-2
            prose-li:text-primary-700 prose-li:marker:text-accent-blue
            prose-hr:border-primary-200
            [&>h2]:mt-6 [&>h2]:mb-3 [&>h2]:text-lg [&>h2]:font-semibold
            [&>h3]:mt-4 [&>h3]:mb-2 [&>h3]:text-base
            table:w-full table:border-collapse table:my-4
            th:bg-accent-blue/10 th:text-primary-900 th:font-semibold th:px-4 th:py-2 th:border th:border-accent-blue/20 th:rounded-t-lg
            td:bg-white td:text-primary-700 td:px-4 td:py-2 td:border td:border-accent-blue/20
            tr:last-child td:first-child:rounded-bl-lg tr:last-child td:last-child:rounded-br-lg
          ">
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
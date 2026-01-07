'use client'

import { useState, useEffect } from 'react'
import { X, Clock, Calendar, Loader2, History } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Badge } from '@/components/ui/badge'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'

interface CrawlSchedule {
  id: string
  knowledge_source_id: string
  schedule_type: 'manual' | 'daily' | 'weekly' | 'monthly'
  day_of_week: number | null
  preferred_hour: number
  is_active: boolean
  last_crawl_at: string | null
  next_crawl_at: string | null
  created_at: string
  updated_at: string
}

interface CrawlHistory {
  id: string
  knowledge_source_id: string
  started_at: string
  completed_at: string | null
  status: 'success' | 'partial' | 'failed'
  pages_checked: number
  pages_added: number
  pages_updated: number
  pages_removed: number
  error_message: string | null
}

interface Props {
  knowledgeSourceId: string
  sourceUrl: string
  pagesCount: number
  lastSynced: string | null
  onClose: () => void
  onSync: () => void
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
]

const HOURS = Array.from({ length: 24 }, (_, i) => ({
  value: i,
  label: `${i.toString().padStart(2, '0')}:00 UTC`
}))

export function CrawlScheduleModal({
  knowledgeSourceId,
  sourceUrl,
  pagesCount,
  lastSynced,
  onClose,
  onSync
}: Props) {
  const [schedule, setSchedule] = useState<CrawlSchedule | null>(null)
  const [history, setHistory] = useState<CrawlHistory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [scheduleType, setScheduleType] = useState<'manual' | 'daily' | 'weekly' | 'monthly'>('manual')
  const [dayOfWeek, setDayOfWeek] = useState(0)
  const [preferredHour, setPreferredHour] = useState(2)
  const [isActive, setIsActive] = useState(true)

  useEffect(() => {
    loadSchedule()
    loadHistory()
  }, [knowledgeSourceId])

  const loadSchedule = async () => {
    try {
      const token = getAccessToken()
      if (!token) return

      const data = await apiRequestWithAuth<CrawlSchedule>(
        `/api/v1/chatbots/knowledge-sources/${knowledgeSourceId}/schedule`,
        token,
        { method: 'GET' }
      )

      setSchedule(data)
      setScheduleType(data.schedule_type)
      setDayOfWeek(data.day_of_week || 0)
      setPreferredHour(data.preferred_hour)
      setIsActive(data.is_active)
    } catch (err: any) {
      console.error('Failed to load schedule:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      const token = getAccessToken()
      if (!token) return

      const data = await apiRequestWithAuth<CrawlHistory[]>(
        `/api/v1/chatbots/knowledge-sources/${knowledgeSourceId}/crawl-history?limit=10`,
        token,
        { method: 'GET' }
      )

      setHistory(data)
    } catch (err: any) {
      console.error('Failed to load history:', err)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    setError(null)

    try {
      const token = getAccessToken()
      if (!token) return

      const payload = {
        schedule_type: scheduleType,
        day_of_week: scheduleType === 'weekly' ? dayOfWeek : null,
        preferred_hour: preferredHour,
        is_active: isActive
      }

      const data = await apiRequestWithAuth<CrawlSchedule>(
        `/api/v1/chatbots/knowledge-sources/${knowledgeSourceId}/schedule`,
        token,
        {
          method: 'POST',
          body: JSON.stringify(payload)
        }
      )

      setSchedule(data)
      alert('Schedule saved successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to save schedule')
    } finally {
      setIsSaving(false)
    }
  }

  const handleSyncNow = async () => {
    setIsSyncing(true)
    setError(null)

    try {
      const token = getAccessToken()
      if (!token) return

      await apiRequestWithAuth(
        `/api/v1/chatbots/knowledge-sources/${knowledgeSourceId}/crawl-now`,
        token,
        { method: 'POST' }
      )

      alert('Sync started! This may take a few minutes.')
      onSync()
      // Reload history after a delay
      setTimeout(() => loadHistory(), 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to start sync')
    } finally {
      setIsSyncing(false)
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Never'
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (startStr: string, endStr: string | null) => {
    if (!endStr) return 'In progress...'
    const start = new Date(startStr).getTime()
    const end = new Date(endStr).getTime()
    const seconds = Math.floor((end - start) / 1000)
    return `${seconds}s`
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Sync Settings</h2>
            <p className="text-sm text-muted-foreground truncate">{sourceUrl}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{pagesCount} pages</span>
            <span className="text-muted-foreground">Last synced: {formatDate(lastSynced)}</span>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          {/* Schedule Settings */}
          <div className="space-y-4">
            <Label className="text-base font-semibold">Sync Frequency</Label>
            
            <RadioGroup value={scheduleType} onValueChange={(v: any) => setScheduleType(v)}>
              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/5">
                <RadioGroupItem value="manual" id="manual" />
                <Label htmlFor="manual" className="flex-1 cursor-pointer">Manual only</Label>
              </div>
              
              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/5">
                <RadioGroupItem value="daily" id="daily" />
                <Label htmlFor="daily" className="flex-1 cursor-pointer">Daily</Label>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/5">
                  <RadioGroupItem value="weekly" id="weekly" />
                  <Label htmlFor="weekly" className="flex-1 cursor-pointer">Weekly</Label>
                </div>
                {scheduleType === 'weekly' && (
                  <div className="ml-8 flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-muted-foreground">Every</span>
                    <select 
                      value={dayOfWeek}
                      onChange={(e) => setDayOfWeek(Number(e.target.value))}
                      className="border rounded px-2 py-1 text-sm"
                    >
                      {DAYS_OF_WEEK.map(day => (
                        <option key={day.value} value={day.value}>{day.label}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/5">
                <RadioGroupItem value="monthly" id="monthly" />
                <Label htmlFor="monthly" className="flex-1 cursor-pointer">Monthly</Label>
              </div>
            </RadioGroup>

            {scheduleType !== 'manual' && (
              <div className="ml-8 flex items-center gap-2">
                <span className="text-sm text-muted-foreground">at</span>
                <select 
                  value={preferredHour}
                  onChange={(e) => setPreferredHour(Number(e.target.value))}
                  className="border rounded px-2 py-1 text-sm"
                >
                  {HOURS.map(hour => (
                    <option key={hour.value} value={hour.value}>{hour.label}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Next Sync */}
          {schedule?.next_crawl_at && scheduleType !== 'manual' && (
            <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-md">
              <div className="flex items-center gap-2 text-sm text-blue-900">
                <Clock className="h-4 w-4" />
                <span>Next sync: {formatDate(schedule.next_crawl_at)}</span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Schedule'
              )}
            </Button>
            <Button variant="outline" onClick={handleSyncNow} disabled={isSyncing}>
              {isSyncing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Syncing...
                </>
              ) : (
                'Sync Now'
              )}
            </Button>
            <Button variant="ghost" onClick={() => setShowHistory(!showHistory)}>
              <History className="h-4 w-4 mr-2" />
              {showHistory ? 'Hide' : 'View'} History
            </Button>
          </div>

          {/* History */}
          {showHistory && (
            <div className="space-y-2 border-t pt-4">
              <Label className="text-base font-semibold">Sync History</Label>
              {history.length > 0 ? (
                <div className="space-y-2">
                  {history.map((h) => (
                    <div key={h.id} className="border rounded-lg p-3 text-sm">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{formatDate(h.started_at)}</span>
                        <Badge variant={h.status === 'success' ? 'success' : h.status === 'failed' ? 'destructive' : 'secondary'}>
                          {h.status === 'success' ? '✓ Success' : h.status === 'failed' ? '✗ Failed' : '⚠ Partial'}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-5 gap-2 text-xs text-muted-foreground">
                        <div>
                          <div className="font-medium">Duration</div>
                          <div>{formatDuration(h.started_at, h.completed_at)}</div>
                        </div>
                        <div>
                          <div className="font-medium">Checked</div>
                          <div>{h.pages_checked}</div>
                        </div>
                        <div>
                          <div className="font-medium">Added</div>
                          <div className="text-green-600">{h.pages_added}</div>
                        </div>
                        <div>
                          <div className="font-medium">Updated</div>
                          <div className="text-blue-600">{h.pages_updated}</div>
                        </div>
                        <div>
                          <div className="font-medium">Removed</div>
                          <div className="text-red-600">{h.pages_removed}</div>
                        </div>
                      </div>
                      {h.error_message && (
                        <div className="mt-2 text-xs text-red-600">
                          Error: {h.error_message}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-muted-foreground text-sm">
                  No sync history yet
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


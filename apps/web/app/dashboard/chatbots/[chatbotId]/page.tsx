'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  ChevronRight,
  Settings,
  Eye,
  Loader2,
  Database,
  Palette,
  MessageSquare,
  Code,
  BarChart3,
  Plus,
  Sparkles,
  Globe,
  Check,
  X as CloseIcon,
  Search,
  RefreshCcw,
  ExternalLink,
  Upload,
  FileText,
  Trash2,
  AlertCircle,
  HelpCircle,
  Edit2,
  CheckSquare,
  Square,
  Save,
  Maximize2,
  Minimize2,
  ShoppingCart,
  Search as SearchIcon,
  Menu as MenuIcon,
  Users
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { CrawlScheduleModal } from '@/components/dashboard/CrawlScheduleModal'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Checkbox
} from '@/components/ui/checkbox'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { createPortal } from 'react-dom'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'
import { cn } from '@/lib/utils'
import { ChatbotWidgetPreview } from '@/components/chatbot/WidgetPreview'
import { ChatbotTeamSettings } from '@/components/dashboard/ChatbotTeamSettings'
import { CrawlSourcePanel } from '@/components/dashboard/CrawlSourcePanel'
import { ChevronDown, ChevronUp, MoreHorizontal } from 'lucide-react'

interface ChatbotDetail {
  id: string
  tenant_id: number
  name: string
  description: string | null
  status: 'draft' | 'active' | 'paused'
  created_by: number
  created_at: string
  updated_at: string
  permission_level: 'owner' | 'admin' | 'editor' | 'viewer'
}

interface KnowledgeSource {
  id: string
  chatbot_id: string
  source_type: 'crawled_url' | 'uploaded_file' | 'qa_pair'
  source_url: string | null
  status: 'pending' | 'crawling' | 'completed' | 'failed'
  pages_found: number
  created_at: string
  updated_at: string
  files?: {
    id: string
    filename: string
    file_size: number
    mime_type: string
  }[]
  qa_pairs?: QAPair[]
  pages?: CrawledPage[]
}

interface CrawledPage {
  id: string
  knowledge_source_id: string
  url: string
  title: string | null
  created_at: string
}

interface QAPair {
  id: string
  question: string
  answer: string
  created_at: string
  updated_at: string
}

interface RecentActivity {
  id: string
  type: 'knowledge_source' | 'conversation' | 'status_change'
  description: string
  created_at: string
}

interface KnowledgeSourceBreakdown {
  total_crawled_urls: number
  total_uploaded_files: number
  total_qa_pairs: number
  total_crawled_pages: number
  total_file_size: number
  total_qa_count: number
}

interface ChatbotStats {
  total_conversations: number
  total_knowledge_sources: number
  active_knowledge_sources: number
  total_kb_size: number
  knowledge_breakdown: KnowledgeSourceBreakdown
  recent_activity: RecentActivity[]
}

const appearanceSchema = z.object({
  primary_color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid hex color'),
  header_text: z.string().min(1, 'Header text is required').max(255),
  avatar_url: z.string().nullable(),
  position: z.enum(['bottom-right', 'bottom-left']),
  offset_x: z.number().int().optional().default(0),
  offset_y: z.number().int().optional().default(0),
  welcome_message: z.string().nullable(),
  initial_suggestions: z.array(z.string()),
  show_branding: z.boolean(),
})

type AppearanceFormData = z.infer<typeof appearanceSchema>

interface AppearanceData extends AppearanceFormData {
  id: string
  chatbot_id: string
  created_at: string
  updated_at: string
}

export default function ChatbotDetailPage() {
  const params = useParams()
  const router = useRouter()
  const chatbotId = params.chatbotId as string
  
  const [chatbot, setChatbot] = useState<ChatbotDetail | null>(null)
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([])
  const [stats, setStats] = useState<ChatbotStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingKnowledge, setIsLoadingKnowledge] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [knowledgeTab, setKnowledgeTab] = useState('crawl')

  // Knowledge base state
  const [isAddKnowledgeOpen, setIsAddKnowledgeOpen] = useState(false)
  const [knowledgeType, setKnowledgeType] = useState<'url' | 'file' | 'qa'>('url')
  const [newUrl, setNewUrl] = useState('')
  const [isCrawling, setIsCrawling] = useState(false)
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  // Selection state
  const [selectedPages, setSelectedPages] = useState<string[]>([])
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [selectedQAs, setSelectedQAs] = useState<string[]>([])
  const [isBulkDeleting, setIsBulkDeleting] = useState(false)

  // QA state
  const [qaPairs, setQaPairs] = useState<QAPair[]>([])
  const [newQA, setNewQA] = useState({ question: '', answer: '' })
  const [editingQA, setEditingQA] = useState<QAPair | null>(null)
  const [isQAOpen, setIsQAOpen] = useState(false)
  const [qaXlsx, setQaXlsx] = useState<File | null>(null)

  // Appearance state
  const [appearance, setAppearance] = useState<AppearanceData | null>(null)
  const [isLoadingAppearance, setIsLoadingAppearance] = useState(false)
  const [isSavingAppearance, setIsSavingAppearance] = useState(false)
  const [appearanceError, setAppearanceError] = useState<string | null>(null)
  const [appearanceSuccessMessage, setAppearanceSuccessMessage] = useState<string | null>(null)
  const [newSuggestion, setNewSuggestion] = useState('')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [embedCopyStatus, setEmbedCopyStatus] = useState<string | null>(null)
  const avatarInputRef = useRef<HTMLInputElement>(null)

  // Settings state
  const [isSavingSettings, setIsSavingSettings] = useState(false)
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)

  // Crawl scheduling state
  const [isCrawlScheduleOpen, setIsCrawlScheduleOpen] = useState(false)
  const [selectedCrawlSource, setSelectedCrawlSource] = useState<any | null>(null)

  useEffect(() => {
    if (isFullscreen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isFullscreen])

  // Polling state - only poll when we explicitly start a crawl
  const [isPolling, setIsPolling] = useState(false)
  const [pollingStartTime, setPollingStartTime] = useState<number | null>(null)
  const MAX_POLLING_DURATION = 5 * 60 * 1000 // 5 minutes max polling
  const [manuallyStartedCrawl, setManuallyStartedCrawl] = useState(false)

  useEffect(() => {
    if (isFullscreen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isFullscreen])

  // Appearance form setup
  const { register, handleSubmit, watch, setValue, formState: { errors, isDirty } } = useForm<AppearanceFormData>({
    resolver: zodResolver(appearanceSchema),
    defaultValues: {
      primary_color: '#3B82F6',
      header_text: 'Chat Support',
      avatar_url: null,
      position: 'bottom-right',
      offset_x: 0,
      offset_y: 0,
      welcome_message: 'Hi! How can I help you today?',
      initial_suggestions: [],
      show_branding: true,
    }
  })

  const formData = watch()
  // Watch primary_color specifically for immediate updates
  const primaryColor = watch('primary_color')

  useEffect(() => {
    fetchChatbotDetails()
    fetchKnowledgeSources()
    fetchQAPairs()
    fetchAppearance()
    fetchChatbotStats()
  }, [chatbotId])

  const fetchChatbotStats = async () => {
    try {
      const token = getAccessToken()
      if (!token) return

      const response = await apiRequestWithAuth<ChatbotStats>(
        `/api/v1/chatbots/${chatbotId}/stats`,
        token,
        { method: 'GET' }
      )
      setStats(response)
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  // Polling for crawling sources - ONLY when we manually start a crawl and it's still in progress
  useEffect(() => {
    // Only poll if we manually started a crawl in this session
    if (!manuallyStartedCrawl) {
      if (isPolling) {
        setIsPolling(false)
        setPollingStartTime(null)
      }
      return
    }

    // Check for crawling/pending status (case-insensitive)
    const hasCrawlingSources = knowledgeSources.some(s => {
      const status = s.status?.toLowerCase()
      return status === 'crawling' || status === 'pending'
    })

    // Stop polling if all crawls are complete
    if (!hasCrawlingSources) {
      console.log('All crawls complete, stopping polling')
      setIsPolling(false)
      setPollingStartTime(null)
      setManuallyStartedCrawl(false)
      return
    }

    // Start polling if we have active crawls
    if (!isPolling) {
      setIsPolling(true)
      setPollingStartTime(Date.now())
    }
  }, [knowledgeSources, manuallyStartedCrawl, isPolling])

  // Separate effect for the actual polling interval
  useEffect(() => {
    if (!isPolling) return

    const interval = setInterval(() => {
      // Check if we've exceeded max polling duration
      if (pollingStartTime && Date.now() - pollingStartTime > MAX_POLLING_DURATION) {
        console.log('Polling timeout reached, stopping automatic refresh')
        setIsPolling(false)
        setPollingStartTime(null)
        return
      }
      fetchKnowledgeSources(false)
    }, 3000)

    return () => clearInterval(interval)
  }, [isPolling, pollingStartTime])

  const fetchChatbotDetails = async () => {
    try {
      setIsLoading(true)
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      const response = await apiRequestWithAuth<ChatbotDetail>(
        `/api/v1/chatbots/${chatbotId}`,
        token,
        { method: 'GET' }
      )
      
      setChatbot(response)
      setError(null)
    } catch (err: any) {
      console.error('Failed to fetch chatbot:', err)
      setError(err.message || 'Failed to load chatbot')
      // Redirect to chatbots list if not found or no permission
      if (err.message?.includes('404') || err.message?.includes('403')) {
        setTimeout(() => router.push('/dashboard/chatbots'), 2000)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const fetchKnowledgeSources = async (showLoading = true): Promise<KnowledgeSource[] | null> => {
    try {
      if (showLoading) setIsLoadingKnowledge(true)
      const token = getAccessToken()
      if (!token) return null

      const response = await apiRequestWithAuth<KnowledgeSource[]>(
        `/api/v1/chatbots/${chatbotId}/knowledge-sources`,
        token,
        { method: 'GET' }
      )
      setKnowledgeSources(response)
      return response
    } catch (err) {
      console.error('Failed to fetch knowledge sources:', err)
      return null
    } finally {
      if (showLoading) setIsLoadingKnowledge(false)
    }
  }

  const fetchQAPairs = async () => {
    try {
      const token = getAccessToken()
      if (!token) return
      const response = await apiRequestWithAuth<QAPair[]>(
        `/api/v1/chatbots/${chatbotId}/qa`,
        token,
        { method: 'GET' }
      )
      setQaPairs(response)
    } catch (err) {
      console.error('Failed to fetch QA pairs:', err)
    }
  }

  const fetchAppearance = async () => {
    try {
      setIsLoadingAppearance(true)
      const token = getAccessToken()
      if (!token) return

      const response = await apiRequestWithAuth<AppearanceData>(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        { method: 'GET' }
      )

      setAppearance(response)
      // Set form values
      Object.keys(response).forEach(key => {
        if (key !== 'id' && key !== 'chatbot_id' && key !== 'created_at' && key !== 'updated_at') {
          setValue(key as keyof AppearanceFormData, response[key as keyof AppearanceData])
        }
      })

      setAppearanceError(null)
    } catch (err: any) {
      console.error('Failed to fetch appearance:', err)
      setAppearanceError(err.message || 'Failed to load appearance settings')
    } finally {
      setIsLoadingAppearance(false)
    }
  }

  const handleCrawl = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUrl.trim()) return

    try {
      setIsCrawling(true)
      const token = getAccessToken()
      if (!token) return

      // Get the response which includes the new knowledge source
      const newSource = await apiRequestWithAuth<KnowledgeSource>(
        `/api/v1/chatbots/${chatbotId}/crawl`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({ base_url: newUrl })
        }
      )
      
      // Optimistically add the new source to the state immediately
      setKnowledgeSources(prev => {
        // Check if it already exists (avoid duplicates)
        const exists = prev.some(s => s.id === newSource.id)
        if (exists) {
          // Update existing source
          return prev.map(s => s.id === newSource.id ? newSource : s)
        }
        // Add new source
        return [...prev, newSource]
      })
      
      setNewUrl('')
      setIsAddKnowledgeOpen(false)
      // Enable polling only when we manually start a crawl
      setManuallyStartedCrawl(true)
      
      // Refresh to get the latest data (including pages as they're crawled)
      await fetchKnowledgeSources()
      // Refresh stats after adding knowledge source
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to start crawl')
    } finally {
      setIsCrawling(false)
    }
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadFiles || uploadFiles.length === 0) return

    try {
      setIsUploading(true)
      const token = getAccessToken()
      if (!token) return

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Upload files sequentially
      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i]
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${API_URL}/api/v1/chatbots/${chatbotId}/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        })

        if (!response.ok) {
          const errData = await response.json()
          throw new Error(`Failed to upload ${file.name}: ${errData.detail || 'Unknown error'}`)
        }
      }
      
      setUploadFiles(null)
      setIsAddKnowledgeOpen(false)
      await fetchKnowledgeSources()
      // Refresh stats after uploading files
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to upload files')
    } finally {
      setIsUploading(false)
    }
  }

  const handleQASubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const token = getAccessToken()
      if (!token) return

      if (editingQA) {
        await apiRequestWithAuth(
          `/api/v1/chatbots/qa/${editingQA.id}`,
          token,
          {
            method: 'PATCH',
            body: JSON.stringify(newQA)
          }
        )
      } else {
        await apiRequestWithAuth(
          `/api/v1/chatbots/${chatbotId}/qa`,
          token,
          {
            method: 'POST',
            body: JSON.stringify(newQA)
          }
        )
      }
      
      setNewQA({ question: '', answer: '' })
      setEditingQA(null)
      await fetchQAPairs()
      await fetchKnowledgeSources()
      // Refresh stats after adding QA
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to save QA pair')
    }
  }

  const handleQAXlsxUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!qaXlsx) return

    try {
      const token = getAccessToken()
      if (!token) return

      const formData = new FormData()
      formData.append('file', qaXlsx)

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/v1/chatbots/${chatbotId}/qa/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Upload failed')
      }
      
      setQaXlsx(null)
      fetchKnowledgeSources()
      fetchQAPairs()
    } catch (err: any) {
      alert(err.message || 'Failed to upload XLSX')
    }
  }

  const handleDeleteQA = async (qaId: string) => {
    if (!confirm('Are you sure you want to delete this QA pair?')) return
    try {
      const token = getAccessToken()
      if (!token) return
      await apiRequestWithAuth(`/api/v1/chatbots/qa/${qaId}`, token, { method: 'DELETE' })
      await fetchQAPairs()
      await fetchKnowledgeSources()
      // Refresh stats after deleting QA
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to delete QA')
    }
  }

  const handleDeleteSource = async (sourceId: string) => {
    if (!confirm('Are you sure you want to delete this knowledge source and all its data?')) return

    try {
      const token = getAccessToken()
      if (!token) return

      await apiRequestWithAuth(
        `/api/v1/chatbots/knowledge-sources/${sourceId}`,
        token,
        { method: 'DELETE' }
      )
      
      await fetchKnowledgeSources()
      // Refresh stats after deleting source
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to delete source')
    }
  }

  const handleDeletePage = async (pageId: string) => {
    if (!confirm('Are you sure you want to delete this page?')) return
    try {
      const token = getAccessToken()
      if (!token) return
      await apiRequestWithAuth(`/api/v1/chatbots/pages/${pageId}`, token, { method: 'DELETE' })
      
      // Refresh knowledge sources and check for empty crawl sources
      const updatedSources = await fetchKnowledgeSources()
      if (updatedSources) {
        const crawlSources = updatedSources.filter(s => s.source_type === 'crawled_url')
        const emptyCrawlSources = crawlSources.filter(source => {
          return !source.pages || source.pages.length === 0
        })
        
        // Delete empty crawl sources
        if (emptyCrawlSources.length > 0) {
          for (const source of emptyCrawlSources) {
            try {
              await apiRequestWithAuth(
                `/api/v1/chatbots/knowledge-sources/${source.id}`,
                token,
                { method: 'DELETE' }
              )
            } catch (err) {
              console.error(`Failed to delete empty crawl source ${source.id}:`, err)
            }
          }
          // Refresh again after deleting empty sources
          await fetchKnowledgeSources()
        }
      }
      // Refresh stats after deleting page
      fetchChatbotStats()
    } catch (err: any) {
      alert(err.message || 'Failed to delete page')
    }
  }

  const handleBulkDelete = async (type: 'pages' | 'files' | 'qa') => {
    const ids = type === 'pages' ? selectedPages : type === 'files' ? selectedFiles : selectedQAs
    if (ids.length === 0) return
    if (!confirm(`Are you sure you want to delete ${ids.length} items?`)) return

    try {
      setIsBulkDeleting(true)
      const token = getAccessToken()
      if (!token) return

      let endpoint = ''
      if (type === 'pages') endpoint = `/api/v1/chatbots/${chatbotId}/pages/bulk-delete`
      else if (type === 'files') endpoint = `/api/v1/chatbots/${chatbotId}/knowledge-sources/bulk-delete`
      else if (type === 'qa') endpoint = `/api/v1/chatbots/${chatbotId}/qa/bulk-delete`

      await apiRequestWithAuth(endpoint, token, {
        method: 'POST',
        body: JSON.stringify({ ids })
      })

      // Reset selection
      if (type === 'pages') setSelectedPages([])
      else if (type === 'files') setSelectedFiles([])
      else if (type === 'qa') setSelectedQAs([])

      // Refresh knowledge sources to get updated state
      const updatedSources = await fetchKnowledgeSources()
      
      // If pages were deleted, check for empty crawl sources and delete them
      if (type === 'pages' && updatedSources) {
        // Find crawl sources with no pages
        const crawlSources = updatedSources.filter(s => s.source_type === 'crawled_url')
        const emptyCrawlSources = crawlSources.filter(source => {
          // Check if source has any pages
          return !source.pages || source.pages.length === 0
        })
        
        // Delete empty crawl sources
        if (emptyCrawlSources.length > 0) {
          for (const source of emptyCrawlSources) {
            try {
              await apiRequestWithAuth(
                `/api/v1/chatbots/knowledge-sources/${source.id}`,
                token,
                { method: 'DELETE' }
              )
            } catch (err) {
              console.error(`Failed to delete empty crawl source ${source.id}:`, err)
            }
          }
          // Refresh again after deleting empty sources
          await fetchKnowledgeSources()
        }
        // Refresh stats after deleting pages
        fetchChatbotStats()
      }
      
      if (type === 'qa') {
        await fetchQAPairs()
        // Refresh stats after deleting QA
        fetchChatbotStats()
      }
      
      if (type === 'files') {
        // Refresh stats after deleting files
        fetchChatbotStats()
      }
    } catch (err: any) {
      alert(err.message || 'Bulk delete failed')
    } finally {
      setIsBulkDeleting(false)
    }
  }

  const handleToggleStatus = async () => {
    if (!chatbot) return

    try {
      const token = getAccessToken()
      if (!token) return

      const newStatus = chatbot.status === 'active' ? 'paused' : 'active'

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}`,
        token,
        {
          method: 'PATCH',
          body: JSON.stringify({ status: newStatus })
        }
      )

      // Refresh chatbot data
      fetchChatbotDetails()
    } catch (err) {
      console.error('Failed to toggle status:', err)
    }
  }

  const handleDeleteChatbot = async () => {
    if (!confirm('Are you sure you want to delete this chatbot? This action cannot be undone.')) return

    try {
      const token = getAccessToken()
      if (!token) return

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}`,
        token,
        { method: 'DELETE' }
      )

      router.push('/dashboard/chatbots')
    } catch (err: any) {
      alert(err.message || 'Failed to delete chatbot')
    }
  }

  const handleSettingsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!chatbot) return

    try {
      setIsSavingSettings(true)
      setSettingsError(null)
      const token = getAccessToken()
      if (!token) return

      const formData = new FormData(e.currentTarget)
      const name = formData.get('name') as string
      const status = formData.get('status') as 'draft' | 'active' | 'paused'

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}`,
        token,
        {
          method: 'PATCH',
          body: JSON.stringify({ name, status }),
        }
      )

      setSettingsSuccess('Settings saved successfully!')
      fetchChatbotDetails()
      setTimeout(() => setSettingsSuccess(null), 3000)
    } catch (err: any) {
      setSettingsError(err.message || 'Failed to save settings')
    } finally {
      setIsSavingSettings(false)
    }
  }

  const handleAppearanceSubmit = async (data: AppearanceFormData) => {
    try {
      setIsSavingAppearance(true)
      const token = getAccessToken()
      if (!token) return

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      )

      setAppearanceSuccessMessage('Appearance settings saved successfully!')
      setTimeout(() => setAppearanceSuccessMessage(null), 3000)

      // Refresh to reset isDirty
      await fetchAppearance()
    } catch (err: any) {
      console.error('Failed to save appearance:', err)
      setAppearanceError(err.message || 'Failed to save appearance settings')
    } finally {
      setIsSavingAppearance(false)
    }
  }

  const handleAddSuggestion = () => {
    if (newSuggestion.trim()) {
      const currentSuggestions = formData.initial_suggestions || []
      setValue('initial_suggestions', [...currentSuggestions, newSuggestion.trim()], { shouldDirty: true })
      setNewSuggestion('')
    }
  }

  const handleRemoveSuggestion = (index: number) => {
    const currentSuggestions = formData.initial_suggestions || []
    setValue(
      'initial_suggestions',
      currentSuggestions.filter((_, i) => i !== index),
      { shouldDirty: true }
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error || !chatbot) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error?.includes('404') ? 'Chatbot Not Found' : 'Access Denied'}
          </h2>
          <p className="text-gray-600 mb-4">
            {error || 'You don\'t have permission to view this chatbot.'}
          </p>
          <Button onClick={() => router.push('/dashboard/chatbots')}>
            Back to Chatbots
          </Button>
        </div>
      </div>
    )
  }

  const canEdit = ['owner', 'admin', 'editor'].includes(chatbot.permission_level)

  // Knowledge base filtering
  const crawlSources = knowledgeSources.filter(s => s.source_type === 'crawled_url')
  const fileSources = knowledgeSources.filter(s => s.source_type === 'uploaded_file')
  const qaSources = knowledgeSources.filter(s => s.source_type === 'qa_pair')

  // Flattened pages for crawl tab
  const allCrawledPages = crawlSources.flatMap(s => 
    (s.pages || []).map(p => ({ ...p, status: s.status, source_url: s.source_url }))
  )

  // Show crawl sources that are actively crawling or have pages
  // This ensures newly added crawl URLs appear immediately even with 0 pages
  const crawlSourcesWithPages = crawlSources.filter(s => {
    const pages = s.pages || []
    const status = s.status?.toLowerCase()
    // Show if: has pages, OR is pending/crawling (active), OR has pages_found > 0
    return pages.length > 0 || s.pages_found > 0 || status === 'pending' || status === 'crawling'
  })

  return (
    <div className="space-y-6">
      {/* Header - Reduced Width */}
      <div className="flex items-center justify-between max-w-4xl">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">
              <Link 
                href="/dashboard/chatbots" 
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Chatbots
              </Link>
              <ChevronRight className="h-4 w-4 inline-block mx-2 text-muted-foreground" />
              <span>{chatbot.name}</span>
            </h1>
            <Badge variant={chatbot.status === 'active' ? 'success' : chatbot.status === 'paused' ? 'warning' : 'secondary'}>
              {chatbot.status.charAt(0).toUpperCase() + chatbot.status.slice(1)}
            </Badge>
            <Badge variant="outline" className="capitalize">
              {chatbot.permission_level}
            </Badge>
          </div>
          {chatbot.description && (
            <p className="text-gray-600 text-sm">{chatbot.description}</p>
          )}
        </div>
      </div>

      {/* Tab Navigation - Full Width Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5 lg:w-auto">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">Overview</span>
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            <span className="hidden sm:inline">Knowledge Base</span>
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            <span className="hidden sm:inline">Design & Test</span>
          </TabsTrigger>
          <TabsTrigger value="install" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            <span className="hidden sm:inline">Install</span>
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <span className="hidden sm:inline">Settings</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Conversations
                </CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_conversations || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.total_conversations === 0 ? 'New chatbot' : 'Active conversations'}
                </p>
              </CardContent>
            </Card>

            <Card
              className="cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => setActiveTab('knowledge')}
            >
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Knowledge Sources
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats?.total_knowledge_sources || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {stats?.knowledge_breakdown?.total_crawled_urls || 0} crawl sites • {stats?.knowledge_breakdown?.total_uploaded_files || 0} files • {stats?.knowledge_breakdown?.total_qa_pairs || 0} Q&A
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Knowledge Base Size
                </CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats?.total_kb_size ? (stats.total_kb_size >= 1024 * 1024 
                    ? `${(stats.total_kb_size / (1024 * 1024)).toFixed(2)} MB`
                    : `${(stats.total_kb_size / 1024).toFixed(1)} KB`
                  ) : '0.0 KB'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Total indexed content
                </p>
              </CardContent>
            </Card>
          </div>


          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks to manage your chatbot
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-1">
                <Button 
                  variant="outline" 
                  className="h-auto flex-col items-start p-4"
                  onClick={() => router.push(`/dashboard/analytics?chatbot_id=${chatbotId}`)}
                >
                  <BarChart3 className="h-5 w-5 mb-2" />
                  <div className="text-left">
                    <div className="font-semibold">View Analytics</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      See usage and performance
                    </div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest updates and changes to this chatbot
              </CardDescription>
            </CardHeader>
            <CardContent>
              {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                <div className="space-y-4">
                  {stats.recent_activity.map((item) => (
                    <div key={item.id} className="flex items-start gap-4 text-sm">
                      <div className={cn(
                        "mt-1 p-1.5 rounded-full",
                        item.type === 'knowledge_source' ? "bg-blue-100 text-blue-600" :
                        item.type === 'conversation' ? "bg-green-100 text-green-600" :
                        "bg-gray-100 text-gray-600"
                      )}>
                        {item.type === 'knowledge_source' ? <Database className="h-3.5 w-3.5" /> :
                         item.type === 'conversation' ? <MessageSquare className="h-3.5 w-3.5" /> :
                         <Settings className="h-3.5 w-3.5" />}
                      </div>
                      <div className="flex-1 space-y-0.5">
                        <p className="font-medium text-gray-900">{item.description}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  No recent activity to display.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Knowledge Base Tab */}
        <TabsContent value="knowledge" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Knowledge Base</CardTitle>
                <CardDescription>
                  Manage the data sources your chatbot learns from
                </CardDescription>
              </div>
              {canEdit && (
                <Button onClick={() => setIsAddKnowledgeOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Source
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {isAddKnowledgeOpen && (
                <div className="mb-6 p-4 border rounded-lg bg-muted/30">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex bg-muted p-1 rounded-md">
                      <Button 
                        variant={knowledgeType === 'url' ? 'secondary' : 'ghost'} 
                        size="sm"
                        onClick={() => setKnowledgeType('url')}
                        className="text-xs"
                      >
                        <Globe className="h-3 w-3 mr-1" /> Website
                      </Button>
                      <Button 
                        variant={knowledgeType === 'file' ? 'secondary' : 'ghost'} 
                        size="sm"
                        onClick={() => setKnowledgeType('file')}
                        className="text-xs"
                      >
                        <Upload className="h-3 w-3 mr-1" /> File
                      </Button>
                      <Button 
                        variant={knowledgeType === 'qa' ? 'secondary' : 'ghost'} 
                        size="sm"
                        onClick={() => setKnowledgeType('qa')}
                        className="text-xs"
                      >
                        <HelpCircle className="h-3 w-3 mr-1" /> Q&A
                      </Button>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => setIsAddKnowledgeOpen(false)}
                      type="button"
                    >
                      <CloseIcon className="h-4 w-4" />
                    </Button>
                  </div>

                  {knowledgeType === 'url' ? (
                    <form onSubmit={handleCrawl} className="space-y-4">
                      <div className="flex gap-2">
                        <div className="flex-1 space-y-1">
                          <Label htmlFor="url">Website URL</Label>
                          <Input 
                            id="url" 
                            placeholder="https://example.com/docs" 
                            value={newUrl}
                            onChange={(e) => setNewUrl(e.target.value)}
                            required
                          />
                        </div>
                        <div className="self-end">
                          <Button type="submit" disabled={isCrawling || !newUrl.trim()}>
                            {isCrawling ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Starting...
                              </>
                            ) : (
                              <>
                                <Search className="h-4 w-4 mr-2" />
                                Crawl URL
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        We&apos;ll crawl the website and process its content for your chatbot.
                      </p>
                    </form>
                  ) : knowledgeType === 'file' ? (
                    <form onSubmit={handleFileUpload} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="file">Upload Files (PDF, DOCX, TXT, MD)</Label>
                        <div className="flex gap-2">
                          <Input 
                            id="file" 
                            type="file" 
                            multiple
                            accept=".pdf,.docx,.txt,.md"
                            onChange={(e) => setUploadFiles(e.target.files)}
                            className="flex-1"
                            required
                          />
                          <Button type="submit" disabled={isUploading || !uploadFiles || uploadFiles.length === 0}>
                            {isUploading ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Uploading...
                              </>
                            ) : (
                              <>
                                <Upload className="h-4 w-4 mr-2" />
                                Upload
                              </>
                            )}
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <AlertCircle className="h-3 w-3" /> Max file size 10MB
                        </p>
                      </div>
                    </form>
                  ) : (
                    <div className="space-y-6">
                      <form onSubmit={handleQASubmit} className="space-y-4">
                        <div className="grid gap-4">
                          <div className="space-y-1">
                            <Label htmlFor="q">Question</Label>
                            <Input 
                              id="q" 
                              value={newQA.question}
                              onChange={(e) => setNewQA({...newQA, question: e.target.value})}
                              placeholder="e.g. What are your opening hours?"
                              required
                            />
                          </div>
                          <div className="space-y-1">
                            <Label htmlFor="a">Answer</Label>
                            <Input 
                              id="a" 
                              value={newQA.answer}
                              onChange={(e) => setNewQA({...newQA, answer: e.target.value})}
                              placeholder="e.g. We are open from 9 AM to 6 PM."
                              required
                            />
                          </div>
                        </div>
                        <Button type="submit">
                          {editingQA ? 'Update QA Pair' : 'Add QA Pair'}
                        </Button>
                        {editingQA && (
                          <Button variant="ghost" className="ml-2" onClick={() => {
                            setEditingQA(null);
                            setNewQA({question: '', answer: ''});
                          }}>Cancel</Button>
                        )}
                      </form>
                      
                      <div className="pt-4 border-t">
                        <Label className="text-xs font-semibold uppercase text-muted-foreground">Or Bulk Upload (XLSX)</Label>
                        <form onSubmit={handleQAXlsxUpload} className="mt-2 flex gap-2">
                          <Input 
                            type="file" 
                            accept=".xlsx,.xls"
                            onChange={(e) => setQaXlsx(e.target.files?.[0] || null)}
                            className="flex-1"
                          />
                          <Button type="submit" variant="outline" disabled={!qaXlsx}>
                            <Upload className="h-4 w-4 mr-2" /> Upload XLSX
                          </Button>
                        </form>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <Tabs value={knowledgeTab} onValueChange={setKnowledgeTab} className="w-full">
                <TabsList className="mb-4">
                  <TabsTrigger value="crawl" className="gap-2">
                    <Globe className="h-4 w-4" /> Crawl {allCrawledPages.length > 0 && <Badge variant="secondary" className="ml-1 h-5 px-1">{allCrawledPages.length}</Badge>}
                  </TabsTrigger>
                  <TabsTrigger value="files" className="gap-2">
                    <FileText className="h-4 w-4" /> Files {fileSources.length > 0 && <Badge variant="secondary" className="ml-1 h-5 px-1">{fileSources.length}</Badge>}
                  </TabsTrigger>
                  <TabsTrigger value="qa" className="gap-2">
                    <MessageSquare className="h-4 w-4" /> Q&A {qaPairs.length > 0 && <Badge variant="secondary" className="ml-1 h-5 px-1">{qaPairs.length}</Badge>}
                  </TabsTrigger>
                </TabsList>

                {isLoadingKnowledge ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                  </div>
                ) : (
                  <>
                    {/* Crawl Tab Content */}
                <TabsContent value="crawl" className="space-y-4">
                  {isCrawlScheduleOpen && selectedCrawlSource && (
                    <CrawlScheduleModal
                      knowledgeSourceId={selectedCrawlSource.id}
                      sourceUrl={selectedCrawlSource.source_url || ''}
                      pagesCount={selectedCrawlSource.pages_found || 0}
                      lastSynced={selectedCrawlSource.updated_at ?? null}
                      onClose={() => { setIsCrawlScheduleOpen(false); setSelectedCrawlSource(null); }}
                      onSync={() => { /* refresh if needed */ }}
                    />
                  )}
                  {crawlSourcesWithPages.length > 0 ? (
                    <div className="space-y-4">
                      {Array.from(new Map(crawlSourcesWithPages.map(ks => [ks.source_url, ks])).values()).map((ks) => (
                        <CrawlSourcePanel
                          key={ks.id}
                          source={ks}
                          pages={allCrawledPages.filter(p => p.source_url === ks.source_url)}
                          selectedPages={selectedPages}
                          onSelectionChange={setSelectedPages}
                          onSchedule={() => {
                            setSelectedCrawlSource(ks)
                            setIsCrawlScheduleOpen(true)
                          }}
                          onDeleteSelected={() => handleBulkDelete('pages')}
                          isBulkDeleting={isBulkDeleting}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 border-2 border-dashed rounded-xl">
                      <Globe className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                      <p className="text-gray-500">No crawled pages found</p>
                      <Button variant="link" onClick={() => {setKnowledgeType('url'); setIsAddKnowledgeOpen(true)}}>Add website URL</Button>
                    </div>
                  )}
                </TabsContent>

                    {/* Files Tab Content */}
                    <TabsContent value="files" className="space-y-4">
                      {fileSources.length > 0 && (
                        <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                          <div className="flex items-center gap-2">
                            <Checkbox 
                              checked={selectedFiles.length === fileSources.length && fileSources.length > 0}
                              onCheckedChange={(checked: boolean) => {
                                if (checked) setSelectedFiles(fileSources.map(s => s.id))
                                else setSelectedFiles([])
                              }}
                            />
                            <span className="text-sm font-medium">Select All</span>
                          </div>
                          {selectedFiles.length > 0 && (
                            <Button 
                              variant="destructive" 
                              size="sm" 
                              onClick={() => handleBulkDelete('files')}
                              disabled={isBulkDeleting}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete {selectedFiles.length}
                            </Button>
                          )}
                        </div>
                      )}

                      {fileSources.length > 0 ? (
                        <div className="space-y-2">
                          {fileSources.map((source) => (
                            <div 
                              key={source.id} 
                              className={`flex items-center justify-between p-3 border rounded-lg hover:bg-muted/5 transition-colors ${selectedFiles.includes(source.id) ? 'bg-blue-50/30 border-blue-200' : ''}`}
                            >
                              <div className="flex items-center gap-3">
                                <Checkbox 
                                  checked={selectedFiles.includes(source.id)}
                                  onCheckedChange={(checked: boolean) => {
                                    if (checked) setSelectedFiles([...selectedFiles, source.id])
                                    else setSelectedFiles(selectedFiles.filter(id => id !== source.id))
                                  }}
                                />
                                <div className="h-8 w-8 rounded bg-blue-50 flex items-center justify-center text-blue-600">
                                  <FileText className="h-4 w-4" />
                                </div>
                                <div>
                                  <div className="font-medium text-sm">
                                    {source.files && source.files.length > 0 ? source.files[0].filename : 'Uploaded File'}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {source.files && source.files.length > 0 ? `${(source.files[0].file_size / 1024).toFixed(1)} KB` : ''} • {new Date(source.created_at).toLocaleDateString()}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant={source.status === 'completed' ? 'success' : 'secondary'} className="text-[10px] px-1 h-4">
                                  {source.status}
                                </Badge>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleDeleteSource(source.id)}
                                  title="Delete file"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 border-2 border-dashed rounded-xl">
                          <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">No files uploaded yet</p>
                          <Button variant="link" onClick={() => {setKnowledgeType('file'); setIsAddKnowledgeOpen(true)}}>Upload your first file</Button>
                        </div>
                      )}
                    </TabsContent>

                    {/* Q&A Tab Content */}
                    <TabsContent value="qa" className="space-y-4">
                      {qaPairs.length > 0 && (
                        <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                          <div className="flex items-center gap-2">
                            <Checkbox 
                              checked={selectedQAs.length === qaPairs.length && qaPairs.length > 0}
                              onCheckedChange={(checked: boolean) => {
                                if (checked) setSelectedQAs(qaPairs.map(q => q.id))
                                else setSelectedQAs([])
                              }}
                            />
                            <span className="text-sm font-medium">Select All</span>
                          </div>
                          {selectedQAs.length > 0 && (
                            <Button 
                              variant="destructive" 
                              size="sm" 
                              onClick={() => handleBulkDelete('qa')}
                              disabled={isBulkDeleting}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete {selectedQAs.length}
                            </Button>
                          )}
                        </div>
                      )}

                      {qaPairs.length > 0 ? (
                        <div className="space-y-3">
                          {qaPairs.map((qa) => (
                            <div 
                              key={qa.id} 
                              className={`p-4 border rounded-lg bg-card shadow-sm hover:shadow-md transition-all ${selectedQAs.includes(qa.id) ? 'bg-blue-50/30 border-blue-200' : ''}`}
                            >
                              <div className="flex justify-between items-start gap-4">
                                <div className="flex items-start gap-3 flex-1">
                                  <Checkbox 
                                    className="mt-1"
                                    checked={selectedQAs.includes(qa.id)}
                                    onCheckedChange={(checked: boolean) => {
                                      if (checked) setSelectedQAs([...selectedQAs, qa.id])
                                      else setSelectedQAs(selectedQAs.filter(id => id !== qa.id))
                                    }}
                                  />
                                  <div className="flex-1 min-w-0">
                                    <div className="font-semibold text-sm mb-1">Q: {qa.question}</div>
                                    <div className="text-sm text-muted-foreground bg-muted/30 p-2 rounded border-l-2 border-blue-500 line-clamp-2">
                                      A: {qa.answer}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex gap-1 shrink-0">
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8"
                                    onClick={() => {
                                      setEditingQA(qa);
                                      setNewQA({question: qa.question, answer: qa.answer});
                                      setKnowledgeType('qa');
                                      setIsAddKnowledgeOpen(true);
                                      window.scrollTo({ top: 0, behavior: 'smooth' });
                                    }}
                                    title="Edit QA pair"
                                  >
                                    <Edit2 className="h-4 w-4" />
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                    onClick={() => handleDeleteQA(qa.id)}
                                    title="Delete QA pair"
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-12 border-2 border-dashed rounded-xl">
                          <MessageSquare className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                          <p className="text-gray-500">No Q&A pairs added</p>
                          <Button variant="link" onClick={() => {setKnowledgeType('qa'); setIsAddKnowledgeOpen(true)}}>Add Q&A manually</Button>
                        </div>
                      )}
                    </TabsContent>
                  </>
                )}
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-4">
          {appearanceError && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {appearanceError}
            </div>
          )}

          {appearanceSuccessMessage && (
            <div className="p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              {appearanceSuccessMessage}
            </div>
          )}

          <form onSubmit={handleSubmit(handleAppearanceSubmit)}>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column - Settings Form */}
              <div className="space-y-6">
                {/* General Settings */}
                <Card>
                  <CardHeader>
                    <CardTitle>General</CardTitle>
                    <CardDescription>Basic chatbot appearance settings</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="header_text">Header Text</Label>
                      <Input
                        id="header_text"
                        {...register('header_text')}
                        placeholder="Chat Support"
                      />
                      {errors.header_text && (
                        <p className="text-sm text-red-600 mt-1">{errors.header_text.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="primary_color">Primary Color</Label>
                      <div className="flex gap-2">
                        <input
                          id="primary_color"
                          type="color"
                          value={primaryColor || '#3B82F6'}
                          onChange={(e) => setValue('primary_color', e.target.value, { shouldDirty: true })}
                          className="w-16 h-10 p-1 border rounded cursor-pointer"
                        />
                        <Input
                          value={primaryColor || ''}
                          onChange={(e) => setValue('primary_color', e.target.value, { shouldDirty: true })}
                          placeholder="#3B82F6"
                          className="flex-1"
                        />
                      </div>
                      {errors.primary_color && (
                        <p className="text-sm text-red-600 mt-1">{errors.primary_color.message}</p>
                      )}
                    </div>

                    <div>
                      <Label htmlFor="welcome_message">Welcome Message</Label>
                      <Textarea
                        id="welcome_message"
                        {...register('welcome_message')}
                        placeholder="Hi! How can I help you today?"
                        rows={3}
                      />
                    </div>

                    <div>
                      <Label htmlFor="avatar_url">Avatar URL</Label>
                      <div className="space-y-2">
                        <Input
                          id="avatar_url"
                          {...register('avatar_url')}
                          placeholder="https://example.com/avatar.png"
                        />
                        <input
                          ref={avatarInputRef}
                          type="file"
                          accept="image/*"
                          style={{ display: 'none' }}
                          onChange={async (e) => {
                            const file = e.target.files?.[0]
                            if (!file) return
                            try {
                              const token = getAccessToken()
                              if (!token) return
                              const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
                              const formData = new FormData()
                              formData.append('avatar', file)
                              const res = await fetch(`${API_URL}/api/v1/chatbots/${chatbotId}/avatar`, {
                                method: 'POST',
                                headers: {
                                  'Authorization': `Bearer ${token}`
                                },
                                body: formData
                              })
                              if (res.ok) {
                                fetchAppearance()
                                setAppearanceSuccessMessage('Avatar uploaded successfully!')
                                setTimeout(() => setAppearanceSuccessMessage(null), 3000)
                              } else {
                                const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
                                setAppearanceError(err.detail || 'Avatar upload failed')
                              }
                            } catch (err) {
                              setAppearanceError('Avatar upload error')
                            } finally {
                              if (avatarInputRef.current) avatarInputRef.current.value = ''
                            }
                          }}
                        />
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={() => avatarInputRef.current?.click()}
                        >
                          <Upload className="h-4 w-4 mr-2" />
                          Upload Custom Avatar
                        </Button>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="position">Position</Label>
                      <RadioGroup
                        value={formData.position}
                        onValueChange={(value) => setValue('position', value as 'bottom-right' | 'bottom-left', { shouldDirty: true })}
                        className="flex gap-6 mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="bottom-left" id="bottom-left" />
                          <Label htmlFor="bottom-left">Bottom Left</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="bottom-right" id="bottom-right" />
                          <Label htmlFor="bottom-right">Bottom Right</Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="offset_x">Offset X (px)</Label>
                        <Input
                          id="offset_x"
                          type="number"
                          {...register('offset_x', { valueAsNumber: true })}
                          placeholder="0"
                        />
                        {errors.offset_x && (
                          <p className="text-sm text-red-600 mt-1">{errors.offset_x.message}</p>
                        )}
                      </div>
                      <div>
                        <Label htmlFor="offset_y">Offset Y (px)</Label>
                        <Input
                          id="offset_y"
                          type="number"
                          {...register('offset_y', { valueAsNumber: true })}
                          placeholder="0"
                        />
                        {errors.offset_y && (
                          <p className="text-sm text-red-600 mt-1">{errors.offset_y.message}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Switch
                        id="show_branding"
                        checked={formData.show_branding}
                        onCheckedChange={(checked) => setValue('show_branding', checked, { shouldDirty: true })}
                      />
                      <Label htmlFor="show_branding">Show branding</Label>
                    </div>
                  </CardContent>
                </Card>

                {/* Initial Suggestions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Initial Suggestions</CardTitle>
                    <CardDescription>Suggested questions to help users start conversations</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add a suggestion..."
                        value={newSuggestion}
                        onChange={(e) => setNewSuggestion(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSuggestion())}
                      />
                      <Button type="button" onClick={handleAddSuggestion} size="sm">
                        Add
                      </Button>
                    </div>

                    <div className="space-y-2">
                      {(formData.initial_suggestions || []).map((suggestion, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                          <span className="text-sm">{suggestion}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveSuggestion(index)}
                            className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                          >
                            ×
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end">
                  <Button type="submit" disabled={isSavingAppearance || !isDirty}>
                    {isSavingAppearance ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Right Column - Live Site Preview */}
              <div className="lg:sticky lg:top-6 h-fit space-y-4">
                {isFullscreen ? createPortal(
                  <div className="fixed inset-0 z-[99999] bg-background flex flex-col">
                    <div className="flex items-center justify-between px-6 py-4 border-b bg-white relative z-20">
                      <div className="flex items-center gap-2">
                        <Label className="text-sm font-semibold text-gray-700">
                          Live Site Preview (Fullscreen Mode)
                        </Label>
                      </div>
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        onClick={() => setIsFullscreen(false)}
                        className="h-8 gap-2"
                      >
                        <Minimize2 className="h-4 w-4" />
                        Exit Fullscreen
                      </Button>
                    </div>

                    <div className="flex-1 relative bg-gray-50 overflow-hidden">
                      <div className="absolute inset-0 overflow-y-auto pb-20">
                        {/* Header */}
                        <header className="bg-white border-b px-6 py-4 flex items-center justify-between sticky top-0 z-10">
                          <div className="flex items-center gap-4">
                            <MenuIcon className="h-5 w-5 text-gray-500" />
                            <div className="font-bold text-xl tracking-tighter">STORE.CO</div>
                          </div>
                          <div className="hidden md:flex items-center gap-6 text-sm font-medium">
                            <span className="text-blue-600 border-b-2 border-blue-600 pb-1">Home</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Shop</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Categories</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Deals</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <SearchIcon className="h-5 w-5 text-gray-500" />
                            <div className="relative">
                              <ShoppingCart className="h-5 w-5 text-gray-500" />
                              <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">3</span>
                            </div>
                          </div>
                        </header>

                        {/* Hero Section */}
                        <section className="bg-blue-600 text-white px-8 text-center relative overflow-hidden py-24 transition-all duration-300">
                          <div className="absolute top-0 left-0 w-full h-full opacity-10">
                            <div className="absolute top-10 left-10 w-20 h-20 border-4 border-white rounded-full"></div>
                            <div className="absolute bottom-10 right-10 w-32 h-32 border-4 border-white rounded-full"></div>
                          </div>
                          <h2 className="font-bold mb-4 relative z-10 text-5xl transition-all duration-300">Summer Collection 2026</h2>
                          <p className="text-blue-100 mb-6 mx-auto relative z-10 text-xl max-w-2xl transition-all duration-300">Get up to 50% off on all new arrivals this season. Shop the latest trends now!</p>
                          <Button variant="secondary" size="lg" className="font-semibold relative z-10">Shop Now</Button>
                        </section>

                        {/* Product Grid */}
                        <section className="p-8 max-w-7xl mx-auto transition-all duration-300">
                          <div className="flex items-center justify-between mb-6">
                            <h3 className="font-bold text-lg">Featured Products</h3>
                            <span className="text-blue-600 text-sm font-medium cursor-pointer">View All</span>
                          </div>
                          <div className="grid gap-6 grid-cols-4 transition-all duration-300">
                            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                              <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden group hover:shadow-md transition-all">
                                <div className="bg-gray-100 relative overflow-hidden h-48 transition-all">
                                  <div className="absolute inset-0 flex items-center justify-center text-gray-300">
                                    <ShoppingCart className="opacity-20 h-12 w-12 transition-all" />
                                  </div>
                                  <div className="absolute top-2 right-2 bg-white/80 backdrop-blur-sm p-1 rounded-full text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <ShoppingCart className="h-4 w-4" />
                                  </div>
                                </div>
                                <div className="p-4">
                                  <div className="h-4 w-2/3 bg-gray-200 rounded mb-2"></div>
                                  <div className="h-3 w-1/3 bg-blue-100 rounded mb-4"></div>
                                  <div className="flex items-center justify-between">
                                    <div className="h-5 w-16 bg-gray-300 rounded"></div>
                                    <div className="h-8 w-8 bg-blue-50 rounded-lg flex items-center justify-center">
                                      <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </section>

                        {/* Newsletter */}
                        <section className="bg-gray-100 text-center rounded-xl border border-gray-200 p-16 max-w-4xl mx-auto mb-16 transition-all duration-300">
                          <h4 className="font-bold mb-2">Join Our Newsletter</h4>
                          <p className="text-sm text-gray-500 mb-6">Stay updated with latest trends and offers</p>
                          <div className="flex gap-2 max-w-md mx-auto">
                            <div className="flex-1 bg-white h-10 rounded-lg border border-gray-200"></div>
                            <div className="w-24 bg-gray-900 h-10 rounded-lg"></div>
                          </div>
                        </section>
                      </div>

                      <ChatbotWidgetPreview
                        key="preview-fullscreen"
                        primaryColor={primaryColor || '#3B82F6'}
                        headerText={formData.header_text}
                        avatarUrl={formData.avatar_url}
                        position={formData.position}
                        offsetX={formData.offset_x}
                        offsetY={formData.offset_y}
                        welcomeMessage={formData.welcome_message}
                        initialSuggestions={formData.initial_suggestions}
                        showBranding={formData.show_branding}
                        contained={true}
                        readOnly={false}
                        chatbotId={chatbotId}
                      />
                    </div>
                  </div>,
                  document.body
                ) : null}

                {/* Standard Preview (Always Visible when not fullscreen, or placeholder) */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Label className="text-sm font-semibold text-gray-700">Live Site Preview</Label>
                    <div className="group relative">
                      <div className="w-4 h-4 rounded-full bg-gray-300 flex items-center justify-center text-xs text-gray-600 cursor-help hover:bg-gray-400 transition-colors">
                        i
                      </div>
                      <div className="absolute left-full ml-2 top-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                        Test your chatbot exactly as it will operate on your site
                      </div>
                    </div>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setIsFullscreen(true)}
                    className="h-8 gap-2"
                  >
                    <Maximize2 className="h-4 w-4" />
                    Fullscreen Preview
                  </Button>
                </div>

                <Card className="overflow-hidden border-2 border-blue-100 shadow-lg h-[700px]">
                  <CardContent className="p-0 h-full relative">
                    <div className="bg-gray-50 h-full relative overflow-hidden">
                      {/* Mock E-commerce Website Structure */}
                      <div className="absolute inset-0 overflow-y-auto pb-20">
                        {/* Header */}
                        <header className="bg-white border-b px-6 py-4 flex items-center justify-between sticky top-0 z-10">
                          <div className="flex items-center gap-4">
                            <MenuIcon className="h-5 w-5 text-gray-500" />
                            <div className="font-bold text-xl tracking-tighter">STORE.CO</div>
                          </div>
                          <div className="hidden md:flex items-center gap-6 text-sm font-medium">
                            <span className="text-blue-600 border-b-2 border-blue-600 pb-1">Home</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Shop</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Categories</span>
                            <span className="text-gray-500 hover:text-blue-600 cursor-pointer transition-colors">Deals</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <SearchIcon className="h-5 w-5 text-gray-500" />
                            <div className="relative">
                              <ShoppingCart className="h-5 w-5 text-gray-500" />
                              <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">3</span>
                            </div>
                          </div>
                        </header>

                        {/* Hero Section */}
                        <section className="bg-blue-600 text-white px-8 text-center relative overflow-hidden py-12">
                          <div className="absolute top-0 left-0 w-full h-full opacity-10">
                            <div className="absolute top-10 left-10 w-20 h-20 border-4 border-white rounded-full"></div>
                            <div className="absolute bottom-10 right-10 w-32 h-32 border-4 border-white rounded-full"></div>
                          </div>
                          <h2 className="font-bold mb-4 relative z-10 text-3xl">Summer Collection 2026</h2>
                          <p className="text-blue-100 mb-6 mx-auto relative z-10 text-sm max-w-md">Get up to 50% off on all new arrivals this season. Shop the latest trends now!</p>
                          <Button variant="secondary" size="default" className="font-semibold relative z-10">Shop Now</Button>
                        </section>

                        {/* Product Grid */}
                        <section className="p-8">
                          <div className="flex items-center justify-between mb-6">
                            <h3 className="font-bold text-lg">Featured Products</h3>
                            <span className="text-blue-600 text-sm font-medium cursor-pointer">View All</span>
                          </div>
                          <div className="grid gap-6 grid-cols-2">
                            {[1, 2, 3, 4].map((i) => (
                              <div key={i} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden group hover:shadow-md transition-all">
                                <div className="bg-gray-100 relative overflow-hidden h-32">
                                  <div className="absolute inset-0 flex items-center justify-center text-gray-300">
                                    <ShoppingCart className="opacity-20 h-10 w-10" />
                                  </div>
                                  <div className="absolute top-2 right-2 bg-white/80 backdrop-blur-sm p-1 rounded-full text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <ShoppingCart className="h-4 w-4" />
                                  </div>
                                </div>
                                <div className="p-4">
                                  <div className="h-4 w-2/3 bg-gray-200 rounded mb-2"></div>
                                  <div className="h-3 w-1/3 bg-blue-100 rounded mb-4"></div>
                                  <div className="flex items-center justify-between">
                                    <div className="h-5 w-16 bg-gray-300 rounded"></div>
                                    <div className="h-8 w-8 bg-blue-50 rounded-lg flex items-center justify-center">
                                      <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </section>

                        {/* Newsletter */}
                        <section className="bg-gray-100 text-center rounded-xl border border-gray-200 p-8 mx-8 mb-8">
                          <h4 className="font-bold mb-2">Join Our Newsletter</h4>
                          <p className="text-sm text-gray-500 mb-6">Stay updated with latest trends and offers</p>
                          <div className="flex gap-2 max-w-md mx-auto">
                            <div className="flex-1 bg-white h-10 rounded-lg border border-gray-200"></div>
                            <div className="w-24 bg-gray-900 h-10 rounded-lg"></div>
                          </div>
                        </section>
                      </div>

                      <ChatbotWidgetPreview
                        key="preview-standard"
                        primaryColor={primaryColor || '#3B82F6'}
                        headerText={formData.header_text}
                        avatarUrl={formData.avatar_url}
                        position={formData.position}
                        offsetX={formData.offset_x}
                        offsetY={formData.offset_y}
                        welcomeMessage={formData.welcome_message}
                        initialSuggestions={formData.initial_suggestions}
                        showBranding={formData.show_branding}
                        contained={true}
                        readOnly={false}
                        chatbotId={chatbotId}
                      />
                    </div>
                    <div className="p-3 bg-blue-50/50 flex items-center justify-center gap-2 border-t">
                      <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                      <p className="text-[11px] text-blue-700 font-semibold uppercase tracking-wider">
                        Fully Interactive Preview
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </form>
        </TabsContent>

        {/* Install Tab */}
        <TabsContent value="install" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Install on Your Website</CardTitle>
              <CardDescription>
                Embed this chatbot on your website with a simple code snippet
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-semibold mb-2">Embed Code</h4>
                  <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm">
                    <pre id="embed-script">{`<script src="${process.env.NEXT_PUBLIC_APP_URL || 'https://chatbot.example.com'}/widget.js"></script>
<script>
  ChatbotWidget.init({
    chatbotId: "${chatbotId}"${process.env.NEXT_PUBLIC_API_URL ? `,\n    apiUrl: "${process.env.NEXT_PUBLIC_API_URL}"` : ''}
  });
</script>`}</pre>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    The widget will automatically fetch appearance settings (position, colors, etc.) from your dashboard.
                    Changes to appearance settings will be reflected automatically without updating the embed code.
                  </p>
                </div>
                <Button variant="outline" onClick={async () => {
                  const el = document.getElementById('embed-script');
                  if (!el) return;
                  const text = el.textContent || '';
                  try {
                    await navigator.clipboard.writeText(text);
                    setEmbedCopyStatus('embed-script')
                    setTimeout(() => setEmbedCopyStatus(null), 2000)
                  } catch {
                    // Fallback if clipboard API isn't available
                    const ta = document.createElement('textarea');
                    ta.value = text;
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    setEmbedCopyStatus('embed-script')
                    setTimeout(() => setEmbedCopyStatus(null), 2000)
                    document.body.removeChild(ta);
                  }
                }} >
                  <Code className="h-4 w-4 mr-2" />
                  Copy Code
                </Button>
                {embedCopyStatus === 'embed-script' ? (
                  <p className="text-sm text-green-600 mt-2">Embed script copied to clipboard.</p>
                ) : null}
              </div>
              <div className="space-y-4 mt-6">
                <div>
                  <h4 className="text-sm font-semibold mb-2">Embed as iframe</h4>
                  <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm">
                    <pre id="embed-iframe">{`<iframe
  src="${process.env.NEXT_PUBLIC_APP_URL || 'https://chatbot.example.com'}/embed/${chatbotId}"
  width="400"
  height="600"
  style="border:0; width:100%; min-width:320px; min-height:420px;"
  title="Chatbot"
></iframe>`}</pre>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Use the iframe option to embed the chat bubble directly on your site.
                  </p>
                </div>
                <Button variant="outline" onClick={async () => {
                  const el = document.getElementById('embed-iframe');
                  if (!el) return;
                  const text = el.textContent || '';
                  try {
                    await navigator.clipboard.writeText(text);
                    setEmbedCopyStatus('embed-iframe')
                    setTimeout(() => setEmbedCopyStatus(null), 2000)
                  } catch {
                    const ta = document.createElement('textarea');
                    ta.value = text;
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    setEmbedCopyStatus('embed-iframe')
                    setTimeout(() => setEmbedCopyStatus(null), 2000)
                    document.body.removeChild(ta);
                  }
                }}>
                  <Code className="h-4 w-4 mr-2" />
                  Copy iframe Code
                </Button>
                {embedCopyStatus === 'embed-iframe' ? (
                  <p className="text-sm text-green-600 mt-2">Iframe embed code copied to clipboard.</p>
                ) : null}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="w-full justify-start border-b rounded-none h-auto p-0 bg-transparent mb-6">
              <TabsTrigger value="general" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2">General</TabsTrigger>
              <TabsTrigger value="team" className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2">Team</TabsTrigger>
            </TabsList>
            <TabsContent value="general" className="space-y-6">
              <Card>
            <CardHeader>
              <CardTitle>Chatbot Settings</CardTitle>
              <CardDescription>
                Update your chatbot&apos;s general information and status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSettingsSubmit} className="space-y-6">
                {settingsError && (
                  <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm">
                    {settingsError}
                  </div>
                )}
                {settingsSuccess && (
                  <div className="p-3 bg-green-50 border border-green-200 text-green-600 rounded-md text-sm">
                    {settingsSuccess}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="chatbot-name">Chatbot Name</Label>
                  <Input
                    id="chatbot-name"
                    name="name"
                    defaultValue={chatbot.name}
                    placeholder="My Awesome Chatbot"
                    required
                    disabled={!canEdit}
                  />
                  <p className="text-xs text-muted-foreground">
                    This is the internal name of your chatbot.
                  </p>
                </div>

                <div className="space-y-3">
                  <Label>Chatbot Status</Label>
                  <RadioGroup
                    name="status"
                    defaultValue={chatbot.status === 'draft' ? 'paused' : chatbot.status}
                    className="grid gap-4 sm:grid-cols-2"
                    disabled={!canEdit}
                  >
                    <div>
                      <RadioGroupItem
                        value="active"
                        id="status-active"
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor="status-active"
                        className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                      >
                        <div className="mb-2 h-4 w-4 rounded-full border border-primary peer-data-[state=checked]:bg-primary" />
                        <span className="text-sm font-semibold">Active</span>
                        <span className="text-xs text-muted-foreground text-center mt-1">
                          Live and responding
                        </span>
                      </Label>
                    </div>
                    <div>
                      <RadioGroupItem
                        value="paused"
                        id="status-paused"
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor="status-paused"
                        className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer"
                      >
                        <div className="mb-2 h-4 w-4 rounded-full border border-primary peer-data-[state=checked]:bg-primary" />
                        <span className="text-sm font-semibold">Paused</span>
                        <span className="text-xs text-muted-foreground text-center mt-1">
                          Temporarily offline
                        </span>
                      </Label>
                    </div>
                  </RadioGroup>
                  {chatbot.status === 'draft' && (
                    <p className="text-sm text-yellow-600 font-medium">
                      This chatbot is currently in Draft mode. Change it to Active to make it live.
                    </p>
                  )}
                </div>

                <div className="flex justify-end pt-4 border-t">
                  <Button type="submit" disabled={isSavingSettings || !canEdit}>
                    {isSavingSettings ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Settings
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {['owner', 'admin'].includes(chatbot.permission_level) && (
            <Card className="border-red-100">
              <CardHeader>
                <CardTitle className="text-red-600">Danger Zone</CardTitle>
                <CardDescription>
                  Permanently delete this chatbot and all its data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="destructive" className="bg-red-600 hover:bg-red-700" onClick={handleDeleteChatbot}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Chatbot
                </Button>
              </CardContent>
            </Card>
          )}
            </TabsContent>
            <TabsContent value="team" className="space-y-6">
              <ChatbotTeamSettings chatbotId={chatbotId} />
            </TabsContent>
          </Tabs>
        </TabsContent>
      </Tabs>
    </div>
  )
}


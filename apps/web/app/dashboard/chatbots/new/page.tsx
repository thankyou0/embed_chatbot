'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Loader2, 
  ChevronRight, 
  ChevronLeft, 
  Plus, 
  Globe, 
  Check, 
  X,
  ExternalLink,
  MessageSquare,
  Database,
  Search
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'
import { useAuth } from '@/contexts/AuthContext'
import { Badge } from '@/components/ui/badge'

type Step = 1 | 2 | 3

interface KnowledgeSource {
  id: string
  source_type: string
  source_url: string | null
  status: 'pending' | 'crawling' | 'completed' | 'failed'
  pages_found: number
  created_at: string
}

export default function NewChatbotWizard() {
  const router = useRouter()
  const [step, setStep] = useState<Step>(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Step 1: Basic Info
  const [name, setName] = useState('')
  const [welcomeMessage, setWelcomeMessage] = useState('Hi! How can I help you today?')
  
  // Step 2: Knowledge
  const [chatbotId, setChatbotId] = useState<string | null>(null)
  const [url, setUrl] = useState('')
  const [isCrawling, setIsCrawling] = useState(false)
  const [knowledgeSourceId, setKnowledgeSourceId] = useState<string | null>(null)
  const [crawlStatus, setCrawlStatus] = useState<KnowledgeSource | null>(null)
  
  // Step 1 -> Step 2: Create chatbot first
  const handleStep1Submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      const response = await apiRequestWithAuth<{ id: string }>(
        '/api/v1/chatbots',
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            name: name,
            welcome_message: welcomeMessage,
          }),
        }
      )
      
      setChatbotId(response.id)
      setStep(2)
    } catch (err: any) {
      setError(err.message || 'Failed to create chatbot')
    } finally {
      setIsLoading(false)
    }
  }

  // Step 2: Start Crawling
  const handleStartCrawl = async () => {
    if (!url.trim() || !chatbotId) return
    
    setIsCrawling(true)
    setError(null)
    
    try {
      const token = getAccessToken()
      if (!token) return

      const response = await apiRequestWithAuth<KnowledgeSource>(
        `/api/v1/chatbots/${chatbotId}/crawl`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            base_url: url,
            max_pages: 500
          }),
        }
      )
      
      setKnowledgeSourceId(response.id)
      setCrawlStatus(response)
    } catch (err: any) {
      setError(err.message || 'Failed to start crawling')
      setIsCrawling(false)
    }
  }

  // Polling for crawl status
  useEffect(() => {
    let intervalId: NodeJS.Timeout

    if (isCrawling && knowledgeSourceId) {
      intervalId = setInterval(async () => {
        try {
          const token = getAccessToken()
          if (!token) return

          const response = await apiRequestWithAuth<KnowledgeSource>(
            `/api/v1/chatbots/knowledge-sources/${knowledgeSourceId}/status`,
            token,
            { method: 'GET' }
          )
          
          setCrawlStatus(response)
          
          if (response.status === 'completed' || response.status === 'failed') {
            setIsCrawling(false)
            clearInterval(intervalId)
          }
        } catch (err) {
          console.error('Polling error:', err)
        }
      }, 2000)
    }

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [isCrawling, knowledgeSourceId])

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3].map((s) => (
        <div key={s} className="flex items-center">
          <div className={`
            w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
            ${step === s ? 'bg-blue-600 text-white' : 
              step > s ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'}
          `}>
            {step > s ? <Check className="h-5 w-5" /> : s}
          </div>
          {s < 3 && (
            <div className={`w-16 h-1 mx-2 ${step > s ? 'bg-green-500' : 'bg-gray-200'}`} />
          )}
        </div>
      ))}
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold mb-2">Create New Chatbot</h1>
        <p className="text-gray-600">Follow the steps to build your custom AI assistant</p>
      </div>

      {renderStepIndicator()}

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Tell us about your chatbot&apos;s identity</CardDescription>
          </CardHeader>
          <form onSubmit={handleStep1Submit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name *</Label>
                <Input 
                  id="name" 
                  placeholder="e.g. Customer Support Bot" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="welcome">Welcome Message</Label>
                <Input 
                  id="welcome" 
                  placeholder="e.g. Hi! How can I help you today?" 
                  value={welcomeMessage}
                  onChange={(e) => setWelcomeMessage(e.target.value)}
                />
              </div>
              {error && <p className="text-sm text-red-500">{error}</p>}
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button type="submit" disabled={isLoading || !name.trim()}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Next: Add Knowledge <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </CardFooter>
          </form>
        </Card>
      )}

      {/* Step 2: Knowledge Base */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Add Knowledge</CardTitle>
            <CardDescription>Provide a URL for your chatbot to learn from</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="url">Website URL</Label>
              <div className="flex gap-2">
                <Input 
                  id="url" 
                  placeholder="https://example.com/docs" 
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={isCrawling}
                />
                <Button 
                  onClick={handleStartCrawl} 
                  disabled={isCrawling || !url.trim()}
                >
                  {isCrawling ? 'Crawling...' : 'Start Crawling'}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                We&apos;ll crawl up to 500 pages from this domain.
              </p>
            </div>

            {crawlStatus && (
              <div className="bg-muted p-4 rounded-lg space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium flex items-center gap-2">
                    {crawlStatus.status === 'completed' ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : crawlStatus.status === 'failed' ? (
                      <X className="h-4 w-4 text-red-500" />
                    ) : (
                      <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                    )}
                    Status: <span className="capitalize">{crawlStatus.status}</span>
                  </span>
                  <Badge variant="outline">{crawlStatus.pages_found} pages found</Badge>
                </div>
                
                {crawlStatus.status === 'crawling' && (
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div className="bg-blue-600 h-1.5 rounded-full animate-pulse" style={{ width: '100%' }}></div>
                  </div>
                )}
                
                {crawlStatus.status === 'completed' && (
                  <div className="text-sm text-green-600 flex items-center gap-1">
                    <Check className="h-4 w-4" /> 
                    Crawling and embedding complete!
                  </div>
                )}
              </div>
            )}
            
            {error && <p className="text-sm text-red-500">{error}</p>}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="ghost" onClick={() => setStep(3)}>Skip for now</Button>
            <Button onClick={() => setStep(3)} disabled={isCrawling}>
              Next: Review <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Step 3: Review */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Review & Finalize</CardTitle>
            <CardDescription>Check everything before going live</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex justify-between items-start pb-4 border-bottom border-gray-100">
                <div>
                  <h4 className="font-semibold text-gray-900">Chatbot Details</h4>
                  <p className="text-sm text-gray-600">{name}</p>
                  <p className="text-xs text-gray-400 mt-1 italic">&quot;{welcomeMessage}&quot;</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setStep(1)}>Edit</Button>
              </div>

              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-gray-900">Knowledge Sources</h4>
                  {crawlStatus ? (
                    <div className="flex items-center gap-2 mt-1">
                      <Globe className="h-3 w-3 text-gray-400" />
                      <span className="text-sm text-gray-600 truncate max-w-[200px]">{url}</span>
                      <Badge variant="success" className="text-[10px] h-4">
                        {crawlStatus.pages_found} pages
                      </Badge>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 italic">No knowledge added yet</p>
                  )}
                </div>
                <Button variant="ghost" size="sm" onClick={() => setStep(2)}>Edit</Button>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={() => setStep(2)}>
              <ChevronLeft className="mr-2 h-4 w-4" /> Back
            </Button>
            <Button onClick={() => router.push(`/dashboard/chatbots/${chatbotId}`)}>
              Create Chatbot & Finish <Check className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}


'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { MessageSquare, Plus, X, Loader2 } from 'lucide-react'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'


interface Chatbot {
  id: string
  name: string
  welcome_message: string | null
  status: 'draft' | 'active' | 'paused'
  created_at: string
  permission_level: string
}

export default function ChatbotsPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [chatbots, setChatbots] = useState<Chatbot[]>([])
  const router = useRouter()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState<{ name: string; description: string }>({ name: '', description: '' })
  const [error, setError] = useState<string | null>(null)

  const fetchChatbots = async () => {
    try {
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      const response = await apiRequestWithAuth<{ chatbots: Chatbot[], total: number }>(
        '/api/v1/chatbots',
        token,
        { method: 'GET' }
      )
      setChatbots(response.chatbots)
    } catch (err) {
      console.error('Failed to fetch chatbots:', err)
    }
  }

  // Fetch chatbots on mount
  useEffect(() => {
    fetchChatbots()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCreateChatbot = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      const response = await apiRequestWithAuth<Chatbot>(
        '/api/v1/chatbots',
        token,
        {
          method: 'POST',
          body: JSON.stringify({
            name: formData.name,
            welcome_message: formData.description || null,
          }),
        }
      )

      // Reset form and close modal
      setFormData({ name: '', description: '' })
      setIsModalOpen(false)
      
      // Refresh chatbots list
      await fetchChatbots()
    } catch (err: any) {
      setError(err.message || 'Failed to create chatbot')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chatbots</h1>
          <p className="text-muted-foreground">
            Manage your AI chatbots and conversations
          </p>
        </div>
        <Link href="/dashboard/chatbots/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Chatbot
          </Button>
        </Link>
      </div>

      {/* Chatbots List */}
      {chatbots.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {chatbots.map((chatbot) => (
            <Link key={chatbot.id} href={`/dashboard/chatbots/${chatbot.id}`}>
              <Card className="cursor-pointer hover:shadow-md transition-shadow h-full">
                <CardHeader>
                  <CardTitle>{chatbot.name}</CardTitle>
                  <CardDescription>
                    {chatbot.welcome_message || 'No welcome message'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Permission: {chatbot.permission_level}</span>
                    <span
                      className={
                        chatbot.status === 'active'
                          ? 'text-green-600'
                          : chatbot.status === 'paused'
                          ? 'text-yellow-600'
                          : 'text-gray-500'
                      }
                    >
                      {chatbot.status}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>No chatbots yet</CardTitle>
            <CardDescription>
              Get started by creating your first AI chatbot
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
                <MessageSquare className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold">Create your first chatbot</h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Build custom AI chatbots for your website, customer support, or
                  internal tools.
                </p>
              </div>
              <Button onClick={() => setIsModalOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Chatbot
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


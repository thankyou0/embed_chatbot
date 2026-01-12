'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2, Upload, Sparkles, Save, Maximize2, Minimize2, ShoppingCart, Search as SearchIcon, Menu as MenuIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { createPortal } from 'react-dom'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'
import { cn } from '@/lib/utils'
import { ChatbotWidgetPreview } from '@/components/chatbot/WidgetPreview'

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

export default function AppearancePage() {
  const params = useParams()
  const router = useRouter()
  const chatbotId = params.chatbotId as string
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [newSuggestion, setNewSuggestion] = useState('')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const avatarInputRef = useRef<HTMLInputElement | null>(null)

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
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors, isDirty },
  } = useForm<AppearanceFormData>({
    resolver: zodResolver(appearanceSchema),
    mode: 'onChange', // Enable real-time validation and updates
    defaultValues: {
      primary_color: '#2563eb',
      header_text: 'Chat with us',
      avatar_url: null,
      position: 'bottom-right',
      offset_x: 0,
      offset_y: 0,
      welcome_message: null,
      initial_suggestions: [],
      show_branding: true,
    },
  })

  // Use useWatch for real-time updates - this will trigger re-renders when values change
  const formData = useWatch({ control }) || watch()
  const primaryColor = useWatch({ control, name: 'primary_color' }) || formData.primary_color || '#2563eb'

  useEffect(() => {
    fetchAppearance()
  }, [chatbotId])

  const fetchAppearance = async () => {
    try {
      setIsLoading(true)
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      const data = await apiRequestWithAuth<AppearanceData>(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        { method: 'GET' }
      )
      
      // Set form values
      Object.keys(data).forEach((key) => {
        if (key in appearanceSchema.shape) {
          setValue(key as keyof AppearanceFormData, data[key as keyof AppearanceData] as any)
        }
      })
      
      setError(null)
    } catch (err: any) {
      console.error('Failed to fetch appearance:', err)
      setError(err.message || 'Failed to load appearance settings')
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data: AppearanceFormData) => {
    try {
      setIsSaving(true)
      const token = getAccessToken()
      if (!token) {
        router.push('/login')
        return
      }

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}/appearance`,
        token,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      )
      
      setSuccessMessage('Appearance settings saved successfully!')
      setTimeout(() => setSuccessMessage(null), 3000)
      
      // Refresh to reset isDirty
      await fetchAppearance()
    } catch (err: any) {
      console.error('Failed to save appearance:', err)
      setError(err.message || 'Failed to save appearance settings')
    } finally {
      setIsSaving(false)
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

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-blue-600" />
          Appearance Customization
        </h1>
        <p className="text-gray-600 mt-2">
          Customize how your chatbot looks and feels to match your brand
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
          {successMessage}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
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
                    onChange={(e) => {
                      setValue('header_text', e.target.value, { shouldValidate: false, shouldDirty: true })
                    }}
                    placeholder="Chat with us"
                  />
                  {errors.header_text && (
                    <p className="text-sm text-red-600 mt-1">{errors.header_text.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="welcome_message">Welcome Message</Label>
                  <Textarea
                    id="welcome_message"
                    {...register('welcome_message')}
                    onChange={(e) => {
                      setValue('welcome_message', e.target.value, { shouldValidate: false, shouldDirty: true })
                    }}
                    placeholder="Hi! How can I help you today?"
                    rows={3}
                  />
                  {errors.welcome_message && (
                    <p className="text-sm text-red-600 mt-1">{errors.welcome_message.message}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Branding */}
            <Card>
              <CardHeader>
                <CardTitle>Branding</CardTitle>
                <CardDescription>Colors and visual identity</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="primary_color">Primary Color</Label>
                  <div className="flex gap-2 items-center mt-1">
                    <div 
                      className="relative w-12 h-10 rounded-md border border-input overflow-hidden shrink-0 shadow-sm transition-colors duration-200"
                      style={{ backgroundColor: primaryColor || formData.primary_color || '#2563eb' }}
                    >
                    <input
                      type="color"
                      id="primary_color_picker"
                      value={primaryColor || formData.primary_color || '#2563eb'}
                      onChange={(e) => {
                        const colorValue = e.target.value
                        setValue('primary_color', colorValue, { shouldDirty: true, shouldValidate: true })
                      }}
                      className="absolute inset-0 w-[200%] h-[200%] -top-1/2 -left-1/2 cursor-pointer opacity-0"
                    />
                    </div>
                    <div className="relative flex-1">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-mono text-sm">#</span>
                      <Input
                        type="text"
                        name="primary_color"
                        placeholder="2563eb"
                        className="pl-7 font-mono"
                        value={(primaryColor || '').replace(/^#/, '')}
                        onChange={(e) => {
                          let val = e.target.value.trim();
                          // Remove any existing # and add it back
                          val = val.replace(/^#/, '');
                          // Only allow hex characters
                          val = val.replace(/[^0-9A-Fa-f]/g, '');
                          // Limit to 6 characters
                          val = val.slice(0, 6);
                          // Add # prefix
                          const colorValue = val ? '#' + val : '';
                          setValue('primary_color', colorValue, { shouldDirty: true });
                        }}
                      />
                    </div>
                  </div>
                  {errors.primary_color && (
                    <p className="text-sm text-red-600 mt-1">{errors.primary_color.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="avatar_url">Avatar URL</Label>
                <div className="space-y-2">
                    <Input
                      id="avatar_url"
                      {...register('avatar_url')}
                      onChange={(e) => {
                        setValue('avatar_url', e.target.value || null, { shouldValidate: false, shouldDirty: true })
                      }}
                      placeholder="https://example.com/avatar.png"
                    />
                    <input ref={avatarInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={async (e) => {
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
                          // Refresh appearance so avatar_url updates
                          fetchAppearance()
                          setSuccessMessage('Avatar uploaded successfully!')
                          setTimeout(() => setSuccessMessage(null), 3000)
                        } else {
                          const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
                          setError(err.detail || 'Avatar upload failed')
                        }
                      } catch (err) {
                        setError('Avatar upload error')
                      } finally {
                        // Reset input so uploading same file again triggers onchange
                        if (avatarInputRef.current) avatarInputRef.current.value = ''
                      }
                    }} />
                    <Button type="button" variant="outline" size="sm" className="w-full" onClick={() => avatarInputRef.current?.click()}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Custom Avatar
                    </Button>
                  </div>
                  {errors.avatar_url && (
                    <p className="text-sm text-red-600 mt-1">{errors.avatar_url.message}</p>
                  )}
                </div>

              {/* Avatar Upload Card - explicit visibility if branding area collapses */ }
              <Card>
                <CardHeader>
                  <CardTitle>Avatar Upload</CardTitle>
                  <CardDescription>Upload a custom avatar image for the chatbot appearance</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Button type="button" variant="outline" size="sm" onClick={() => avatarInputRef.current?.click()}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Custom Avatar
                    </Button>
                    <input ref={avatarInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={async (e) => {
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
                          setSuccessMessage('Avatar uploaded successfully!')
                          setTimeout(() => setSuccessMessage(null), 3000)
                        } else {
                          const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
                          setError(err.detail || 'Avatar upload failed')
                        }
                      } catch {
                        setError('Avatar upload error')
                      } finally {
                        if (avatarInputRef.current) avatarInputRef.current.value = ''
                      }
                    }} />
                  </div>
                </CardContent>
              </Card>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="show_branding">Show &quot;Powered By&quot;</Label>
                    <p className="text-sm text-gray-500">Display branding in the widget</p>
                  </div>
                  <Switch
                    id="show_branding"
                    checked={formData.show_branding}
                    onCheckedChange={(checked) => setValue('show_branding', checked, { shouldDirty: true })}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Behavior */}
            <Card>
              <CardHeader>
                <CardTitle>Behavior</CardTitle>
                <CardDescription>Widget positioning and suggestions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Widget Position</Label>
                  <RadioGroup
                    value={formData.position}
                    onValueChange={(value) => setValue('position', value as 'bottom-right' | 'bottom-left', { shouldDirty: true })}
                    className="flex gap-4 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="bottom-left" id="bottom-left" />
                      <Label htmlFor="bottom-left" className="font-normal cursor-pointer">
                        Bottom Left
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="bottom-right" id="bottom-right" />
                      <Label htmlFor="bottom-right" className="font-normal cursor-pointer">
                        Bottom Right
                      </Label>
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
                      onChange={(e) => {
                        setValue('offset_x', parseInt(e.target.value) || 0, { shouldValidate: false, shouldDirty: true })
                      }}
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
                      onChange={(e) => {
                        setValue('offset_y', parseInt(e.target.value) || 0, { shouldValidate: false, shouldDirty: true })
                      }}
                      placeholder="0"
                    />
                    {errors.offset_y && (
                      <p className="text-sm text-red-600 mt-1">{errors.offset_y.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <Label>Initial Suggestions</Label>
                  <p className="text-sm text-gray-500 mb-2">
                    Quick prompts users can click to start a conversation
                  </p>
                  <div className="space-y-2">
                    {formData.initial_suggestions.map((suggestion, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Input value={suggestion} readOnly className="flex-1 bg-gray-50" />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveSuggestion(index)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        >
                          Remove
                        </Button>
                      </div>
                    ))}
                    <div className="flex gap-2">
                      <Input
                        value={newSuggestion}
                        onChange={(e) => setNewSuggestion(e.target.value)}
                        placeholder="e.g., How can I track my order?"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault()
                            handleAddSuggestion()
                          }
                        }}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleAddSuggestion}
                        disabled={!newSuggestion.trim()}
                      >
                        Add
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Save Buttons */}
            <div className="flex items-center justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => fetchAppearance()}
                disabled={isSaving || !isDirty}
              >
                Reset Changes
              </Button>
              <Button type="submit" disabled={isSaving || !isDirty}>
                {isSaving ? (
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
                    key={`preview-fullscreen-${chatbotId}`}
                    primaryColor={formData.primary_color || '#2563eb'}
                    headerText={formData.header_text}
                    avatarUrl={formData.avatar_url}
                    position={formData.position}
                    offsetX={formData.offset_x}
                    offsetY={formData.offset_y}
                    welcomeMessage={formData.welcome_message}
                    initialSuggestions={formData.initial_suggestions}
                    showBranding={formData.show_branding}
                    contained={true}
                    initialOpen={true}
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
                    key={`preview-standard-${chatbotId}`}
                    primaryColor={formData.primary_color || '#2563eb'}
                    headerText={formData.header_text}
                    avatarUrl={formData.avatar_url}
                    position={formData.position}
                    offsetX={formData.offset_x}
                    offsetY={formData.offset_y}
                    welcomeMessage={formData.welcome_message}
                    initialSuggestions={formData.initial_suggestions}
                    showBranding={formData.show_branding}
                    contained={true}
                    initialOpen={true}
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
    </div>
  )
}


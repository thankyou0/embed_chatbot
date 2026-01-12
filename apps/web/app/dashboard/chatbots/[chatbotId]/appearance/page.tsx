'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useForm, Controller, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2, Upload, Sparkles, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { apiRequestWithAuth } from '@/lib/api'
import { getAccessToken } from '@/lib/auth'

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
  // #region agent log
  console.log('🚀 APPEARANCE PAGE COMPONENT MOUNTED')
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:44',message:'Component mounted',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch((e)=>{console.error('Log fetch failed:',e)});
  // #endregion
  const params = useParams()
  const router = useRouter()
  const chatbotId = params.chatbotId as string
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [newSuggestion, setNewSuggestion] = useState('')
  const avatarInputRef = useRef<HTMLInputElement | null>(null)
  
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
  // #region agent log
  console.log('📋 FORM INITIALIZED - control exists:', !!control, 'mode:', 'onChange')
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:89',message:'Form initialized',data:{hasControl:!!control,mode:'onChange'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch((e)=>{console.error('Log fetch failed:',e)});
  // #endregion

  // Use useWatch with defaultValue to ensure it works correctly
  // This is the key for live preview - each field change triggers a re-render
  const watchedPrimaryColor = useWatch({ control, name: 'primary_color', defaultValue: '#2563eb' })
  const watchedHeaderText = useWatch({ control, name: 'header_text', defaultValue: 'Chat with us' })
  const watchedWelcomeMessage = useWatch({ control, name: 'welcome_message', defaultValue: null })
  const watchedAvatarUrl = useWatch({ control, name: 'avatar_url', defaultValue: null })
  const watchedPosition = useWatch({ control, name: 'position', defaultValue: 'bottom-right' })
  const watchedOffsetX = useWatch({ control, name: 'offset_x', defaultValue: 0 })
  const watchedOffsetY = useWatch({ control, name: 'offset_y', defaultValue: 0 })
  const watchedInitialSuggestions = useWatch({ control, name: 'initial_suggestions', defaultValue: [] })
  const watchedShowBranding = useWatch({ control, name: 'show_branding', defaultValue: true })
  
  // #region agent log
  console.log('👀 USEWATCH CALLED - headerText:', watchedHeaderText, 'primaryColor:', watchedPrimaryColor, 'hasControl:', !!control)
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:101',message:'useWatch hooks called',data:{watchedHeaderText,watchedPrimaryColor,hasControl:!!control},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch((e)=>{console.error('Log fetch failed:',e)});
  // #endregion
  
  // Alternative: Use watch() subscription to force re-renders when form changes
  const [renderKey, setRenderKey] = useState(0)
  useEffect(() => {
    // #region agent log
    console.log('📺 Setting up watch subscription')
    // #endregion
    const subscription = watch((value, { name, type }) => {
      // #region agent log
      console.log('📺 WATCH SUBSCRIPTION - field changed:', name, 'type:', type, 'value:', name ? value[name as keyof typeof value] : 'all')
      fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:120',message:'Watch subscription triggered',data:{fieldName:name,fieldType:type,value:name ? value[name as keyof typeof value] : value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch((e)=>{console.error('Log fetch failed:',e)});
      // #endregion
      setRenderKey(prev => prev + 1) // Force re-render
    })
    return () => subscription.unsubscribe()
  }, [watch])
  
  // Debug: Log when individual watched values change
  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:107',message:'Watched Header Text changed',data:{watchedHeaderText},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    console.log('🔍 Watched Header Text changed:', watchedHeaderText)
  }, [watchedHeaderText])
  
  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:113',message:'Watched Primary Color changed',data:{watchedPrimaryColor},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    console.log('🔍 Watched Primary Color changed:', watchedPrimaryColor)
  }, [watchedPrimaryColor])
  
  // Get current form values using watch() - this ensures we have the latest values
  const currentFormValues = watch()
  
  // Combine watched values with current form values (fallback to watch() if useWatch returns undefined)
  const watchedValues = {
    primary_color: watchedPrimaryColor ?? currentFormValues?.primary_color ?? '#2563eb',
    header_text: watchedHeaderText ?? currentFormValues?.header_text ?? 'Chat with us',
    welcome_message: watchedWelcomeMessage ?? currentFormValues?.welcome_message ?? null,
    avatar_url: watchedAvatarUrl ?? currentFormValues?.avatar_url ?? null,
    position: watchedPosition ?? currentFormValues?.position ?? 'bottom-right',
    offset_x: watchedOffsetX ?? currentFormValues?.offset_x ?? 0,
    offset_y: watchedOffsetY ?? currentFormValues?.offset_y ?? 0,
    initial_suggestions: watchedInitialSuggestions ?? currentFormValues?.initial_suggestions ?? [],
    show_branding: watchedShowBranding !== undefined ? watchedShowBranding : (currentFormValues?.show_branding ?? true),
  }
  
  // #region agent log
  useEffect(() => {
    console.log('🔄 RENDER KEY CHANGED (form updated):', renderKey, 'watchedValues:', watchedValues)
  }, [renderKey])
  // #endregion
  
  // Debug: Log when watchedValues object changes
  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:144',message:'Watched Values Object changed',data:watchedValues,timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
    // #endregion
    console.log('📊 Watched Values Object:', watchedValues)
  }, [watchedValues.primary_color, watchedValues.header_text, watchedValues.welcome_message])

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
          // #region agent log
          fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:171',message:'setValue called in fetchAppearance',data:{key,value:data[key as keyof AppearanceData]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
          // #endregion
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
      const currentSuggestions = watchedValues.initial_suggestions || []
      setValue('initial_suggestions', [...currentSuggestions, newSuggestion.trim()], { shouldDirty: true })
      setNewSuggestion('')
    }
  }

  const handleRemoveSuggestion = (index: number) => {
    const currentSuggestions = watchedValues.initial_suggestions || []
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

      {/* #region agent log */}
      {console.log('🎨 RENDERING FORM - watchedValues:', watchedValues)}
      {/* #endregion */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="max-w-4xl">
          {/* Settings Form */}
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
                  <Controller
                    name="header_text"
                    control={control}
                    render={({ field }) => (
                      <Input
                        value={field.value || ''}
                        onChange={(e: any) => {
                          // #region agent log
                          fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:264',message:'Header Text onChange fired',data:{newValue:e.target.value,oldValue:field.value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                          // #endregion
                          console.log('✏️ Header Text onChange called with:', e.target.value)
                          field.onChange(e.target.value)
                          // #region agent log
                          fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:267',message:'field.onChange called',data:{value:e.target.value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                          // #endregion
                          console.log('✅ field.onChange called, current field.value:', field.value)
                        }}
                        onBlur={field.onBlur}
                        ref={field.ref}
                        placeholder="Chat with us"
                      />
                    )}
                  />
                  {errors.header_text && (
                    <p className="text-sm text-red-600 mt-1">{errors.header_text.message}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="welcome_message">Welcome Message</Label>
                  <Controller
                    name="welcome_message"
                    control={control}
                    render={({ field }) => (
                      <Textarea
                        value={field.value || ''}
                        onChange={(e: any) => {
                          field.onChange(e.target.value)
                        }}
                        onBlur={field.onBlur}
                        ref={field.ref}
                        placeholder="Hi! How can I help you today?"
                        rows={3}
                      />
                    )}
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
                      style={{ backgroundColor: watchedValues.primary_color || '#2563eb' }}
                    >
                    <input
                      type="color"
                      id="primary_color_picker"
                      value={watchedValues.primary_color || '#2563eb'}
                      onChange={(e) => {
                        const colorValue = e.target.value
                        // #region agent log
                        fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:321',message:'Color picker onChange fired',data:{colorValue},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                        // #endregion
                        console.log('🎨 Color picker onChange called with:', colorValue)
                        setValue('primary_color', colorValue, { shouldDirty: true, shouldValidate: true })
                        // #region agent log
                        fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:324',message:'setValue called for primary_color',data:{colorValue},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                        // #endregion
                        console.log('✅ setValue called for primary_color')
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
                        value={(watchedValues.primary_color || '').replace(/^#/, '')} // Use watchedValues here
                        onChange={(e) => {
                          let val = e.target.value.trim().replace(/^#/, '').replace(/[^0-9A-Fa-f]/g, '').slice(0, 6);
                          const colorValue = val ? '#' + val : '';
                          // #region agent log
                          fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:370',message:'Color input onChange fired',data:{colorValue,rawValue:e.target.value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                          // #endregion
                          console.log('🎨 Color input onChange called with:', colorValue)
                          setValue('primary_color', colorValue, { shouldDirty: true }); 
                          // #region agent log
                          fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'appearance/page.tsx:373',message:'setValue called for primary_color from input',data:{colorValue},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
                          // #endregion
                          console.log('✅ setValue called for primary_color from input')
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
                    <Controller
                      name="avatar_url"
                      control={control}
                      render={({ field }) => (
                        <Input
                          value={field.value || ''}
                          onChange={(e: any) => {
                            field.onChange(e.target.value || null)
                          }}
                          onBlur={field.onBlur}
                          ref={field.ref}
                          placeholder="https://example.com/avatar.png"
                        />
                      )}
                    />
                    <input ref={avatarInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={async (e: React.ChangeEvent<HTMLInputElement>) => {
                      const file = e.target.files?.[0] as File | null
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
                    <input ref={avatarInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={async (e: React.ChangeEvent<HTMLInputElement>) => {
                      const file = e.target.files?.[0] as File | null
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
                    checked={watchedValues.show_branding}
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
                    value={watchedValues.position}
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
                    <Controller
                      name="offset_x"
                      control={control}
                      render={({ field }) => (
                        <Input
                          type="number"
                          value={field.value || 0}
                          onChange={(e: any) => {
                            const value = parseInt(e.target.value) || 0
                            field.onChange(value)
                          }}
                          onBlur={field.onBlur}
                          ref={field.ref}
                          placeholder="0"
                        />
                      )}
                    />
                    {errors.offset_x && (
                      <p className="text-sm text-red-600 mt-1">{errors.offset_x.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="offset_y">Offset Y (px)</Label>
                    <Controller
                      name="offset_y"
                      control={control}
                      render={({ field }) => (
                        <Input
                          type="number"
                          value={field.value || 0}
                          onChange={(e: any) => {
                            const value = parseInt(e.target.value) || 0
                            field.onChange(value)
                          }}
                          onBlur={field.onBlur}
                          ref={field.ref}
                          placeholder="0"
                        />
                      )}
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
                    {watchedValues.initial_suggestions?.map((suggestion: string, index: number) => (
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
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewSuggestion(e.target.value)}
                        placeholder="e.g., How can I track my order?"
                         onKeyDown={(e: any) => {
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
        </div>
      </form>
    </div>
  )
}


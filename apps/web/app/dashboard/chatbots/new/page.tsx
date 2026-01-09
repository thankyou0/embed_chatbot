'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

export default function NewChatbotPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to chatbots list page (which has the modal)
    router.replace('/dashboard/chatbots')
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
    </div>
  )
}

'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { getAccessToken } from '@/lib/auth'
import { apiRequestWithAuth } from '@/lib/api'
import {
  Shield,
  User,
  Plus,
  Trash2,
  Check,
  X,
  Loader2,
  Users,
  AlertCircle,
  MoreVertical,
  Mail,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface Member {
  id: number
  email: string
  name: string | null
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
  chatbot_permissions?: { chatbot_id: string, chatbot_name: string }[]
}

export default function TeamPage() {
  const { user, isAdmin, loading: authLoading } = useAuth()
  const router = useRouter()
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Add Member State
  const [showAddModal, setShowAddModal] = useState(false)
  const [newMember, setNewMember] = useState({
    email: '',
    name: '',
    role: 'user',
    password: '',
    expiry_hours: 72
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
      return
    }
    if (!authLoading && user && !isAdmin) {
      router.push('/dashboard')
      return
    }
    if (!authLoading && isAdmin) {
      fetchData()
    }
  }, [authLoading, user, isAdmin, router])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const token = getAccessToken()
      if (!token) throw new Error('No access token')

      const response = await apiRequestWithAuth<{ members: Member[]; total: number }>('/api/v1/members', token)
      setMembers(response.members)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load team data')
    } finally {
      setLoading(false)
    }
  }

  const generatePassword = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%'
    let password = ''
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setNewMember({ ...newMember, password })
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      const token = getAccessToken()
      if (!token) throw new Error('No access token')

      await apiRequestWithAuth('/api/v1/members', token, {
        method: 'POST',
        body: JSON.stringify({
          email: newMember.email,
          password: newMember.password,
          name: newMember.name || null,
          role: newMember.role,
          password_expiry_hours: newMember.expiry_hours,
        }),
      })

      setShowAddModal(false)
      setNewMember({
        email: '',
        name: '',
        role: 'user',
        password: '',
        expiry_hours: 72
      })
      fetchData()
    } catch (err: any) {
      alert(err.message || 'Failed to add member')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveMember = async (memberId: number) => {
    if (!confirm('Are you sure you want to remove this member? This will remove their access to all chatbots.')) return

    try {
      const token = getAccessToken()
      if (!token) throw new Error('No access token')

      await apiRequestWithAuth(`/api/v1/members/${memberId}`, token, {
        method: 'DELETE',
      })

      fetchData()
    } catch (err: any) {
      alert(err.message || 'Failed to remove member')
    }
  }

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    )
  }

  if (!isAdmin) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Organization Team</h1>
          <p className="text-muted-foreground">
            Manage your organization members and their roles.
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Member
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

      <div className="grid gap-4">
        {members.map((member) => (
          <Card key={member.id}>
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-medium">
                  {(member.name || member.email)[0].toUpperCase()}
                </div>
                <div>
                  <div className="font-medium flex items-center gap-2">
                    {member.name || 'No Name'}
                    {member.role === 'admin' && (
                      <Badge variant="secondary" className="text-xs">Org Admin</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground flex items-center gap-1">
                    <Mail className="h-3 w-3" />
                    {member.email}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-sm text-right">
                  <div className="text-muted-foreground">Access</div>
                  <div className="font-medium">
                    {member.role === 'admin' 
                      ? 'Full Access' 
                      : `${member.chatbot_permissions?.length || 0} Chatbots`
                    }
                  </div>
                </div>

                <div className="text-sm text-right">
                  <div className="text-muted-foreground">Status</div>
                  <div className={`font-medium ${member.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {member.is_active ? 'Active' : 'Disabled'}
                  </div>
                </div>

                {member.id !== user?.id && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={() => handleRemoveMember(member.id)} className="text-red-600">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remove Member
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Custom Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full shadow-xl">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Add Organization Member</h2>
                <p className="text-sm text-muted-foreground">
                  Create a new account for a team member.
                </p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setShowAddModal(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleAddMember} className="p-6 space-y-4">
              <div className="space-y-2">
                <Label>Email Address</Label>
                <Input
                  type="email"
                  required
                  placeholder="colleague@company.com"
                  value={newMember.email}
                  onChange={(e) => setNewMember({...newMember, email: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input
                  placeholder="John Doe"
                  value={newMember.name}
                  onChange={(e) => setNewMember({...newMember, name: e.target.value})}
                />
              </div>

              <div className="space-y-2">
                <Label>Role</Label>
                <select
                  className="w-full h-10 px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  value={newMember.role}
                  onChange={(e) => setNewMember({...newMember, role: e.target.value as 'admin' | 'user'})}
                >
                  <option value="user">Member (Assigned access only)</option>
                  <option value="admin">Admin (Full organization access)</option>
                </select>
                <p className="text-xs text-muted-foreground mt-1">
                  Admins can see and manage all chatbots. Members only see chatbots they are assigned to.
                </p>
              </div>

              <div className="space-y-2">
                <Label>Temporary Password</Label>
                <div className="flex gap-2">
                  <Input
                    value={newMember.password}
                    onChange={(e) => setNewMember({...newMember, password: e.target.value})}
                    required
                    minLength={8}
                    placeholder="Enter or generate..."
                  />
                  <Button type="button" variant="outline" onClick={generatePassword}>Generate</Button>
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <Button variant="outline" className="flex-1" type="button" onClick={() => setShowAddModal(false)}>
                  Cancel
                </Button>
                <Button className="flex-1" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create Account'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

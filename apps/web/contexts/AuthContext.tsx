'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { 
  User, 
  Tenant, 
  signup, 
  login, 
  getMe, 
  logout as authLogout, 
  changePassword as authChangePassword,
  SignupData, 
  LoginData,
  ChangePasswordData
} from '@/lib/auth'

interface AuthContextType {
  user: User | null
  tenant: Tenant | null
  loading: boolean
  isAdmin: boolean
  mustChangePassword: boolean
  signup: (data: SignupData) => Promise<void>
  login: (data: LoginData) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  changePassword: (data: ChangePasswordData) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [tenant, setTenant] = useState<Tenant | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  const isAdmin = user?.role === 'admin'
  const mustChangePassword = user?.must_change_password ?? false

  const refreshUser = async () => {
    try {
      const data = await getMe()
      setUser(data.user)
      setTenant(data.tenant)
    } catch (error) {
      setUser(null)
      setTenant(null)
    }
  }

  useEffect(() => {
    refreshUser().finally(() => setLoading(false))
  }, [])

  // Redirect to change password page if user must change password
  useEffect(() => {
    if (!loading && user && mustChangePassword && pathname !== '/change-password') {
      router.push('/change-password')
    }
  }, [loading, user, mustChangePassword, pathname, router])

  const handleSignup = async (data: SignupData) => {
    const response = await signup(data)
    setUser(response.user)
    setTenant(response.tenant)
    router.push('/dashboard')
  }

  const handleLogin = async (data: LoginData) => {
    const response = await login(data)
    setUser(response.user)
    setTenant(response.tenant)
    
    // Redirect based on whether password change is required
    if (response.user.must_change_password) {
      router.push('/change-password')
    } else {
      router.push('/dashboard')
    }
  }

  const handleLogout = () => {
    authLogout()
    setUser(null)
    setTenant(null)
    router.push('/login')
  }

  const handleChangePassword = async (data: ChangePasswordData) => {
    const response = await authChangePassword(data)
    // Update user state after password change
    setUser(response.user)
    if (response.tenant) {
      setTenant(response.tenant)
    }
    // Redirect to dashboard after successful password change
    router.push('/dashboard')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        tenant,
        loading,
        isAdmin,
        mustChangePassword,
        signup: handleSignup,
        login: handleLogin,
        logout: handleLogout,
        refreshUser,
        changePassword: handleChangePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}


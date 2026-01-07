'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'

export default function SettingsPage() {
  const { user, tenant, isAdmin } = useAuth()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and tenant settings
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Profile Card */}
        <div className="bg-card border rounded-xl p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
              {(user?.name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div>
              <h3 className="font-semibold">{user?.name || 'No name set'}</h3>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Role</span>
              <span className="font-medium capitalize">{user?.role}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Organization</span>
              <span className="font-medium">{tenant?.name}</span>
            </div>
          </div>
        </div>

        {/* Team Management Card (Admin only) */}
        {isAdmin && (
          <Link href="/dashboard/settings/team" className="block">
            <div className="bg-card border rounded-xl p-6 hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10 transition-all cursor-pointer h-full">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">Team Members</h3>
                  <p className="text-sm text-muted-foreground">Manage your team</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Add team members, set permissions, and control who can access your chatbots.
              </p>
            </div>
          </Link>
        )}

        {/* Security Card */}
        <div className="bg-card border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold">Security</h3>
              <p className="text-sm text-muted-foreground">Account security</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Manage your password and security preferences.
          </p>
          <Link
            href="/change-password"
            className="text-sm text-purple-500 hover:text-purple-400 font-medium"
          >
            Change password →
          </Link>
        </div>

        {/* API Keys Card (Coming Soon) */}
        <div className="bg-card border rounded-xl p-6 opacity-60">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold">API Keys</h3>
              <p className="text-sm text-muted-foreground">Coming soon</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Manage API keys for programmatic access to your chatbots.
          </p>
        </div>
      </div>
    </div>
  )
}


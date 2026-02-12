'use client'

interface HeaderProps {
  user?: any
  tenant?: any
}

export function Header({ user, tenant }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center justify-end px-6">
        {/* Header content can be added here if needed */}
      </div>
    </header>
  )
}


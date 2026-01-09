'use client'

import React, { useState } from 'react'
import {
  ChevronDown,
  ChevronUp,
  Trash2,
  Globe,
  Loader2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { cn } from '@/lib/utils'

interface CrawledPage {
  id: string
  url: string
  title: string | null
  status: string
}

interface KnowledgeSource {
  id: string
  source_url: string | null
  status: string
  pages_found: number
}

interface CrawlSourcePanelProps {
  source: KnowledgeSource
  pages: CrawledPage[]
  selectedPages: string[]
  onSelectionChange: (ids: string[]) => void
  onSchedule: () => void
  onDeleteSelected: () => void
  isBulkDeleting: boolean
}

export function CrawlSourcePanel({
  source,
  pages,
  selectedPages,
  onSelectionChange,
  onSchedule,
  onDeleteSelected,
  isBulkDeleting
}: CrawlSourcePanelProps) {
  const [isOpen, setIsOpen] = useState(false)

  // Pages belonging to this panel
  const panelPageIds = pages.map(p => p.id)
  
  // Check if all pages in this panel are selected
  const allSelected = panelPageIds.length > 0 && panelPageIds.every(id => selectedPages.includes(id))
  
  // Check if some pages are selected
  const someSelected = panelPageIds.some(id => selectedPages.includes(id))

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      // Add all panel pages to selection (avoiding duplicates)
      const toAdd = panelPageIds.filter(id => !selectedPages.includes(id))
      onSelectionChange([...selectedPages, ...toAdd])
    } else {
      // Remove all panel pages from selection
      onSelectionChange(selectedPages.filter(id => !panelPageIds.includes(id)))
    }
  }

  return (
    <Card className="overflow-hidden border-l-4 border-l-blue-500">
      <CardHeader className="py-3 px-4 bg-muted/20 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-3 overflow-hidden">
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-1 h-6 w-6" 
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
          <div className="font-medium truncate flex items-center gap-2">
            <Globe className="h-4 w-4 text-blue-500" />
            {source.source_url}
          </div>
          <Badge variant={source.status === 'completed' ? 'secondary' : 'default'} className="capitalize">
            {source.status}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {pages.length} Pages
          </Badge>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Button size="sm" variant="outline" onClick={onSchedule} className="h-8 text-xs">
            Schedule Crawl
          </Button>
        </div>
      </CardHeader>
      
      {isOpen && (
        <CardContent className="p-0 border-t animate-in slide-in-from-top-2 duration-200">
          <div className="p-3 border-b bg-muted/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Checkbox 
                checked={allSelected}
                onCheckedChange={handleSelectAll}
                id={`select-all-${source.id}`}
              />
              <label htmlFor={`select-all-${source.id}`} className="text-sm font-medium cursor-pointer select-none">
                Select All
              </label>
            </div>
            {someSelected && (
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={onDeleteSelected}
                disabled={isBulkDeleting}
                className="h-7 text-xs"
              >
                <Trash2 className="h-3.5 w-3.5 mr-1.5" />
                Delete Selected
              </Button>
            )}
          </div>
          
          <div className="max-h-[400px] overflow-y-auto">
            {pages.length > 0 ? (
              <div className="divide-y">
                {pages.map(page => (
                  <div key={page.id} className={cn(
                    "flex items-center justify-between p-3 hover:bg-muted/5 transition-colors",
                    selectedPages.includes(page.id) && "bg-blue-50/50"
                  )}>
                    <div className="flex items-center gap-3 overflow-hidden">
                      <Checkbox 
                        checked={selectedPages.includes(page.id)}
                        onCheckedChange={(checked) => {
                          if (checked) onSelectionChange([...selectedPages, page.id])
                          else onSelectionChange(selectedPages.filter(id => id !== page.id))
                        }}
                      />
                      <div className="overflow-hidden min-w-0">
                        <div className="text-sm truncate font-medium">{page.title || page.url}</div>
                        <div className="text-xs text-muted-foreground truncate">{page.url}</div>
                      </div>
                    </div>
                    <Badge variant="outline" className={cn(
                      "text-[10px] capitalize ml-2",
                      page.status === 'completed' ? "text-green-600 border-green-200 bg-green-50" : "text-amber-600 border-amber-200 bg-amber-50"
                    )}>
                      {page.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground text-sm flex flex-col items-center gap-2">
                <Loader2 className="h-8 w-8 animate-spin opacity-20" />
                <p>Waiting for pages...</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

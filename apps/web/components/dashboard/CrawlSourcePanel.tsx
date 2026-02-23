"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  Trash2,
  Globe,
  AlertCircle,
  Clock,
  Tag,
  StopCircle,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { InlineSpinner, Spinner } from "@/components/ui/loading";

interface CrawledPage {
  id: string;
  url: string;
  title: string | null;
  status: string;
  is_product?: boolean;
}

interface KnowledgeSource {
  id: string;
  source_url: string | null;
  status: string;
  pages_found: number;
  error_message?: string | null;
  updated_at?: string;
}

interface CrawlSourcePanelProps {
  source: KnowledgeSource;
  pages: CrawledPage[];
  selectedPages: string[];
  onSelectionChange: (ids: string[]) => void;
  onSchedule: () => void;
  onDeleteSelected: () => void;
  isBulkDeleting: boolean;
  onStopCrawl?: (sourceId: string) => Promise<void>;
}

export function CrawlSourcePanel({
  source,
  pages,
  selectedPages,
  onSelectionChange,
  onSchedule,
  onDeleteSelected,
  isBulkDeleting,
  onStopCrawl,
}: CrawlSourcePanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [wasStopped, setWasStopped] = useState(false);

  const isCrawling = source.status?.toLowerCase() === "crawling";
  const isActiveCrawl = ["pending", "processing", "crawling"].includes(
    source.status?.toLowerCase(),
  );
  // Only show stop button during active crawling, not processing, and not after being stopped
  const showStopButton = isCrawling && onStopCrawl && !wasStopped;

  // Pages belonging to this panel
  const panelPageIds = pages.map((p) => p.id);

  // Check if all pages in this panel are selected
  const allSelected =
    panelPageIds.length > 0 &&
    panelPageIds.every((id) => selectedPages.includes(id));

  // Check if some pages are selected
  const someSelected = panelPageIds.some((id) => selectedPages.includes(id));

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      // Add all panel pages to selection (avoiding duplicates)
      const toAdd = panelPageIds.filter((id) => !selectedPages.includes(id));
      onSelectionChange([...selectedPages, ...toAdd]);
    } else {
      // Remove all panel pages from selection
      onSelectionChange(
        selectedPages.filter((id) => !panelPageIds.includes(id)),
      );
    }
  };

  // Determine badge variant based on status
  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "secondary";
      case "failed":
        return "destructive";
      case "processing":
      case "crawling":
        return "default";
      default:
        return "outline";
    }
  };

  return (
    <Card
      className={cn(
        "overflow-hidden border-l-4",
        source.status === "failed"
          ? "border-l-red-500"
          : source.status === "completed"
            ? "border-l-emerald-500"
            : "border-l-emerald-500",
      )}
    >
      <CardHeader className="py-3 px-4 bg-muted/20 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-3 overflow-hidden">
          <Button
            variant="ghost"
            size="sm"
            className="p-1 h-6 w-6"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
          <div
            className="font-medium truncate flex items-center gap-2"
            title={source.source_url || ""}
          >
            <Globe
              className={cn(
                "h-4 w-4",
                source.status === "failed"
                  ? "text-red-500"
                  : source.status === "completed"
                    ? "text-green-600"
                    : "text-blue-500",
              )}
            />
            {source.source_url}
          </div>
          <Badge
            variant={getStatusBadgeVariant(source.status)}
            className="capitalize font-normal"
          >
            {source.status === "failed" && (
              <AlertCircle className="h-3 w-3 mr-1" />
            )}
            {isActiveCrawl && <InlineSpinner size="xs" className="mr-1" />}
            {source.status}
          </Badge>
          <Badge variant="outline" className="text-xs font-normal">
            {pages.length} Pages
          </Badge>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {showStopButton && (
            <Button
              size="sm"
              variant="destructive"
              onClick={async () => {
                setIsStopping(true);
                try {
                  await onStopCrawl!(source.id);
                  setWasStopped(true);
                } finally {
                  setIsStopping(false);
                }
              }}
              disabled={isStopping}
              className="h-8 text-xs"
            >
              {isStopping ? (
                <InlineSpinner size="sm" className="mr-1.5" />
              ) : (
                <StopCircle className="h-3.5 w-3.5 mr-1.5" />
              )}
              {isStopping ? "Stopping..." : "Stop Crawl"}
            </Button>
          )}
          {source.updated_at && (
            <div className="hidden md:flex items-center gap-1.5 text-xs text-muted-foreground mr-2">
              <Clock className="h-3 w-3" />
              <span>
                Last synced {new Date(source.updated_at).toLocaleDateString()}
              </span>
            </div>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={onSchedule}
            className="h-8 text-xs"
          >
            Schedule Crawl
          </Button>
        </div>
      </CardHeader>

      {/* Show error message if status is failed */}
      {source.status === "failed" && source.error_message && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100">
          <div className="flex items-start gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <p className="whitespace-pre-line">{source.error_message}</p>
          </div>
        </div>
      )}

      {/* Show warning message (JS-heavy, quota) for completed sources - exclude "stopped" messages (shown as toast) */}
      {source.status === "completed" &&
        source.error_message &&
        !source.error_message.toLowerCase().includes("stopped") && (
          <div className="px-4 py-2 bg-amber-50 border-t border-amber-100">
            <div className="flex items-start gap-2 text-sm text-amber-800">
              <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
              <p className="whitespace-pre-line">{source.error_message}</p>
            </div>
          </div>
        )}

      {/* Show info message during active crawl (JS-heavy detection, sitemap usage) */}
      {isActiveCrawl && source.error_message && (
        <div className="px-4 py-2 bg-blue-50 border-t border-blue-100">
          <div className="flex items-start gap-2 text-sm text-blue-700">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <p className="whitespace-pre-line">{source.error_message}</p>
          </div>
        </div>
      )}

      {isOpen && (
        <CardContent className="p-0 border-t animate-in slide-in-from-top-2 duration-200">
          <div className="p-3 border-b bg-muted/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Checkbox
                checked={allSelected}
                onCheckedChange={handleSelectAll}
                id={`select-all-${source.id}`}
              />
              <label
                htmlFor={`select-all-${source.id}`}
                className="text-sm font-medium cursor-pointer select-none"
              >
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
                {pages.map((page) => (
                  <div
                    key={page.id}
                    className={cn(
                      "flex items-center gap-3 overflow-hidden p-3 hover:bg-muted/5 transition-colors",
                      selectedPages.includes(page.id) && "bg-blue-50/50",
                    )}
                  >
                    <Checkbox
                      checked={selectedPages.includes(page.id)}
                      onCheckedChange={(checked) => {
                        if (checked)
                          onSelectionChange([...selectedPages, page.id]);
                        else
                          onSelectionChange(
                            selectedPages.filter((id) => id !== page.id),
                          );
                      }}
                    />
                    <div className="overflow-hidden min-w-0">
                      <div
                        className="text-sm truncate font-medium flex items-center gap-2"
                        title={page.title || page.url}
                      >
                        <span>{page.title || page.url}</span>
                        {page.is_product && (
                          <Badge
                            variant="outline"
                            className="h-4 px-1 text-[10px] bg-blue-50 text-blue-700 border-blue-200 flex items-center"
                          >
                            <Tag className="h-2.5 w-2.5 mr-0.5" />
                            Product
                          </Badge>
                        )}
                      </div>
                      <div
                        className="text-xs text-muted-foreground truncate"
                        title={page.url}
                      >
                        {page.url}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground text-sm flex flex-col items-center gap-2">
                <Spinner size="lg" className="opacity-20" />
                <p>Waiting for pages...</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

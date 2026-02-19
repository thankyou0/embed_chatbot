"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  Trash2,
  FileQuestion,
  AlertCircle,
  HelpCircle,
  MessageCircle,
  Edit2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { InlineSpinner, Spinner } from "@/components/ui/loading";

interface QAPair {
  id: string;
  question: string;
  answer: string;
  created_at?: string;
}

interface KnowledgeSource {
  id: string;
  source_url: string | null;
  status: string;
  pages_found: number;
  error_message?: string | null;
  updated_at?: string;
  qa_pairs?: QAPair[];
}

interface QABundlePanelProps {
  source: KnowledgeSource;
  qaPairs: QAPair[];
  selectedPairs: string[];
  onSelectionChange: (ids: string[]) => void;
  onDeleteSource: () => void;
  onDeleteSelectedPairs: () => void;
  isDeleting: boolean;
  onEditPair: (qa: QAPair) => void;
  onDeletePair: (id: string) => void;
}

export function QABundlePanel({
  source,
  qaPairs,
  selectedPairs,
  onSelectionChange,
  onDeleteSource,
  onDeleteSelectedPairs,
  isDeleting,
  onEditPair,
  onDeletePair,
}: QABundlePanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  // QA pairs belonging to this panel
  const panelPairIds = qaPairs.map((p) => p.id);

  // Check if all pairs in this panel are selected
  const allSelected =
    panelPairIds.length > 0 &&
    panelPairIds.every((id) => selectedPairs.includes(id));

  // Check if some pairs are selected
  const someSelected = panelPairIds.some((id) => selectedPairs.includes(id));

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      // Add all panel pairs to selection (avoiding duplicates)
      const toAdd = panelPairIds.filter((id) => !selectedPairs.includes(id));
      onSelectionChange([...selectedPairs, ...toAdd]);
    } else {
      // Remove all panel pairs from selection
      onSelectionChange(
        selectedPairs.filter((id) => !panelPairIds.includes(id)),
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
        "overflow-hidden border-l-4 mb-4",
        source.status === "failed"
          ? "border-l-red-500"
          : source.status === "completed"
            ? "border-l-emerald-500"
            : "border-l-indigo-500",
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
          <div className="font-medium truncate flex items-center gap-2">
            <FileQuestion
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
            className="capitalize"
          >
            {(source.status === "processing" || source.status === "crawling") && (
              <InlineSpinner size="xs" className="mr-1" />
            )}
            {source.status === "failed" && (
              <AlertCircle className="h-3 w-3 mr-1" />
            )}
            {source.status}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {qaPairs.length} Pairs
          </Badge>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {/* Removed all buttons from header as requested */}
        </div>
      </CardHeader>

      {/* Show error message if status is failed */}
      {source.status === "failed" && source.error_message && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100">
          <div className="flex items-start gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <p className="line-clamp-2">{source.error_message}</p>
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
                onClick={onDeleteSelectedPairs}
                disabled={isDeleting}
                className="h-7 text-xs"
              >
                <Trash2 className="h-3.5 w-3.5 mr-1.5" />
                Delete Selected
              </Button>
            )}
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {qaPairs.length > 0 ? (
              <div className="divide-y">
                {qaPairs.map((qa) => (
                  <div
                    key={qa.id}
                    className={cn(
                      "flex items-start gap-3 p-3 hover:bg-muted/5 transition-colors",
                      selectedPairs.includes(qa.id) && "bg-blue-50/50",
                    )}
                  >
                    <Checkbox
                      className="mt-1"
                      checked={selectedPairs.includes(qa.id)}
                      onCheckedChange={(checked) => {
                        if (checked)
                          onSelectionChange([...selectedPairs, qa.id]);
                        else
                          onSelectionChange(
                            selectedPairs.filter((id) => id !== qa.id),
                          );
                      }}
                    />
                    <div className="grid gap-1.5 flex-1 min-w-0">
                        <div className="flex items-start gap-2">
                            <HelpCircle className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                            <p className="text-sm font-medium leading-tight">{qa.question}</p>
                        </div>
                        <div className="flex items-start gap-2">
                            <MessageCircle className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
                            <p className="text-sm text-muted-foreground leading-relaxed">{qa.answer}</p>
                        </div>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-primary"
                        onClick={() => onEditPair(qa)}
                        title="Edit QA pair"
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => onDeletePair(qa.id)}
                        title="Delete QA pair"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground text-sm flex flex-col items-center gap-2">
                <Spinner size="lg" className="opacity-20" />
                <p>Waiting for QA pairs...</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

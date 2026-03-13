"use client";

import React, { useState } from "react";
import { toast } from "@/lib/notify-toast";
import {
  Plus,
  Globe,
  Upload,
  FileText,
  Trash2,
  AlertCircle,
  HelpCircle,
  X as CloseIcon,
  Search,
  Eye,
  Edit2,
  MessageSquare,
  RefreshCw,
  X,
} from "lucide-react";
import {
  PageLoader,
  SectionLoader,
  ButtonSpinner,
  InlineSpinner,
} from "@/components/ui/loading";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { CrawlScheduleModal } from "@/components/dashboard/CrawlScheduleModal";
import { CrawlSourcePanel } from "@/components/dashboard/CrawlSourcePanel";
import { QABundlePanel } from "@/components/dashboard/QABundlePanel";

import type { KnowledgeSource, QAPair, CrawlNotification } from "../types";

interface KnowledgeTabProps {
  chatbotId: string;
  canEdit: boolean;
  knowledgeSources: KnowledgeSource[];
  isLoadingKnowledge: boolean;
  // Add knowledge panel
  isAddKnowledgeOpen: boolean;
  setIsAddKnowledgeOpen: (open: boolean) => void;
  knowledgeType: "url" | "file" | "qa";
  setKnowledgeType: (type: "url" | "file" | "qa") => void;
  // URL crawl
  newUrl: string;
  setNewUrl: (url: string) => void;
  isCrawling: boolean;
  handleCrawl: (e: React.FormEvent) => void;
  // File upload
  uploadFiles: FileList | null;
  setUploadFiles: (files: FileList | null) => void;
  isUploading: boolean;
  handleFileUpload: (e: React.FormEvent) => void;
  // QA
  newQA: { question: string; answer: string };
  setNewQA: (qa: { question: string; answer: string }) => void;
  editingQA: QAPair | null;
  setEditingQA: (qa: QAPair | null) => void;
  handleQASubmit: (e: React.FormEvent) => void;
  qaXlsx: File | null;
  setQaXlsx: (file: File | null) => void;
  handleQAXlsxUpload: (e: React.FormEvent) => void;
  handleDeleteQA: (qaId: string) => void;
  // Source management
  handleDeleteSource: (sourceId: string, customMessage?: string, silent?: boolean) => void;
  handleStopCrawl: (sourceId: string) => void;
  handlePreviewFile: (file: any) => void;
  // Selection
  selectedPages: string[];
  setSelectedPages: (pages: string[]) => void;
  selectedFiles: string[];
  setSelectedFiles: (files: string[]) => void;
  selectedQAs: string[];
  setSelectedQAs: (qas: string[]) => void;
  isBulkDeleting: boolean;
  handleBulkDelete: (type: "pages" | "files" | "qa") => void;
  deletingFileId: string | null;
  loadingPreviewFileId: string | null;
  // Sub-tabs
  knowledgeTab: string;
  setKnowledgeTab: (tab: string) => void;
  // Computed
  crawlSources: KnowledgeSource[];
  fileSources: KnowledgeSource[];
  qaPairs: QAPair[];
  allCrawledPages: Array<any>;
  crawlSourcesWithPages: KnowledgeSource[];
  // Notifications
  crawlNotifications: CrawlNotification[];
  dismissNotification: (id: string) => void;
  dismissAllNotifications: () => void;
  // Crawl schedule
  isCrawlScheduleOpen: boolean;
  setIsCrawlScheduleOpen: (open: boolean) => void;
  selectedCrawlSource: any | null;
  setSelectedCrawlSource: (source: any | null) => void;
  // Callbacks for crawl schedule on-sync
  onSyncTriggered: () => void;
}

export function KnowledgeTab({
  chatbotId,
  canEdit,
  knowledgeSources,
  isLoadingKnowledge,
  isAddKnowledgeOpen,
  setIsAddKnowledgeOpen,
  knowledgeType,
  setKnowledgeType,
  newUrl,
  setNewUrl,
  isCrawling,
  handleCrawl,
  uploadFiles,
  setUploadFiles,
  isUploading,
  handleFileUpload,
  newQA,
  setNewQA,
  editingQA,
  setEditingQA,
  handleQASubmit,
  qaXlsx,
  setQaXlsx,
  handleQAXlsxUpload,
  handleDeleteQA,
  handleDeleteSource,
  handleStopCrawl,
  handlePreviewFile,
  selectedPages,
  setSelectedPages,
  selectedFiles,
  setSelectedFiles,
  selectedQAs,
  setSelectedQAs,
  isBulkDeleting,
  handleBulkDelete,
  deletingFileId,
  loadingPreviewFileId,
  knowledgeTab,
  setKnowledgeTab,
  crawlSources,
  fileSources,
  qaPairs,
  allCrawledPages,
  crawlSourcesWithPages,
  crawlNotifications,
  dismissNotification,
  dismissAllNotifications,
  isCrawlScheduleOpen,
  setIsCrawlScheduleOpen,
  selectedCrawlSource,
  setSelectedCrawlSource,
  onSyncTriggered,
}: KnowledgeTabProps) {
  const [expandedNotifs, setExpandedNotifs] = useState<Set<string>>(new Set());

  const toggleNotifExpand = (id: string) => {
    setExpandedNotifs((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Add Knowledge</CardTitle>
          <CardDescription>
            Manage the data sources your chatbot learns from
          </CardDescription>
        </div>
        {canEdit && (
          <Button onClick={() => setIsAddKnowledgeOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Source
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {isAddKnowledgeOpen && (
          <div className="mb-6 p-4 border rounded-lg bg-muted/30">
            <div className="flex items-center justify-between mb-4">
              <div className="flex bg-muted p-1 rounded-md">
                <Button
                  variant={knowledgeType === "url" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setKnowledgeType("url")}
                  className="text-xs"
                >
                  <Globe className="h-3 w-3 mr-1" /> Website
                </Button>
                <Button
                  variant={knowledgeType === "file" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setKnowledgeType("file")}
                  className="text-xs"
                >
                  <Upload className="h-3 w-3 mr-1" /> File
                </Button>
                <Button
                  variant={knowledgeType === "qa" ? "secondary" : "ghost"}
                  size="sm"
                  onClick={() => setKnowledgeType("qa")}
                  className="text-xs"
                >
                  <HelpCircle className="h-3 w-3 mr-1" /> Q&A
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsAddKnowledgeOpen(false)}
                type="button"
              >
                <CloseIcon className="h-4 w-4" />
              </Button>
            </div>

            {knowledgeType === "url" ? (
              <form onSubmit={handleCrawl} className="space-y-4">
                <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>💡 Tip:</strong> Add your website URL that
                    contains information you want your bot to learn from.
                    The bot will crawl and index the content from the
                    pages it finds.
                  </p>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1 space-y-1">
                    <Label htmlFor="url">Website URL</Label>
                    <Input
                      id="url"
                      placeholder="https://example.com/docs"
                      value={newUrl}
                      onChange={(e) => setNewUrl(e.target.value)}
                      required
                    />
                  </div>
                  <div className="self-end">
                    <Button
                      type="submit"
                      disabled={isCrawling || !newUrl.trim()}
                    >
                      {isCrawling ? (
                        <>
                          <ButtonSpinner />
                          Starting...
                        </>
                      ) : (
                        <>
                          <Search className="h-4 w-4 mr-2" />
                          Crawl URL
                        </>
                      )}
                    </Button>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  We&apos;ll crawl the website and process its content for
                  your chatbot.
                </p>
              </form>
            ) : knowledgeType === "file" ? (
              <form onSubmit={handleFileUpload} className="space-y-4">
                <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>💡 Tip:</strong> Upload policy documents,
                    product guides, presentations (PPT), PDFs, or any
                    files related to your product, firm, or website that
                    you want the bot to reference.
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="file">
                    Upload Files (PDF, DOCX, TXT, MD)
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="file"
                      type="file"
                      multiple
                      accept=".pdf,.docx,.txt,.md"
                      onChange={(e) => setUploadFiles(e.target.files)}
                      className="flex-1"
                      required
                    />
                    <Button
                      type="submit"
                      disabled={
                        isUploading ||
                        !uploadFiles ||
                        uploadFiles.length === 0
                      }
                    >
                      {isUploading ? (
                        <>
                          <ButtonSpinner />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="h-4 w-4 mr-2" />
                          Upload
                        </>
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" /> Max file size 10MB
                  </p>
                </div>
              </form>
            ) : (
              <div className="space-y-6">
                <div className="mb-3 p-3 bg-teal-50 border border-teal-200 rounded-lg">
                  <p className="text-sm text-teal-800">
                    <strong>💡 Tip:</strong> Add frequently asked
                    questions (FAQs) from your site or any specific
                    questions you want your bot to answer consistently.
                    This ensures accurate responses for common queries.
                  </p>
                </div>
                <form onSubmit={handleQASubmit} className="space-y-4">
                  <div className="grid gap-4">
                    <div className="space-y-1">
                      <Label htmlFor="q">Question</Label>
                      <Input
                        id="q"
                        value={newQA.question}
                        onChange={(e) =>
                          setNewQA({ ...newQA, question: e.target.value })
                        }
                        placeholder="e.g. What are your opening hours?"
                        required
                      />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="a">Answer</Label>
                      <Input
                        id="a"
                        value={newQA.answer}
                        onChange={(e) =>
                          setNewQA({ ...newQA, answer: e.target.value })
                        }
                        placeholder="e.g. We are open from 9 AM to 6 PM."
                        required
                      />
                    </div>
                  </div>
                  <Button type="submit">
                    {editingQA ? "Update QA Pair" : "Add QA Pair"}
                  </Button>
                  {editingQA && (
                    <Button
                      variant="ghost"
                      className="ml-2"
                      onClick={() => {
                        setEditingQA(null);
                        setNewQA({ question: "", answer: "" });
                      }}
                    >
                      Cancel
                    </Button>
                  )}
                </form>

                <div className="pt-4 border-t">
                  <Label className="text-xs font-semibold uppercase text-muted-foreground">
                    Or Bulk Upload (XLSX)
                  </Label>
                  <div className="mt-2 mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-sm text-amber-800 mb-2">
                      <strong>📊 Excel Format:</strong> Your XLSX file
                      should contain two columns:
                    </p>
                    <ul className="text-xs text-amber-700 ml-4 space-y-1 list-disc">
                      <li>
                        <strong>Column A:</strong> &quot;question&quot; -
                        The question text
                      </li>
                      <li>
                        <strong>Column B:</strong> &quot;answer&quot; -
                        The corresponding answer
                      </li>
                      <li>
                        First row should be the header row with column
                        names
                      </li>
                      <li>Each subsequent row represents one Q&A pair</li>
                    </ul>
                  </div>
                  <form
                    onSubmit={handleQAXlsxUpload}
                    className="mt-2 flex gap-2"
                  >
                    <Input
                      type="file"
                      accept=".xlsx,.xls"
                      onChange={(e) =>
                        setQaXlsx(e.target.files?.[0] || null)
                      }
                      className="flex-1"
                    />
                    <Button
                      type="submit"
                      variant="outline"
                      disabled={!qaXlsx}
                    >
                      <Upload className="h-4 w-4 mr-2" /> Upload XLSX
                    </Button>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        <Tabs
          value={knowledgeTab}
          onValueChange={setKnowledgeTab}
          className="w-full"
        >
          <TabsList className="mb-4">
            <TabsTrigger value="crawl" className="gap-2">
              <Globe className="h-4 w-4" /> Crawl{" "}
              {allCrawledPages.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1">
                  {allCrawledPages.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="files" className="gap-2">
              <FileText className="h-4 w-4" /> Files{" "}
              {fileSources.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1">
                  {fileSources.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="qa" className="gap-2">
              <MessageSquare className="h-4 w-4" /> Q&A{" "}
              {qaPairs.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1">
                  {qaPairs.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {isLoadingKnowledge ? (
            <SectionLoader minHeight="min-h-[200px]" />
          ) : (
            <>
              {/* Crawl Tab Content */}
              <TabsContent value="crawl" className="space-y-4">
                {isCrawlScheduleOpen && selectedCrawlSource && (
                  <CrawlScheduleModal
                    knowledgeSourceId={selectedCrawlSource.id}
                    sourceUrl={selectedCrawlSource.source_url || ""}
                    pagesCount={selectedCrawlSource.pages_found || 0}
                    lastSynced={selectedCrawlSource.updated_at ?? null}
                    onClose={() => {
                      setIsCrawlScheduleOpen(false);
                      setSelectedCrawlSource(null);
                    }}
                    onSync={async () => {
                      toast.info(
                        "Crawl started. This may take a few minutes...",
                      );
                      onSyncTriggered();
                    }}
                  />
                )}
                {crawlSourcesWithPages.length > 0 ? (
                  <div className="space-y-4">
                    {/* Persistent crawl notifications */}
                    {crawlNotifications.length > 0 && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-muted-foreground">
                            Recent Notifications
                          </span>
                          {crawlNotifications.length > 1 && (
                            <button
                              onClick={dismissAllNotifications}
                              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                            >
                              Dismiss all
                            </button>
                          )}
                        </div>
                        {crawlNotifications.map((notif) => {
                          const isExpanded = expandedNotifs.has(notif.id);
                          return (
                          <div
                            key={notif.id}
                            className={cn(
                              "px-3 py-2 rounded-lg border text-sm flex items-start gap-2 group transition-colors",
                              notif.severity === "error"
                                ? "bg-red-50 border-red-200 text-red-800"
                                : notif.severity === "warning"
                                  ? "bg-amber-50 border-amber-200 text-amber-800"
                                  : "bg-blue-50 border-blue-200 text-blue-800",
                            )}
                          >
                            {notif.severity === "error" ? (
                              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                            ) : notif.severity === "warning" ? (
                              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
                            ) : (
                              <RefreshCw className="h-4 w-4 mt-0.5 shrink-0" />
                            )}
                            <p
                              className={cn(
                                "flex-1 cursor-pointer select-text",
                                !isExpanded && "line-clamp-2",
                              )}
                              onClick={() => toggleNotifExpand(notif.id)}
                              title={isExpanded ? undefined : notif.message}
                            >
                              {notif.message}
                            </p>
                            <button
                              onClick={() => dismissNotification(notif.id)}
                              className="p-0.5 hover:bg-black/10 rounded shrink-0 opacity-60 group-hover:opacity-100 transition-opacity"
                            >
                              <X className="h-3.5 w-3.5" />
                            </button>
                          </div>
                          );
                        })}
                      </div>
                    )}
                    {Array.from(
                      new Map(
                        crawlSourcesWithPages.map((ks) => [
                          ks.source_url,
                          ks,
                        ]),
                      ).values(),
                    ).map((ks) => (
                      <CrawlSourcePanel
                        key={ks.id}
                        source={ks}
                        pages={allCrawledPages.filter(
                          (p) => p.source_url === ks.source_url,
                        )}
                        selectedPages={selectedPages}
                        onSelectionChange={setSelectedPages}
                        onSchedule={() => {
                          setSelectedCrawlSource(ks);
                          setIsCrawlScheduleOpen(true);
                        }}
                        onDeleteSelected={() => handleBulkDelete("pages")}
                        isBulkDeleting={isBulkDeleting}
                        onStopCrawl={handleStopCrawl}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 border-2 border-dashed rounded-xl">
                    <Globe className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                    <p className="text-gray-500">
                      No crawled pages found
                    </p>
                    <Button
                      variant="link"
                      onClick={() => {
                        setKnowledgeType("url");
                        setIsAddKnowledgeOpen(true);
                      }}
                    >
                      Add website URL
                    </Button>
                  </div>
                )}
              </TabsContent>

              {/* Files Tab Content */}
              <TabsContent value="files" className="space-y-4">
                {fileSources.length > 0 && (
                  <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                    <div className="flex items-center gap-2">
                      <Checkbox
                        checked={
                          selectedFiles.length === fileSources.length &&
                          fileSources.length > 0
                        }
                        onCheckedChange={(checked: boolean) => {
                          if (checked)
                            setSelectedFiles(
                              fileSources.map((s) => s.id),
                            );
                          else setSelectedFiles([]);
                        }}
                      />
                      <span className="text-sm font-medium">
                        Select All
                      </span>
                    </div>
                    {selectedFiles.length > 0 && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleBulkDelete("files")}
                        disabled={isBulkDeleting}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete {selectedFiles.length}
                      </Button>
                    )}
                  </div>
                )}

                {fileSources.length > 0 ? (
                  <div className="space-y-2">
                    {fileSources.map((source) => (
                      <div
                        key={source.id}
                        className={`flex items-center justify-between p-3 border rounded-lg hover:bg-muted/5 transition-colors ${
                          selectedFiles.includes(source.id)
                            ? "bg-blue-50/30 border-blue-200"
                            : ""
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Checkbox
                            checked={selectedFiles.includes(source.id)}
                            onCheckedChange={(checked: boolean) => {
                              if (checked)
                                setSelectedFiles([
                                  ...selectedFiles,
                                  source.id,
                                ]);
                              else
                                setSelectedFiles(
                                  selectedFiles.filter(
                                    (id) => id !== source.id,
                                  ),
                                );
                            }}
                          />
                          <div className="h-8 w-8 rounded bg-blue-50 flex items-center justify-center text-blue-600">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div>
                            <div className="font-medium text-sm">
                              {source.files && source.files.length > 0
                                ? source.files[0].filename
                                : "Uploaded File"}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {source.files && source.files.length > 0
                                ? `${(
                                    source.files[0].file_size / 1024
                                  ).toFixed(1)} KB`
                                : ""}{" "}
                              •{" "}
                              {new Date(
                                source.created_at,
                              ).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              source.status === "completed"
                                ? "success"
                                : "secondary"
                            }
                            className="text-[10px] px-1 h-4"
                          >
                            {source.status}
                          </Badge>
                          {source.status === "completed" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 px-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                              onClick={() => handlePreviewFile(source)}
                              disabled={loadingPreviewFileId !== null}
                              title="Preview file content"
                            >
                              {loadingPreviewFileId ===
                              source.files?.[0]?.id ? (
                                <InlineSpinner size="sm" />
                              ) : (
                                <>
                                  <Eye className="h-4 w-4 mr-1" />
                                  <span className="text-xs">Show</span>
                                </>
                              )}
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteSource(source.id)}
                            disabled={deletingFileId === source.id}
                            title="Delete file"
                          >
                            {deletingFileId === source.id ? (
                              <InlineSpinner size="sm" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 border-2 border-dashed rounded-xl">
                    <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                    <p className="text-muted-foreground">
                      No files uploaded yet
                    </p>
                    <Button
                      variant="link"
                      onClick={() => {
                        setKnowledgeType("file");
                        setIsAddKnowledgeOpen(true);
                      }}
                    >
                      Upload your first file
                    </Button>
                  </div>
                )}
              </TabsContent>

              {/* Q&A Tab Content */}
              <TabsContent value="qa" className="space-y-4">
                {(() => {
                  const qaSources = knowledgeSources.filter(
                    (s) =>
                      s.source_type === "qa_pair" &&
                      s.source_url !== "manual" &&
                      s.files?.length === 0,
                  );

                  const bundleIds = qaSources.map((s) => s.id);
                  const standaloneQAs = qaPairs.filter(
                    (qa) =>
                      !knowledgeSources.some(
                        (ks) =>
                          ks.id === (qa as any).knowledge_source_id &&
                          bundleIds.includes(ks.id),
                      ),
                  );

                  const manualSource = knowledgeSources.find(
                    (s) =>
                      s.source_type === "qa_pair" &&
                      s.source_url === "manual",
                  );

                  return (
                    <>
                      {/* Render Bundles */}
                      {qaSources.map((source) => {
                        const sourcePairs = qaPairs
                          .filter(
                            (qa: any) =>
                              qa.knowledge_source_id === source.id,
                          )
                          .sort((a, b) => {
                            const timeA = new Date(
                              a.created_at || 0,
                            ).getTime();
                            const timeB = new Date(
                              b.created_at || 0,
                            ).getTime();
                            if (timeA !== timeB) return timeA - timeB;
                            return a.id.localeCompare(b.id);
                          });

                        return (
                          <QABundlePanel
                            key={source.id}
                            source={source as any}
                            qaPairs={sourcePairs}
                            selectedPairs={selectedQAs}
                            onSelectionChange={setSelectedQAs}
                            onDeleteSource={() =>
                              handleDeleteSource(
                                source.id,
                                `Are you sure you want to delete this bundle? It contains ${sourcePairs.length} Q&A pairs. Bundle: ${source.source_url}`,
                              )
                            }
                            onDeleteSelectedPairs={() =>
                              handleBulkDelete("qa")
                            }
                            isDeleting={isBulkDeleting}
                            onEditPair={(qa) => {
                              setEditingQA(qa as any);
                              setNewQA({
                                question: qa.question,
                                answer: qa.answer,
                              });
                              setKnowledgeType("qa");
                              setIsAddKnowledgeOpen(true);
                              window.scrollTo({
                                top: 0,
                                behavior: "smooth",
                              });
                            }}
                            onDeletePair={handleDeleteQA}
                          />
                        );
                      })}

                      <div className="my-4 border-t" />

                      <div className="space-y-4">
                        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                          Manual Q&A Pairs
                        </h3>

                        {(() => {
                          const standalone = qaPairs
                            .filter((qa: any) => {
                              return !bundleIds.includes(
                                qa.knowledge_source_id,
                              );
                            })
                            .sort((a, b) => {
                              const timeA = new Date(
                                a.created_at || 0,
                              ).getTime();
                              const timeB = new Date(
                                b.created_at || 0,
                              ).getTime();
                              if (timeA !== timeB) return timeA - timeB;
                              return a.id.localeCompare(b.id);
                            });

                          if (
                            standalone.length === 0 &&
                            qaSources.length === 0
                          ) {
                            return (
                              <div className="text-center py-12 border-2 border-dashed rounded-xl">
                                <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground/40 mb-3" />
                                <p className="text-muted-foreground">
                                  No Q&A pairs added
                                </p>
                                <Button
                                  variant="link"
                                  onClick={() => {
                                    setKnowledgeType("qa");
                                    setIsAddKnowledgeOpen(true);
                                  }}
                                >
                                  Add Q&A manually
                                </Button>
                              </div>
                            );
                          }

                          if (standalone.length === 0)
                            return (
                              <p className="text-sm text-muted-foreground italic">
                                No manual Q&A pairs.
                              </p>
                            );

                          return (
                            <>
                              {standalone.length > 0 && (
                                <div className="flex items-center justify-between bg-muted/20 p-2 rounded-md mb-2">
                                  <div className="flex items-center gap-2">
                                    <Checkbox
                                      checked={
                                        standalone.length > 0 &&
                                        standalone.every((q) =>
                                          selectedQAs.includes(q.id),
                                        )
                                      }
                                      onCheckedChange={(
                                        checked: boolean,
                                      ) => {
                                        if (checked) {
                                          const newSelected = [
                                            ...selectedQAs,
                                            ...standalone
                                              .map((q) => q.id)
                                              .filter(
                                                (id) =>
                                                  !selectedQAs.includes(
                                                    id,
                                                  ),
                                              ),
                                          ];
                                          setSelectedQAs(newSelected);
                                        } else {
                                          const standaloneIds =
                                            standalone.map((q) => q.id);
                                          setSelectedQAs(
                                            selectedQAs.filter(
                                              (id) =>
                                                !standaloneIds.includes(
                                                  id,
                                                ),
                                            ),
                                          );
                                        }
                                      }}
                                    />
                                    <span className="text-sm font-medium">
                                      Select All ({standalone.length})
                                    </span>
                                  </div>
                                  {selectedQAs.filter((id) =>
                                    standalone.find((q) => q.id === id),
                                  ).length > 0 && (
                                    <Button
                                      variant="destructive"
                                      size="sm"
                                      onClick={() =>
                                        handleBulkDelete("qa")
                                      }
                                      disabled={isBulkDeleting}
                                    >
                                      <Trash2 className="h-4 w-4 mr-2" />
                                      Delete Selected
                                    </Button>
                                  )}
                                </div>
                              )}

                              <div className="space-y-3">
                                {standalone.map((qa) => (
                                  <div
                                    key={qa.id}
                                    className={`p-4 border rounded-lg bg-card shadow-sm hover:shadow-md transition-all ${
                                      selectedQAs.includes(qa.id)
                                        ? "bg-blue-50/30 border-blue-200"
                                        : ""
                                    }`}
                                  >
                                    <div className="flex justify-between items-start gap-4">
                                      <div className="flex items-start gap-3 flex-1">
                                        <Checkbox
                                          className="mt-1"
                                          checked={selectedQAs.includes(
                                            qa.id,
                                          )}
                                          onCheckedChange={(
                                            checked: boolean,
                                          ) => {
                                            if (checked)
                                              setSelectedQAs([
                                                ...selectedQAs,
                                                qa.id,
                                              ]);
                                            else
                                              setSelectedQAs(
                                                selectedQAs.filter(
                                                  (id) => id !== qa.id,
                                                ),
                                              );
                                          }}
                                        />
                                        <div className="flex-1 min-w-0">
                                          <div className="font-semibold text-sm mb-1">
                                            Q: {qa.question}
                                          </div>
                                          <div className="text-sm text-muted-foreground bg-muted/30 p-2 rounded border-l-2 border-blue-500 line-clamp-2">
                                            A: {qa.answer}
                                          </div>
                                        </div>
                                      </div>
                                      <div className="flex gap-1 shrink-0">
                                        <Button
                                          variant="ghost"
                                          size="icon"
                                          className="h-8 w-8"
                                          onClick={() => {
                                            setEditingQA(qa);
                                            setNewQA({
                                              question: qa.question,
                                              answer: qa.answer,
                                            });
                                            setKnowledgeType("qa");
                                            setIsAddKnowledgeOpen(true);
                                            window.scrollTo({
                                              top: 0,
                                              behavior: "smooth",
                                            });
                                          }}
                                          title="Edit QA pair"
                                        >
                                          <Edit2 className="h-4 w-4" />
                                        </Button>
                                        <Button
                                          variant="ghost"
                                          size="icon"
                                          className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                                          onClick={() =>
                                            handleDeleteQA(qa.id)
                                          }
                                          title="Delete QA pair"
                                        >
                                          <Trash2 className="h-4 w-4" />
                                        </Button>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </>
                          );
                        })()}
                      </div>
                    </>
                  );
                })()}
              </TabsContent>
            </>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}

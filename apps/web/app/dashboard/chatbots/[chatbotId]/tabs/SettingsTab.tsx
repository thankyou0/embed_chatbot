"use client";

import React from "react";
import {
  Settings,
  Trash2,
  AlertCircle,
  CheckCircle2,
  Save,
} from "lucide-react";
import { ButtonSpinner } from "@/components/ui/loading";
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChatbotTeamSettings } from "@/components/dashboard/ChatbotTeamSettings";
import type { ChatbotDetail } from "../types";

interface SettingsTabProps {
  chatbot: ChatbotDetail;
  chatbotId: string;
  canEdit: boolean;
  settingsSubTab: string;
  setSettingsSubTab: (tab: string) => void;
  isSavingSettings: boolean;
  settingsSuccess: string | null;
  settingsError: string | null;
  handleSettingsSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  handleDeleteChatbot: () => void;
}

export function SettingsTab({
  chatbot,
  chatbotId,
  canEdit,
  settingsSubTab,
  setSettingsSubTab,
  isSavingSettings,
  settingsSuccess,
  settingsError,
  handleSettingsSubmit,
  handleDeleteChatbot,
}: SettingsTabProps) {
  return (
    <div className="space-y-6">
      <Tabs
        value={settingsSubTab}
        onValueChange={setSettingsSubTab}
        className="w-full"
      >
        <TabsList className="w-full justify-start border-b rounded-none h-auto p-0 bg-transparent mb-6">
          <TabsTrigger
            value="general"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2"
          >
            General
          </TabsTrigger>
          <TabsTrigger
            value="team"
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-2"
          >
            Team
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          {/* General Information */}
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center flex-shrink-0">
                  <Settings className="h-5 w-5 text-white" />
                </div>
                <div>
                  <CardTitle>General Information</CardTitle>
                  <CardDescription>
                    Manage your chatbot&apos;s identity and operational status
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSettingsSubmit} className="space-y-6">
                {settingsError && (
                  <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-md text-sm flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    {settingsError}
                  </div>
                )}
                {settingsSuccess && (
                  <div className="p-3 bg-green-50 border border-green-200 text-green-600 rounded-md text-sm flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
                    {settingsSuccess}
                  </div>
                )}

                {/* Name */}
                <div className="space-y-2">
                  <Label htmlFor="chatbot-name" className="text-sm font-medium">
                    Chatbot Name
                  </Label>
                  <Input
                    id="chatbot-name"
                    name="name"
                    defaultValue={chatbot.name}
                    placeholder="My Awesome Chatbot"
                    required
                    disabled={!canEdit}
                    className="max-w-md"
                  />
                  <p className="text-xs text-muted-foreground">
                    Internal name used to identify this chatbot across your
                    dashboard.
                  </p>
                </div>

                {/* Details (read-only) */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 bg-muted/30 rounded-lg border">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Chatbot ID
                    </p>
                    <p
                      className="text-sm font-mono mt-1 truncate"
                      title={chatbot.id}
                    >
                      {chatbot.id}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Created
                    </p>
                    <p className="text-sm mt-1">
                      {new Date(chatbot.created_at).toLocaleDateString(
                        "en-US",
                        { year: "numeric", month: "short", day: "numeric" },
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Your Role
                    </p>
                    <Badge variant="outline" className="mt-1 capitalize">
                      {chatbot.permission_level}
                    </Badge>
                  </div>
                </div>

                {/* Status */}
                <div className="space-y-3 pt-2 border-t">
                  <Label className="text-sm font-medium">Chatbot Status</Label>
                  <p className="text-xs text-muted-foreground -mt-2">
                    Control whether your chatbot is live and responding to users.
                  </p>
                  <RadioGroup
                    name="status"
                    defaultValue={
                      chatbot.status === "draft" ? "paused" : chatbot.status
                    }
                    className="grid gap-4 sm:grid-cols-2 max-w-lg"
                    disabled={!canEdit}
                  >
                    <div>
                      <RadioGroupItem
                        value="active"
                        id="status-active"
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor="status-active"
                        className="flex items-center gap-3 rounded-lg border-2 border-muted bg-popover p-4 hover:bg-accent/50 hover:text-accent-foreground peer-data-[state=checked]:border-emerald-500 peer-data-[state=checked]:bg-emerald-50 [&:has([data-state=checked])]:border-emerald-500 [&:has([data-state=checked])]:bg-emerald-50 cursor-pointer transition-all"
                      >
                        <div className="h-3 w-3 rounded-full bg-emerald-500 ring-4 ring-emerald-500/20" />
                        <div>
                          <span className="text-sm font-semibold block">
                            Active
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Live and responding to users
                          </span>
                        </div>
                      </Label>
                    </div>
                    <div>
                      <RadioGroupItem
                        value="paused"
                        id="status-paused"
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor="status-paused"
                        className="flex items-center gap-3 rounded-lg border-2 border-muted bg-popover p-4 hover:bg-accent/50 hover:text-accent-foreground peer-data-[state=checked]:border-amber-500 peer-data-[state=checked]:bg-amber-50 [&:has([data-state=checked])]:border-amber-500 [&:has([data-state=checked])]:bg-amber-50 cursor-pointer transition-all"
                      >
                        <div className="h-3 w-3 rounded-full bg-amber-500 ring-4 ring-amber-500/20" />
                        <div>
                          <span className="text-sm font-semibold block">
                            Paused
                          </span>
                          <span className="text-xs text-muted-foreground">
                            Temporarily offline
                          </span>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>
                  {chatbot.status === "draft" && (
                    <div className="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-md">
                      <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0" />
                      <p className="text-sm text-amber-700">
                        This chatbot is in Draft mode. Set it to Active to make
                        it live.
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex justify-end pt-4 border-t">
                  <Button
                    type="submit"
                    disabled={isSavingSettings || !canEdit}
                    className="min-w-[140px]"
                  >
                    {isSavingSettings ? (
                      <>
                        <ButtonSpinner />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Settings
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          {["owner", "admin"].includes(chatbot.permission_level) && (
            <Card className="border-red-200/50">
              <CardHeader className="pb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-red-50 border border-red-200 flex items-center justify-center flex-shrink-0">
                    <Trash2 className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <CardTitle className="text-red-700">Danger Zone</CardTitle>
                    <CardDescription>
                      This action is irreversible. All data including knowledge
                      base, conversations, and analytics will be permanently
                      deleted.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <Button
                  variant="destructive"
                  className="bg-red-600 hover:bg-red-700"
                  onClick={handleDeleteChatbot}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Chatbot
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent
          value="team"
          className="space-y-6"
          forceMount
          style={{
            display: settingsSubTab === "team" ? undefined : "none",
          }}
        >
          <ChatbotTeamSettings chatbotId={chatbotId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import { toast } from "@/lib/notify-toast";
import { useAuth } from "@/contexts/AuthContext";
import { getAccessToken } from "@/lib/auth";
import { ErrorMessage } from "@/components/ui/error-message";
import { apiRequestWithAuth } from "@/lib/api";
import { Plus, Trash2, X, AlertCircle } from "lucide-react";
import { SectionLoader, ButtonSpinner } from "@/components/ui/loading";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Types
interface Permission {
  id: number;
  user_id: number;
  chatbot_id: string;
  permission_level: "owner" | "admin" | "editor" | "viewer" | "custom";
  can_manage_knowledge: boolean;
  can_manage_appearance: boolean;
  can_resolve_queries: boolean;
  can_view_analytics_billing: boolean;
  granted_by: number;
  user_email: string;
  user_username: string;
  user_name: string | null;
}

interface OrganizationMember {
  id: number;
  email: string;
  username: string;
  name: string | null;
  role: "admin" | "user";
  is_org_owner: boolean;
}

const PRESETS = {
  viewer: {
    label: "Viewer",
    description: "Can only view chatbot and read conversations",
    flags: {
      can_manage_knowledge: false,
      can_manage_appearance: false,
      can_resolve_queries: false,
      can_view_analytics_billing: true,
    },
  },
  editor: {
    label: "Editor",
    description: "Can edit content and appearance",
    flags: {
      can_manage_knowledge: true,
      can_manage_appearance: true,
      can_resolve_queries: true,
      can_view_analytics_billing: true,
    },
  },
  admin: {
    label: "Admin",
    description: "Full access including settings",
    flags: {
      can_manage_knowledge: true,
      can_manage_appearance: true,
      can_resolve_queries: true,
      can_view_analytics_billing: true,
    },
  },
  custom: {
    label: "Custom",
    description: "Configure specific permissions",
    flags: {
      can_manage_knowledge: false,
      can_manage_appearance: false,
      can_resolve_queries: false,
      can_view_analytics_billing: false,
    },
  },
};

interface ChatbotTeamSettingsProps {
  chatbotId: string;
}

export function ChatbotTeamSettings({ chatbotId }: ChatbotTeamSettingsProps) {
  const { user, isAdmin } = useAuth();

  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [orgMembers, setOrgMembers] = useState<OrganizationMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Add Member State
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedMemberId, setSelectedMemberId] = useState<string>("");
  const [selectedPreset, setSelectedPreset] = useState<string>("viewer");
  const [customFlags, setCustomFlags] = useState({
    can_manage_knowledge: false,
    can_manage_appearance: false,
    can_resolve_queries: false,
    can_view_analytics_billing: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit State
  const [editingPermission, setEditingPermission] = useState<Permission | null>(
    null,
  );

  useEffect(() => {
    fetchData();
  }, [chatbotId]);

  // Update custom flags when preset changes
  useEffect(() => {
    if (selectedPreset !== "custom") {
      setCustomFlags(PRESETS[selectedPreset as keyof typeof PRESETS].flags);
    }
  }, [selectedPreset]);

  const fetchData = async () => {
    try {
      // Only show loading spinner on first load
      if (!hasLoadedOnce) {
        setLoading(true);
      }
      const token = getAccessToken();
      if (!token) return;

      const [permsRes, membersRes] = await Promise.all([
        apiRequestWithAuth<{ permissions: Permission[] }>(
          `/api/v1/chatbots/${chatbotId}/permissions`,
          token,
        ),
        apiRequestWithAuth<{ members: OrganizationMember[] }>(
          "/api/v1/members",
          token,
        ),
      ]);

      setPermissions(permsRes.permissions);
      setOrgMembers(membersRes.members);
      setHasLoadedOnce(true);
    } catch (err: any) {
      console.error("Failed to fetch data:", err);
      setError(err.message || "Failed to load permissions");
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = async () => {
    if (!selectedMemberId) return;

    try {
      setIsSubmitting(true);
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}/permissions`,
        token,
        {
          method: "POST",
          body: JSON.stringify({
            user_id: parseInt(selectedMemberId),
            permission_level: selectedPreset,
            ...customFlags,
          }),
        },
      );

      setShowAddModal(false);
      resetForm();
      fetchData();
    } catch (err: any) {
      setError(err.message || "Failed to add member");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!confirm("Are you sure you want to remove this member?")) return;

    try {
      const token = getAccessToken();
      if (!token) return;

      await apiRequestWithAuth(
        `/api/v1/chatbots/${chatbotId}/permissions/${userId}`,
        token,
        { method: "DELETE" },
      );

      fetchData();
    } catch (err: any) {
      toast.error(err.message || "Failed to remove member");
    }
  };

  const resetForm = () => {
    setSelectedMemberId("");
    setSelectedPreset("viewer");
    setCustomFlags(PRESETS.viewer.flags);
    setEditingPermission(null);
  };

  const openEditModal = (perm: Permission) => {
    setEditingPermission(perm);
    setSelectedMemberId(perm.user_id.toString());

    // Determine if it matches a preset
    let matchedPreset = "custom";
    for (const [key, preset] of Object.entries(PRESETS)) {
      if (key === "custom") continue;
      if (
        perm.permission_level === key &&
        perm.can_manage_knowledge === preset.flags.can_manage_knowledge &&
        perm.can_manage_appearance === preset.flags.can_manage_appearance &&
        perm.can_resolve_queries === preset.flags.can_resolve_queries &&
        perm.can_view_analytics_billing ===
          preset.flags.can_view_analytics_billing
      ) {
        matchedPreset = key;
        break;
      }
    }

    setSelectedPreset(matchedPreset);
    setCustomFlags({
      can_manage_knowledge: perm.can_manage_knowledge,
      can_manage_appearance: perm.can_manage_appearance,
      can_resolve_queries: perm.can_resolve_queries,
      can_view_analytics_billing: perm.can_view_analytics_billing,
    });
    setShowAddModal(true);
  };

  // Filter out members who already have permission (unless editing)
  // Also filter out admins since they have full access already
  const availableMembers = orgMembers.filter(
    (m) =>
      m.role !== "admin" &&
      (!permissions.some((p) => p.user_id === m.id) ||
        (editingPermission && editingPermission.user_id === m.id)),
  );

  if (loading) {
    return <SectionLoader />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Chatbot Team</h2>
          <p className="text-sm text-muted-foreground">
            Manage who has access to this specific chatbot
          </p>
        </div>
        <Button
          onClick={() => {
            resetForm();
            setShowAddModal(true);
          }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Member
        </Button>
      </div>

      <ErrorMessage message={error} />

      <div className="grid gap-4">
        {permissions.map((perm) => (
          <Card key={perm.id}>
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 font-semibold">
                  {(perm.user_username || perm.user_email)[0].toUpperCase()}
                </div>
                <div>
                  <div className="font-medium flex items-center gap-2">
                    {perm.user_name || `@${perm.user_username}`}
                    {perm.permission_level === "owner" && (
                      <Badge variant="secondary" className="text-xs">
                        Owner
                      </Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {perm.user_email}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex gap-2">
                  <Badge
                    variant="outline"
                    className={
                      perm.permission_level === "owner"
                        ? "bg-success/10 text-success border-success/30"
                        : perm.permission_level === "admin"
                          ? "bg-info/10 text-info border-info/30"
                          : perm.permission_level === "editor"
                            ? "bg-amber-500/10 text-amber-600 border-amber-500/30"
                            : "bg-muted text-muted-foreground border-border"
                    }
                  >
                    {perm.permission_level.charAt(0).toUpperCase() + perm.permission_level.slice(1)}
                  </Badge>
                </div>

                {perm.permission_level !== "owner" && (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openEditModal(perm)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleRemoveMember(perm.user_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Custom Modal */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editingPermission ? "Edit Member Access" : "Add Team Member"}
            </DialogTitle>
            <DialogDescription>
              Control what members can do with this chatbot.
            </DialogDescription>
          </DialogHeader>

            <div className="space-y-6">
              {!editingPermission && (
                <div className="space-y-2">
                  <Label>Select Member</Label>
                  <Select value={selectedMemberId} onValueChange={setSelectedMemberId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a team member..." />
                    </SelectTrigger>
                    <SelectContent>
                      {availableMembers.map((member) => (
                        <SelectItem key={member.id} value={member.id.toString()}>
                          {member.name || member.email} ({member.email})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="space-y-3 border rounded-lg p-4 bg-muted/20">
                <Label className="text-xs font-semibold uppercase text-muted-foreground mb-2 block">
                  Granular Permissions
                </Label>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="p_knowledge"
                    checked={customFlags.can_manage_knowledge}
                    onCheckedChange={(checked) => {
                      setCustomFlags((prev) => ({
                        ...prev,
                        can_manage_knowledge: !!checked,
                      }));
                      setSelectedPreset("custom");
                    }}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="p_knowledge"
                      className="cursor-pointer font-medium"
                    >
                      Manage Knowledge Base
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Add URLs, upload files, and edit Q&A pairs.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="p_appearance"
                    checked={customFlags.can_manage_appearance}
                    onCheckedChange={(checked) => {
                      setCustomFlags((prev) => ({
                        ...prev,
                        can_manage_appearance: !!checked,
                      }));
                      setSelectedPreset("custom");
                    }}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="p_appearance"
                      className="cursor-pointer font-medium"
                    >
                      Manage Appearance
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Customize colors, avatar, and widget settings.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="p_resolve"
                    checked={customFlags.can_resolve_queries}
                    onCheckedChange={(checked) => {
                      const isChecked = !!checked;
                      // If enabling resolve queries, also auto-enable analytics & usage
                      setCustomFlags((prev) => ({
                        ...prev,
                        can_resolve_queries: isChecked,
                        // Auto-enable analytics & usage when resolve queries is enabled
                        can_view_analytics_billing: isChecked
                          ? true
                          : prev.can_view_analytics_billing,
                      }));
                      setSelectedPreset("custom");
                    }}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="p_resolve"
                      className="cursor-pointer font-medium"
                    >
                      Resolve Queries
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      Manually answer user queries and view conversations. This
                      automatically includes Analytics & Usage access.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="p_analytics"
                    checked={customFlags.can_view_analytics_billing}
                    // Disable unchecking if resolve_queries is enabled
                    disabled={customFlags.can_resolve_queries}
                    onCheckedChange={(checked) => {
                      if (!customFlags.can_resolve_queries) {
                        setCustomFlags((prev) => ({
                          ...prev,
                          can_view_analytics_billing: !!checked,
                        }));
                        setSelectedPreset("custom");
                      }
                    }}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="p_analytics"
                      className={`cursor-pointer font-medium ${customFlags.can_resolve_queries ? "text-muted-foreground" : ""}`}
                    >
                      View Analytics & Usage
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      See conversation stats, usage metrics, and subscription
                      information.
                      {customFlags.can_resolve_queries &&
                        " (Required when Resolve Queries is enabled)"}
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  type="button"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleAddMember}
                  disabled={isSubmitting || !selectedMemberId}
                >
                  {isSubmitting ? (
                    <>
                      <ButtonSpinner />
                      Saving...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </Button>
              </div>
            </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

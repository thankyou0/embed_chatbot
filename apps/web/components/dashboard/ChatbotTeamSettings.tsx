"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getAccessToken } from "@/lib/auth";
import { apiRequestWithAuth } from "@/lib/api";
import { Plus, Trash2, X, AlertCircle } from "lucide-react";
import { SectionLoader, ButtonSpinner } from "@/components/ui/loading";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

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
      alert(err.message || "Failed to remove member");
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

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      )}

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
                        ? "bg-teal-50 text-teal-700 border-teal-200"
                        : perm.permission_level === "admin"
                          ? "bg-blue-50 text-blue-700 border-blue-200"
                          : "bg-gray-50 text-gray-700 border-gray-200"
                    }
                  >
                    {perm.permission_level === "owner"
                      ? "Owner"
                      : perm.permission_level === "admin"
                        ? "Admin"
                        : "Member"}
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
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full shadow-xl">
            <div className="p-6 border-b flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">
                  {editingPermission ? "Edit Member Access" : "Add Team Member"}
                </h2>
                <p className="text-sm text-muted-foreground">
                  Control what members can do with this chatbot.
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowAddModal(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {!editingPermission && (
                <div className="space-y-2">
                  <Label>Select Member</Label>
                  <select
                    className="w-full h-10 px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                    value={selectedMemberId}
                    onChange={(e) => setSelectedMemberId(e.target.value)}
                  >
                    <option value="">Select a team member...</option>
                    {availableMembers.map((member) => (
                      <option key={member.id} value={member.id.toString()}>
                        {member.name || member.email} ({member.email})
                      </option>
                    ))}
                  </select>
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
                      // If enabling resolve queries, also auto-enable analytics & billing
                      setCustomFlags((prev) => ({
                        ...prev,
                        can_resolve_queries: isChecked,
                        // Auto-enable analytics & billing when resolve queries is enabled
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
                      automatically includes Analytics & Billing access.
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
                      View Analytics & Billing
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      See conversation stats, usage metrics, and billing
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
          </div>
        </div>
      )}
    </div>
  );
}

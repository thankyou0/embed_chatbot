/**
 * Toast wrapper that mirrors sonner's API but also persists each
 * toast as a notification in the Header's notification panel.
 *
 * - User manually dismisses the toast → notification marked **read**
 * - Toast auto-closes (user missed it) → notification stays **unread**
 *
 * Usage: replace `import { toast } from "sonner"` with
 *        `import { toast } from "@/lib/notify-toast"`
 */

import { toast as sonnerToast, type ExternalToast } from "sonner";
import {
  loadNotifications,
  saveNotifications,
  type Notification,
} from "./notifications";

// ─── Helpers ──────────────────────────────────────────────
function generateId(): string {
  return `n_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/** Persist a new notification to localStorage and notify the Header. */
function addNotification(
  title: string,
  message: string,
  type: Notification["type"],
  read: boolean,
): string {
  const id = generateId();
  const existing = loadNotifications();
  const notification: Notification = {
    id,
    type,
    title,
    message,
    createdAt: new Date().toISOString(),
    read,
  };
  saveNotifications([notification, ...existing]);
  // Tell the Header component to reload its state
  window.dispatchEvent(new Event("notification-update"));
  return id;
}

/** Mark a specific notification as read in localStorage. */
function markAsRead(notifId: string): void {
  const notifications = loadNotifications();
  const updated = notifications.map((n) =>
    n.id === notifId ? { ...n, read: true } : n,
  );
  saveNotifications(updated);
  window.dispatchEvent(new Event("notification-update"));
}

// ─── Map sonner type → notification type ──────────────────
type NotifType = Notification["type"];

const TYPE_MAP: Record<string, NotifType> = {
  default: "info",
  info: "info",
  success: "success",
  error: "warning",
  warning: "warning",
};

// ─── Builder ──────────────────────────────────────────────
type ToastMessage = string | React.ReactNode;

function wrapToast(
  sonnerFn: typeof sonnerToast | typeof sonnerToast.success,
  type: NotifType,
) {
  return function (message: ToastMessage, options?: ExternalToast) {
    // Only persist string messages as notifications
    const title =
      typeof message === "string" ? message : String(message ?? "Notification");
    const description =
      typeof options?.description === "string" ? options.description : "";

    const notifId = addNotification(title, description, type, false);

    return sonnerFn(message, {
      ...options,
      onDismiss: (t) => {
        // User clicked dismiss → mark read
        markAsRead(notifId);
        options?.onDismiss?.(t);
      },
      onAutoClose: (t) => {
        // Auto-closed → stays unread
        options?.onAutoClose?.(t);
      },
    });
  };
}

// ─── Public API (drop-in replacement for sonner's `toast`) ─
export const toast = Object.assign(
  wrapToast(sonnerToast, "info"),
  {
    success: wrapToast(sonnerToast.success, "success"),
    error: wrapToast(sonnerToast.error, "warning"),
    warning: wrapToast(sonnerToast.warning, "warning"),
    info: wrapToast(sonnerToast.info, "info"),
    // Pass-through for loading / promise / dismiss / custom that
    // don't need notification persistence
    loading: sonnerToast.loading,
    promise: sonnerToast.promise,
    dismiss: sonnerToast.dismiss,
    message: sonnerToast.message,
    custom: sonnerToast.custom,
  },
);

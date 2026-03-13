// Notification system with localStorage persistence
// Provides welcome messages for new accounts and persistent read/dismiss state

export interface Notification {
  id: string;
  type: "info" | "warning" | "success";
  title: string;
  message: string;
  createdAt: string; // ISO date string
  read: boolean;
}

const STORAGE_KEY = "chatbot_notifications";
const WELCOME_SEED_KEY = "chatbot_notifications_seeded";

// Welcome notifications shown to every new account
const welcomeNotifications: Omit<Notification, "id" | "createdAt" | "read">[] = [
  {
    type: "success",
    title: "Welcome to EmbedChatbot!",
    message:
      "Your account is ready. Create your first chatbot to get started.",
  },
  {
    type: "info",
    title: "Add Knowledge Sources",
    message:
      "Upload documents, paste URLs, or add FAQs to train your chatbot with relevant content.",
  },
  {
    type: "info",
    title: "Customize Your Widget",
    message:
      "Personalize colours, avatar, and greeting message from the Appearance tab.",
  },
  {
    type: "info",
    title: "Invite Your Team",
    message:
      "Collaborate with team members by inviting them from Settings → Team.",
  },
];

function generateId(): string {
  return `n_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/** Read notifications from localStorage */
export function loadNotifications(): Notification[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Notification[];
    // Auto-dismiss: remove read notifications older than 7 days
    const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    return parsed.filter(
      (n) => !n.read || new Date(n.createdAt).getTime() > sevenDaysAgo,
    );
  } catch {
    return [];
  }
}

/** Save notifications to localStorage */
export function saveNotifications(notifications: Notification[]): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications));
  } catch {
    // localStorage full or unavailable — silently ignore
  }
}

/** Seed welcome notifications for a new account (runs once per browser) */
export function seedWelcomeNotifications(): Notification[] {
  if (typeof window === "undefined") return [];
  const alreadySeeded = localStorage.getItem(WELCOME_SEED_KEY);
  if (alreadySeeded) return loadNotifications();

  const now = new Date();
  const seeded: Notification[] = welcomeNotifications.map((n, i) => ({
    ...n,
    id: generateId() + `_${i}`,
    // Stagger timestamps so they appear ordered
    createdAt: new Date(now.getTime() - i * 60_000).toISOString(),
    read: false,
  }));

  saveNotifications(seeded);
  localStorage.setItem(WELCOME_SEED_KEY, "true");
  return seeded;
}

/** Mark a single notification as read */
export function markRead(
  notifications: Notification[],
  id: string,
): Notification[] {
  const updated = notifications.map((n) =>
    n.id === id ? { ...n, read: true } : n,
  );
  saveNotifications(updated);
  return updated;
}

/** Mark all notifications as read */
export function markAllRead(notifications: Notification[]): Notification[] {
  const updated = notifications.map((n) => ({ ...n, read: true }));
  saveNotifications(updated);
  return updated;
}

/** Dismiss (remove) a single notification */
export function dismissNotification(
  notifications: Notification[],
  id: string,
): Notification[] {
  const updated = notifications.filter((n) => n.id !== id);
  saveNotifications(updated);
  return updated;
}

/** Clear all notifications */
export function clearAll(): Notification[] {
  saveNotifications([]);
  return [];
}

/** Format relative time from ISO date string */
export function formatRelativeTime(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(isoDate).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

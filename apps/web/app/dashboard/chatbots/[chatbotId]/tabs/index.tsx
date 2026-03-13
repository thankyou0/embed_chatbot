import dynamic from "next/dynamic";
import { PageLoader } from "@/components/ui/loading";

// Code-split each tab — only the active tab's JS is loaded
const TabFallback = () => (
  <div className="flex items-center justify-center py-12">
    <div className="animate-pulse text-muted-foreground text-sm">Loading…</div>
  </div>
);

export const OverviewTab = dynamic(
  () => import("./OverviewTab").then((m) => ({ default: m.OverviewTab })),
  { loading: TabFallback },
);

export const KnowledgeTab = dynamic(
  () => import("./KnowledgeTab").then((m) => ({ default: m.KnowledgeTab })),
  { loading: TabFallback },
);

export const AppearanceTab = dynamic(
  () => import("./AppearanceTab").then((m) => ({ default: m.AppearanceTab })),
  { loading: TabFallback },
);

export const InstallTab = dynamic(
  () => import("./InstallTab").then((m) => ({ default: m.InstallTab })),
  { loading: TabFallback },
);

export const SettingsTab = dynamic(
  () => import("./SettingsTab").then((m) => ({ default: m.SettingsTab })),
  { loading: TabFallback },
);


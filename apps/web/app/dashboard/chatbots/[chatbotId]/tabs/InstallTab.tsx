"use client";

import React from "react";
import {
  Sparkles,
  Globe,
  Code,
  CheckCircle2,
  CheckSquare,
  HelpCircle,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface InstallTabProps {
  chatbotId: string;
  embedCopyStatus: string | null;
  setEmbedCopyStatus: (status: string | null) => void;
}

export function InstallTab({
  chatbotId,
  embedCopyStatus,
  setEmbedCopyStatus,
}: InstallTabProps) {
  const copyToClipboard = async (elementId: string) => {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.textContent || "";
    try {
      await navigator.clipboard.writeText(text);
      setEmbedCopyStatus(elementId);
      setTimeout(() => setEmbedCopyStatus(null), 2000);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      setEmbedCopyStatus(elementId);
      setTimeout(() => setEmbedCopyStatus(null), 2000);
      document.body.removeChild(ta);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Start Guide */}
      <Card className="border-emerald-200 bg-gradient-to-r from-emerald-50/50 to-teal-50/50">
        <CardHeader>
          <div className="flex items-start gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-600 flex items-center justify-center flex-shrink-0 shadow-sm">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <CardTitle>Quick Start Guide</CardTitle>
              <CardDescription className="mt-1">
                Get your chatbot live on your website in 3 simple steps
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                step: 1,
                title: "Choose Your Integration Method",
                desc: "Select between JavaScript Widget (recommended) or iframe embed below based on your platform.",
              },
              {
                step: 2,
                title: "Copy and Paste the Code",
                desc: "Copy the code snippet and paste it into your website's HTML, just before the closing </body> tag.",
              },
              {
                step: 3,
                title: "Test Your Chatbot",
                desc: "Refresh your website and look for the chat widget in the bottom corner. Click it to start chatting!",
              },
            ].map(({ step, title, desc }) => (
              <div key={step} className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-600 to-teal-600 text-white flex items-center justify-center font-semibold text-sm shadow-sm">
                  {step}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-sm mb-1">{title}</h4>
                  <p className="text-sm text-muted-foreground">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* JavaScript Widget */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                JavaScript Widget
                <Badge
                  variant="secondary"
                  className="bg-emerald-50 text-emerald-700 border-emerald-200"
                >
                  Recommended
                </Badge>
              </CardTitle>
              <CardDescription className="mt-1">
                Best for most websites. Lightweight, fully customizable, and
                works with any platform.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            {[
              { bold: "Automatic updates:", text: "Changes to appearance and settings sync instantly" },
              { bold: "Lightweight:", text: "Only ~15KB gzipped, won't slow down your site" },
              { bold: "Mobile responsive:", text: "Optimized for all devices and screen sizes" },
            ].map(({ bold, text }) => (
              <div key={bold} className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm">
                  <strong>{bold}</strong> {text}
                </p>
              </div>
            ))}
          </div>

          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold mb-3">Installation Code</h4>
            <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm overflow-x-auto">
              <pre id="embed-script">{`<script src="${
                process.env.NEXT_PUBLIC_WIDGET_URL ||
                process.env.NEXT_PUBLIC_APP_URL ||
                "http://localhost:3001"
              }/widget.umd.js"></script>
<script>
  ChatbotWidget.init({
    chatbotId: "${chatbotId}"${
                process.env.NEXT_PUBLIC_API_URL
                  ? `,\n    apiUrl: "${process.env.NEXT_PUBLIC_API_URL}"`
                  : ""
              }
  });
</script>`}</pre>
            </div>
            <Button
              variant="default"
              className="mt-3"
              onClick={() => copyToClipboard("embed-script")}
            >
              <Code className="h-4 w-4 mr-2" />
              {embedCopyStatus === "embed-script" ? "Copied!" : "Copy Code"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Platform-Specific Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Platform-Specific Instructions</CardTitle>
          <CardDescription>
            Step-by-step guides for popular platforms
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* HTML */}
            <PlatformGuide
              icon={<Globe className="h-5 w-5 text-emerald-600" />}
              title="HTML / Static Websites"
              steps={[
                "Open your HTML file in a text editor",
                <>Find the closing <code className="bg-muted px-1.5 py-0.5 rounded text-xs">&lt;/body&gt;</code> tag</>,
                "Paste the JavaScript Widget code just before it",
                "Save the file and refresh your browser",
              ]}
            />
            {/* React */}
            <PlatformGuide
              icon={<Code className="h-5 w-5 text-blue-600" />}
              title="React / Next.js"
              steps={[
                <>Add the script to your <code className="bg-muted px-1.5 py-0.5 rounded text-xs">public/index.html</code> (React) or <code className="bg-muted px-1.5 py-0.5 rounded text-xs">_document.tsx</code> (Next.js)</>,
                <>Place it in the <code className="bg-muted px-1.5 py-0.5 rounded text-xs">&lt;body&gt;</code> section or use <code className="bg-muted px-1.5 py-0.5 rounded text-xs">useEffect()</code> to load it dynamically</>,
                "Alternatively, use the iframe method for easier integration",
              ]}
            />
            {/* WordPress */}
            <PlatformGuide
              icon={<Globe className="h-5 w-5 text-blue-500" />}
              title="WordPress"
              steps={[
                <>Go to <strong>Appearance → Theme File Editor</strong></>,
                <>Select <code className="bg-muted px-1.5 py-0.5 rounded text-xs">footer.php</code> from the right sidebar</>,
                <>Paste the code before the <code className="bg-muted px-1.5 py-0.5 rounded text-xs">&lt;/body&gt;</code> tag</>,
                <>Click <strong>Update File</strong></>,
                <em>Or use a plugin like &quot;Insert Headers and Footers&quot; for easier management</em>,
              ]}
            />
            {/* Shopify */}
            <PlatformGuide
              icon={<Globe className="h-5 w-5 text-green-600" />}
              title="Shopify"
              steps={[
                <>Go to <strong>Online Store → Themes</strong></>,
                <>Click <strong>Actions → Edit code</strong></>,
                <>Find <code className="bg-muted px-1.5 py-0.5 rounded text-xs">theme.liquid</code> under Layout</>,
                <>Paste the code before <code className="bg-muted px-1.5 py-0.5 rounded text-xs">&lt;/body&gt;</code></>,
                "Save and preview your store",
              ]}
            />
            {/* Wix / Squarespace */}
            <PlatformGuide
              icon={<Globe className="h-5 w-5 text-orange-600" />}
              title="Wix / Squarespace / Webflow"
              steps={[
                "Look for \"Custom Code\" or \"Code Injection\" in your site settings",
                <>Add the script to the <strong>Footer</strong> or <strong>Body End</strong> section</>,
                "Save and publish your changes",
                <em>Note: Exact steps vary by platform version - check their documentation</em>,
              ]}
            />
          </div>
        </CardContent>
      </Card>

      {/* iframe Alternative */}
      <Card>
        <CardHeader>
          <CardTitle>iframe Embed (Alternative)</CardTitle>
          <CardDescription>
            Use this if you prefer iframe embedding or need to restrict JavaScript execution
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-slate-950 text-slate-50 p-4 rounded-md font-mono text-sm overflow-x-auto">
            <pre id="embed-iframe">{`<iframe
  src="${
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"
  }/embed/${chatbotId}"
  width="400"
  height="600"
  style="border:0; width:100%; min-width:320px; min-height:420px;"
  title="Chatbot"
></iframe>`}</pre>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => copyToClipboard("embed-iframe")}
            >
              <Code className="h-4 w-4 mr-2" />
              {embedCopyStatus === "embed-iframe"
                ? "Copied!"
                : "Copy iframe Code"}
            </Button>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-2">
              <HelpCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-900">
                <strong>Note:</strong> The iframe method displays the chatbot
                inline on your page, not as a floating widget. Adjust the width
                and height attributes to fit your layout.
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Testing & Troubleshooting */}
      <Card>
        <CardHeader>
          <CardTitle>Testing & Troubleshooting</CardTitle>
          <CardDescription>
            Verify your installation and fix common issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <CheckSquare className="h-4 w-4 text-teal-600" />
                Testing Checklist
              </h4>
              <div className="space-y-2 ml-6">
                {[
                  "Widget appears in the bottom corner of your page",
                  "Clicking the widget opens the chat interface",
                  "Your welcome message displays correctly",
                  "Bot responds to test messages",
                  "Widget works on mobile devices",
                ].map((text) => (
                  <div key={text} className="flex items-start gap-2">
                    <div className="h-5 w-5 rounded border-2 border-muted-foreground flex-shrink-0 mt-0.5" />
                    <p className="text-sm">{text}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t pt-6">
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-amber-600" />
                Common Issues & Solutions
              </h4>
              <div className="space-y-4">
                <TroubleshootItem
                  title="Widget doesn't appear"
                  tips={[
                    "Check browser console for errors (F12)",
                    <>Verify the code is placed before the <code className="bg-background px-1 rounded">&lt;/body&gt;</code> tag</>,
                    "Clear browser cache and hard refresh (Ctrl+F5)",
                    "Ensure your chatbot status is set to \"Active\" in Settings",
                  ]}
                />
                <TroubleshootItem
                  title="Widget appears but doesn't respond"
                  tips={[
                    "Verify you've added knowledge sources in the Knowledge tab",
                    "Check that your knowledge sources are indexed",
                    "Look for API errors in the browser console",
                  ]}
                />
                <TroubleshootItem
                  title="Widget conflicts with other elements"
                  tips={[
                    "Adjust widget position in the Appearance tab",
                    "Use offset settings to fine-tune placement",
                    "Check for CSS conflicts with z-index",
                  ]}
                />
              </div>
            </div>

            <div className="border-t pt-6">
              <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
                <div className="flex gap-3">
                  <HelpCircle className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm text-teal-900 mb-1">
                      Still need help?
                    </h4>
                    <p className="text-sm text-teal-800">
                      If you&apos;re experiencing issues not covered here,
                      please contact our support team or check our documentation
                      for more detailed guides and API references.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ── Helpers ─────────────────────────────────────────────── */

function PlatformGuide({
  icon,
  title,
  steps,
}: {
  icon: React.ReactNode;
  title: string;
  steps: React.ReactNode[];
}) {
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center gap-2">
        {icon}
        <h4 className="font-semibold">{title}</h4>
      </div>
      <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground ml-7">
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    </div>
  );
}

function TroubleshootItem({
  title,
  tips,
}: {
  title: string;
  tips: React.ReactNode[];
}) {
  return (
    <div className="bg-muted/50 rounded-lg p-4">
      <p className="font-medium text-sm mb-1">{title}</p>
      <ul className="text-sm text-muted-foreground space-y-1 ml-4 list-disc">
        {tips.map((tip, i) => (
          <li key={i}>{tip}</li>
        ))}
      </ul>
    </div>
  );
}

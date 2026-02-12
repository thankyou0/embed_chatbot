import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import { readFileSync } from "fs";
import { join } from "path";

// Plugin to inject CSS into JS bundle
const injectCss = () => {
  return {
    name: "inject-css",
    apply: "build",
    enforce: "post",
    generateBundle(options, bundle) {
      // Find the CSS file
      const cssFileName = Object.keys(bundle).find((fileName) =>
        fileName.endsWith(".css"),
      );

      if (!cssFileName) return;

      const cssAsset = bundle[cssFileName];
      if (cssAsset.type !== "asset") return;

      const cssCode = cssAsset.source;

      // Inject CSS into each JS bundle
      for (const fileName of Object.keys(bundle)) {
        if (fileName.endsWith(".js")) {
          const jsChunk = bundle[fileName];
          if (jsChunk.type !== "chunk") continue;

          // Prepend CSS injection code
          const cssInjectionCode = `
(function() {
  if (typeof document !== 'undefined') {
    var style = document.createElement('style');
    style.textContent = ${JSON.stringify(cssCode)};
    document.head.appendChild(style);
  }
})();
`;
          jsChunk.code = cssInjectionCode + jsChunk.code;
        }
      }

      // Remove CSS file from bundle
      delete bundle[cssFileName];
    },
  };
};

// Plugin to serve built widget files in dev mode
const serveBuiltFiles = () => {
  return {
    name: "serve-built-files",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // Serve widget.umd.js from dist if it exists
        if (req.url === "/widget.umd.js" || req.url === "/widget.es.js") {
          try {
            const fileName = req.url.slice(1); // remove leading /
            const filePath = join(__dirname, "dist", fileName);
            const content = readFileSync(filePath);
            res.setHeader("Content-Type", "application/javascript");
            res.end(content);
            return;
          } catch (e) {
            // File doesn't exist, continue to next middleware
          }
        }
        next();
      });
    },
  };
};

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [preact(), serveBuiltFiles(), injectCss()],
  resolve: {
    alias: {
      react: "preact/compat",
      "react-dom": "preact/compat",
    },
    // Ensure workspace dependencies are resolved from root
    dedupe: ["preact", "preact/compat", "preact/jsx-runtime"],
    // Resolve from root node_modules for workspace packages
    conditions: ["import", "module", "browser", "default"],
  },
  build: {
    lib: {
      entry: "src/index.tsx",
      name: "ChatbotWidget",
      fileName: (format) => `widget.${format}.js`,
      formats: ["es", "umd"],
    },
    rollupOptions: {
      output: {
        extend: true,
        globals: {
          preact: "Preact",
          "preact/jsx-runtime": "PreactJSXRuntime",
        },
      },
      // Don't externalize preact - bundle it
      external: (id) => {
        // Only externalize node built-ins
        return id.startsWith("node:");
      },
    },
    emptyOutDir: true,
    cssCodeSplit: false,
    commonjsOptions: {
      include: [/node_modules/],
      transformMixedEsModules: true,
    },
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
  },
  optimizeDeps: {
    include: ["preact", "preact/jsx-runtime", "@chatbot/chatbot-widget"],
  },
});

import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'
import { readFileSync } from 'fs'
import { join } from 'path'

// Plugin to serve built widget files in dev mode
const serveBuiltFiles = () => {
  return {
    name: 'serve-built-files',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // Serve widget.umd.js from dist if it exists
        if (req.url === '/widget.umd.js' || req.url === '/widget.es.js') {
          try {
            const fileName = req.url.slice(1) // remove leading /
            const filePath = join(__dirname, 'dist', fileName)
            const content = readFileSync(filePath)
            res.setHeader('Content-Type', 'application/javascript')
            res.end(content)
            return
          } catch (e) {
            // File doesn't exist, continue to next middleware
          }
        }
        next()
      })
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [preact(), serveBuiltFiles()],
  resolve: {
    alias: {
      'react': 'preact/compat',
      'react-dom': 'preact/compat',
    },
    // Ensure workspace dependencies are resolved from root
    dedupe: ['preact', 'preact/compat', 'preact/jsx-runtime'],
    // Resolve from root node_modules for workspace packages
    conditions: ['import', 'module', 'browser', 'default'],
  },
  build: {
    lib: {
      entry: 'src/index.tsx',
      name: 'ChatbotWidget',
      fileName: (format) => `widget.${format}.js`,
      formats: ['es', 'umd']
    },
    rollupOptions: {
      output: {
        extend: true,
        globals: {
          'preact': 'Preact',
          'preact/jsx-runtime': 'PreactJSXRuntime',
        },
      },
      // Don't externalize preact - bundle it
      external: (id) => {
        // Only externalize node built-ins
        return id.startsWith('node:');
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
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  optimizeDeps: {
    include: ['preact', 'preact/jsx-runtime', '@chatbot/chatbot-widget'],
  },
})

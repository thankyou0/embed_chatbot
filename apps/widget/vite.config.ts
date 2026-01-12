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
    }
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
      }
    },
    emptyOutDir: true,
    cssCodeSplit: false,
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  }
})

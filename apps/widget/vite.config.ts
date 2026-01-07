import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [preact()],
  build: {
    lib: {
      entry: 'src/main.tsx',
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
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  }
})

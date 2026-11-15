import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  publicDir: false,
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  ssr: { noExternal: true },
  build: {
    ssr: 'scripts/render-cv.tsx',
    outDir: '../backend/argus/cv_templates',
    emptyOutDir: false,
    rollupOptions: { output: { entryFileNames: 'render.mjs' } },
  },
})

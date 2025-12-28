import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0', // Allow access from network (optional)
    // Proxy API requests to backend server
    // Frontend runs on PC, backend runs on server at 192.168.0.109:8000
    proxy: {
      '/api': {
        target: 'http://192.168.0.109:8000',
        changeOrigin: true,
        secure: false, // Allow self-signed certificates if needed
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})


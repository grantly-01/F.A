import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // <-- ЭТО ОБЯЗАТЕЛЬНО ДЛЯ DOCKER
    strictPort: true,
    port: 5173,
    watch: {
      usePolling: true // <-- ЭТО НУЖНО ДЛЯ WINDOWS/WSL, чтобы работала авто-перезагрузка
    }
  }
})
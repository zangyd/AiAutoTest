import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    cors: true,
    proxy: {},
    fs: {
      strict: true
    }
  },
  define: {
    __VUE_PROD_DEVTOOLS__: true, // 生产环境启用devtools
    __VUE_DEVTOOLS_HOST__: JSON.stringify('localhost'), // devtools主机
    __VUE_DEVTOOLS_PORT__: JSON.stringify('8098'), // devtools端口
  }
}) 
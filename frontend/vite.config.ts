import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import * as sass from 'sass'

export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        implementation: sass,
        sassOptions: {
          outputStyle: 'expanded'
        },
        api: 'modern',
        silenceDeprecations: ['legacy-js-api']
      }
    }
  },
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
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    },
    fs: {
      strict: true
    },
    hmr: {
      overlay: true
    }
  },
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios'
    ],
    exclude: []
  },
  build: {
    cssCodeSplit: false,
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      }
    }
  },
  define: {
    __VUE_PROD_DEVTOOLS__: true, // 生产环境启用devtools
    __VUE_DEVTOOLS_HOST__: JSON.stringify('localhost'), // devtools主机
    __VUE_DEVTOOLS_PORT__: JSON.stringify('8098'), // devtools端口
  }
}) 
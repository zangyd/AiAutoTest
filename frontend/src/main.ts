import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia'

const app = createApp(App)
const pinia = createPinia()

// 开发环境下启用Vue Devtools
if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true
  app.config.performance = true
}

app.use(router)
app.use(pinia)

app.mount('#app') 
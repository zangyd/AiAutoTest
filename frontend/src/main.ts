import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia'
import errorTracker from './utils/errorTracker'

// 导入全局样式
import './styles/global.scss'

const app = createApp(App)
const pinia = createPinia()

// 开发环境下启用Vue Devtools
if (process.env.NODE_ENV === 'development') {
  app.config.devtools = true
  app.config.performance = true
}

// 初始化错误追踪
errorTracker.init(app)

app.use(router)
app.use(pinia)

app.mount('#app') 
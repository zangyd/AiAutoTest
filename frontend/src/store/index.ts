import { createPinia } from 'pinia'
import { markRaw } from 'vue'
import router from '../router'

const pinia = createPinia()

// 添加路由到store
pinia.use(({ store }) => {
  store.router = markRaw(router)
})

export default pinia 
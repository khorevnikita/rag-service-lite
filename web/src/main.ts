import 'element-plus/theme-chalk/display.css'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import i18n from '@/i18n/index'
import App from './App.vue'
import router from './router'
import SuperTokens from 'supertokens-web-js'
import Session from 'supertokens-web-js/recipe/session'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

SuperTokens.init({
  appInfo: {
    appName: 'rag-service',
    apiDomain: import.meta.env.VITE_APP_ENDPOINT,
    apiBasePath: '/api/auth'
  },
  recipeList: [Session.init()]
})

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')

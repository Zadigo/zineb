import { createApp } from 'vue'
import { createAxios } from '@/plugins/axios'
import { createPinia } from 'pinia'
import App from './App.vue'

import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'mdb-ui-kit/css/mdb.min.css'

const app = createApp(App)
const store = createPinia()

app.use(createAxios())
app.use(store)
app.use(router)
app.mount('#app')

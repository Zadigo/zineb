import { createRouter, createWebHistory } from 'vue-router'
import { loadView } from '@/composables/utils'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home_view',
      component: loadView('IndexView')
    }
  ]
})

export default router

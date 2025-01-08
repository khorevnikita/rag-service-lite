import { createRouter, createWebHistory } from 'vue-router'
import Session from 'supertokens-web-js/recipe/session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue')
    },
    {
      path: '/conversations',
      name: 'conversations',
      component: () => import('../views/ConversationsView.vue')
    },
    {
      path: '/conversations/:id',
      name: 'conversation-questions',
      component: () => import('../views/QuestionsView.vue')
    },
    /* {
          path: '/questions',
          name: 'questions',
          component: () => import('../views/QuestionsView.vue')
        },*/
    {
      path: '/documents',
      name: 'documents',
      component: () => import('../views/DocumentsView.vue')
    },
    {
      path: '/documents/:id',
      name: 'documentItem',
      component: () => import('../views/Documents/DocumentsItemView.vue')
    },
    {
      path: '/usage',
      name: 'usage',
      component: () => import('../views/UsageView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue')
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('../views/Auth/AuthView.vue')
    },
    {
      path: '/access',
      name: 'access',
      component: () => import('../views/Auth/NoAccessView.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const isAuthenticated = await Session.doesSessionExist()

  const guestRoutes = ['auth', 'access']

  if (!isAuthenticated && !guestRoutes.includes(String(to.name))) {
    next({ name: 'auth' }) // Если токен есть, продолжаем навигацию
  } else if (isAuthenticated && guestRoutes.includes(String(to.name))) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})
export default router

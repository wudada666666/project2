import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../api'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/words', name: 'Words', component: () => import('../views/Words.vue') },
  { path: '/study', name: 'Study', component: () => import('../views/Study.vue') },
  { path: '/review', name: 'Review', component: () => import('../views/Review.vue') },
  { path: '/test', name: 'Test', component: () => import('../views/Test.vue') },
  { path: '/stats', name: 'Stats', component: () => import('../views/Stats.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta.public) return true
  if (!getToken()) return { path: '/login', query: { redirect: to.fullPath } }
  return true
})

export default router

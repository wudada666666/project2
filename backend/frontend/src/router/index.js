import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/words', name: 'Words', component: () => import('../views/Words.vue') },
  { path: '/study', name: 'Study', component: () => import('../views/Study.vue') },
  { path: '/review', name: 'Review', component: () => import('../views/Review.vue') },
  { path: '/test', name: 'Test', component: () => import('../views/Test.vue') },
  { path: '/stats', name: 'Stats', component: () => import('../views/Stats.vue') },
]

export default createRouter({ history: createWebHistory(), routes })

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUsername, clearAuth } from './api'

const route = useRoute()
const router = useRouter()
const username = ref(getUsername())

onMounted(() => {
  username.value = getUsername()
})

function logout() {
  clearAuth()
  router.push('/login')
}
</script>

<template>
  <div v-if="route.path === '/login'" class="auth-layout">
    <router-view />
  </div>
  <div v-else class="layout">
    <aside class="sidebar">
      <div class="logo">✨ CET-6 背词</div>
      <nav>
        <router-link to="/" :class="{ active: route.path === '/' }">🏠 首页</router-link>
        <router-link to="/words" :class="{ active: route.path === '/words' }">📖 单词本</router-link>
        <router-link to="/study" :class="{ active: route.path === '/study' }">🎯 背诵</router-link>
        <router-link to="/test" :class="{ active: route.path === '/test' }">📝 测验</router-link>
        <router-link to="/review" :class="{ active: route.path === '/review' }">🔄 复习</router-link>
        <router-link to="/stats" :class="{ active: route.path === '/stats' }">📊 统计</router-link>
      </nav>
      <div class="sidebar-footer">
        <div v-if="username" class="user-bar">
          <span>👤 {{ username }}</span>
          <button class="logout-btn" @click="logout">退出</button>
        </div>
        <div>CET-6 · 5523词</div>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.auth-layout{min-height:100vh;background:var(--bg)}
.user-bar{display:flex;flex-direction:column;gap:6px;margin-bottom:8px;font-size:13px;font-weight:600}
.logout-btn{border:1px solid var(--border);background:#fff;border-radius:8px;padding:4px 8px;font-size:12px;cursor:pointer;color:var(--dim)}
.logout-btn:hover{border-color:var(--purple);color:var(--purple)}
</style>

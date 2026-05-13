<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="layout">
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
      <div class="sidebar-footer">CET-6 · 5523词</div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ total: 5523, mastered: 0, unclear: 0, unknown: 0, unmarked: 5523 })
const last = ref(null)
const total = ref(null)
const pct = ref(0)

onMounted(async () => {
  try { const { data } = await api.getStats(); stats.value = data; pct.value = Math.round(data.mastered / data.total * 100) } catch {}
  try { const { data } = await api.lastSession(); last.value = data } catch {}
  try { const { data } = await api.totalStats(); total.value = data } catch {}
})
</script>

<template>
  <div class="welcome">
    <div class="hero-icon">📚</div>
    <h1>CET-6 快乐背词</h1>
    <p class="subtitle">每天进步一点点，四级六级不是梦 ✨</p>

    <div class="stats-grid home-stats">
      <div class="stat-card t">
        <div class="stat-icon">📖</div>
        <div class="num">{{ stats.total }}</div>
        <div class="lbl">总词量</div>
      </div>
      <div class="stat-card m">
        <div class="stat-icon">✅</div>
        <div class="num">{{ stats.mastered }}</div>
        <div class="lbl">已掌握</div>
      </div>
      <div class="stat-card u">
        <div class="stat-icon">🤔</div>
        <div class="num">{{ stats.unclear }}</div>
        <div class="lbl">待复习</div>
      </div>
      <div class="stat-card n">
        <div class="stat-icon">❌</div>
        <div class="num">{{ stats.unknown }}</div>
        <div class="lbl">不认识</div>
      </div>
    </div>

    <div v-if="last && last.total > 0" class="last-session">
      <div class="session-card">
        <div class="session-icon-wrap" style="background:linear-gradient(135deg,#7c3aed,#a78bfa)">
          <span>📝</span>
        </div>
        <div class="session-value">{{ last.total }}</div>
        <div class="session-label">上次背词</div>
      </div>
      <div class="session-card">
        <div class="session-icon-wrap" style="background:linear-gradient(135deg,#10b981,#34d399)">
          <span>🎯</span>
        </div>
        <div class="session-value">{{ last.accuracy }}%</div>
        <div class="session-label">正确率</div>
      </div>
      <div class="session-card">
        <div class="session-icon-wrap" style="background:linear-gradient(135deg,#f97316,#fb923c)">
          <span>⏱️</span>
        </div>
        <div class="session-value">{{ Math.floor(last.duration/60) }}分{{ last.duration%60 }}秒</div>
        <div class="session-label">用时</div>
      </div>
    </div>

    <div v-if="total && total.total_words > 0" class="total-info">
      <span class="total-info-item">📊 {{ total.sessions }} 次练习</span>
      <span class="total-info-divider"></span>
      <span class="total-info-item">📝 {{ total.total_words }} 词</span>
      <span class="total-info-divider"></span>
      <span class="total-info-item">✅ 掌握 {{ total.mastered }} 词</span>
    </div>

    <router-link to="/study" class="btn-start">🚀 去背单词</router-link>
  </div>
</template>

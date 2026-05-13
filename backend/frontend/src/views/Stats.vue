<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ total: 5523, mastered: 0, unclear: 0, unknown: 0, unmarked: 5523 })
const total = ref(null)

onMounted(async () => {
  try { const { data } = await api.getStats(); stats.value = data } catch {}
  try { const { data } = await api.totalStats(); total.value = data } catch {}
})

const pct = (n) => Math.max(0, Math.min(100, Math.round(n / stats.value.total * 100)))
</script>

<template>
  <h1 class="page-title">📊 学习统计</h1>

  <div class="stats-grid">
    <div class="stat-card t"><div class="num">{{ stats.total }}</div><div class="lbl">总词汇量</div></div>
    <div class="stat-card m"><div class="num">{{ stats.mastered }}</div><div class="lbl">已掌握</div></div>
    <div class="stat-card u"><div class="num">{{ stats.unclear }}</div><div class="lbl">待复习</div></div>
    <div class="stat-card n"><div class="num">{{ stats.unknown }}</div><div class="lbl">不认识</div></div>
  </div>

  <div class="card-grid">
    <div class="card">
      <h3 style="margin-bottom:12px">✅ 已掌握 {{ pct(stats.mastered) }}%</h3>
      <div class="progress-bar"><div class="fill" :style="{ width: pct(stats.mastered)+'%', background: 'var(--green)' }"></div></div>
    </div>
    <div class="card">
      <h3 style="margin-bottom:12px">📋 待复习 {{ pct(stats.unclear) }}%</h3>
      <div class="progress-bar"><div class="fill" :style="{ width: pct(stats.unclear)+'%', background: 'var(--coral)' }"></div></div>
    </div>
    <div class="card">
      <h3 style="margin-bottom:12px">❌ 不认识 {{ pct(stats.unknown) }}%</h3>
      <div class="progress-bar"><div class="fill" :style="{ width: pct(stats.unknown)+'%', background: 'var(--red)' }"></div></div>
    </div>
    <div class="card">
      <h3 style="margin-bottom:12px">⬜ 未标记 {{ pct(stats.unmarked) }}%</h3>
      <div class="progress-bar"><div class="fill" :style="{ width: pct(stats.unmarked)+'%' }"></div></div>
    </div>
  </div>

  <div v-if="total && total.total_words > 0" class="card" style="margin-top:16px">
    <h3 style="margin-bottom:12px">📈 历史总览</h3>
    <div style="display:flex;gap:32px;flex-wrap:wrap;font-size:14px">
      <div><strong>{{ total.sessions }}</strong> 次练习</div>
      <div><strong>{{ total.total_words }}</strong> 词累计学习</div>
      <div><strong>{{ total.mastered }}</strong> 词已掌握</div>
      <div><strong>{{ Math.floor(total.total_sec/60) }}</strong> 分钟总学习时长</div>
    </div>
  </div>
</template>

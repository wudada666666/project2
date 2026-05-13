<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const dueWords = ref([])
const wrongWords = ref([])
const favs = ref([])
const pendingReview = ref([])
const idx = ref(0)
const flipped = ref(false)
const current = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const [due, wrong, fav, pending] = await Promise.all([
      api.getReviewDue(),
      api.getWrongWords(),
      api.getFavorites(),
      api.getPendingReview(),
    ])
    dueWords.value = due.data
    wrongWords.value = wrong.data
    favs.value = fav.data
    pendingReview.value = pending.data
  } catch {}
  loading.value = false
})

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t)
  u.lang = 'en-US'; u.rate = 0.85
  speechSynthesis.speak(u)
}

function startReview(words) {
  dueWords.value = []
  wrongWords.value = []
  favs.value = []
  pendingReview.value = []
  dueWords.value = words
  idx.value = 0; flipped.value = false
  current.value = dueWords.value[0]
  if (current.value) speak(current.value.english)
}

function mark(status) {
  if (!current.value) return
  api.markProgress(current.value.id, status)
  dueWords.value.splice(idx.value, 1)
  if (dueWords.value.length === 0) { current.value = null; return }
  if (idx.value >= dueWords.value.length) idx.value = dueWords.value.length - 1
  flipped.value = false; current.value = dueWords.value[idx.value]
  speak(current.value.english)
}
function flip() { flipped.value = !flipped.value; if (flipped.value) speak(current.value.english) }
function unmark(w) { api.markProgress(w.id, 0); wrongWords.value = wrongWords.value.filter(x => x.id !== w.id) }
function unfav(w) { api.toggleFavorite(w.id, 'remove'); favs.value = favs.value.filter(x => x.id !== w.id) }

async function confirmPending(w) {
  await api.confirmReview(w.id)
  pendingReview.value = pendingReview.value.filter(x => x.id !== w.id)
}
</script>

<template>
  <h1 class="page-title">🔄 复习中心</h1>

  <div v-if="loading" class="empty"><h3>加载中…</h3></div>

  <template v-else>
    <!-- 艾宾浩斯到期复习 -->
    <div class="card" v-if="dueWords.length > 0 && !current">
      <h3 style="margin-bottom:10px">📅 今日待复习 (艾宾浩斯) · {{ dueWords.length }} 词</h3>
      <button class="btn btn-purple" @click="startReview(dueWords)">开始复习</button>
    </div>
    <div class="card" v-else-if="dueWords.length === 0 && !current">
      <p style="color:var(--dim)">✅ 今日无到期复习，干得漂亮！</p>
    </div>

    <!-- 复习中 -->
    <div v-if="current" style="text-align:center">
      <div class="study-card-area">
        <div class="big-card" @click="flip">
          <div class="en">{{ current.english }}</div>
          <div class="ph">{{ current.sent }}</div>
          <div v-if="flipped" class="cn">{{ current.chinese }}</div>
          <div v-else class="hint">👆 点击查看释义</div>
        </div>
      </div>
      <div class="action-row">
        <button class="btn-act btn-know" @click="mark(1)">✅ 认识</button>
        <button class="btn-act btn-unk" @click="mark(3)">❌ 不认识</button>
      </div>
      <div class="nav-row">
        <span class="prog">{{ idx + 1 }} / {{ dueWords.length }}</span>
      </div>
    </div>

    <!-- 待确认（认识→斩） -->
    <div v-if="pendingReview.length > 0 && !current" class="card" style="margin-top:16px">
      <h3 style="margin-bottom:10px">📋 待确认 · {{ pendingReview.length }} 词</h3>
      <p style="font-size:14px;color:var(--dim);margin-bottom:14px">这些是你在背诵中点了「认识」的词，确认后计入掌握进度。</p>
      <div class="card-grid">
        <div class="word-card" v-for="w in pendingReview" :key="w.id">
          <div class="en">{{ w.english }}</div>
          <div class="ph">{{ w.sent }}</div>
          <div class="cn">{{ w.chinese }}</div>
          <button class="btn btn-purple btn-sm" style="margin-top:10px" @click="confirmPending(w)">✅ 确认掌握</button>
        </div>
      </div>
    </div>

    <!-- 不认识列表 -->
    <div v-if="wrongWords.length > 0 && !current" class="card" style="margin-top:16px">
      <h3 style="margin-bottom:10px">❌ 不认识 · {{ wrongWords.length }} 词</h3>
      <div style="margin-bottom:10px"><button class="btn btn-purple" @click="startReview(wrongWords)">复习这些</button></div>
      <div class="card-grid">
        <div class="word-card" v-for="w in wrongWords" :key="w.id">
          <div class="en">{{ w.english }}</div><div class="ph">{{ w.sent }}</div><div class="cn">{{ w.chinese }}</div>
          <button class="btn btn-sm" style="margin-top:8px" @click="unmark(w)">移出</button>
        </div>
      </div>
    </div>

    <!-- 收藏 -->
    <div v-if="favs.length > 0 && !current" class="card" style="margin-top:16px">
      <h3 style="margin-bottom:10px">⭐ 收藏 · {{ favs.length }} 词</h3>
      <div class="card-grid">
        <div class="word-card" v-for="w in favs" :key="w.id">
          <div class="en">{{ w.english }}</div><div class="ph">{{ w.sent }}</div><div class="cn">{{ w.chinese }}</div>
          <button class="btn btn-sm" style="margin-top:8px" @click="unfav(w)">取消</button>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api'

const dueWords = ref([])
const wrongWords = ref([])
const favs = ref([])
const pendingReview = ref([])
const idx = ref(0)
const flipped = ref(false)
const current = ref(null)
const loading = ref(true)
const wordRetries = ref({})
const pendingUnknown = ref(false)
const cardTick = ref(0)
const streak = ref(0)
const bestStreak = ref(0)
const praiseMsg = ref('')
const confettiPieces = ref([])

const PRAISE_POOL = {
  5: [
    '连续 5 个！太稳了 🔥',
    '五连击！状态来了 ⚡',
    '5 连对，复习机器！🤖',
    '第五个！手感火热 🌟',
    '连对 5 题，继续保持 💪',
  ],
  10: [
    '连对 10 题！神了 🌟',
    '十连击！无人能挡 🏆',
    '10 连对，词汇大师 👑',
    '双倍五连！太强了 🔥',
    '十题全对，飘起来了 ✨',
  ],
  15: [
    '15 连对！学霸模式 📚',
    '十五连击！炉火纯青 💎',
    '三连五！已经无敌 🚀',
    '15 题连对，神之一手 🧠',
    '复习达人认证 ✅',
  ],
  20: [
    '20 连对！传说级 🏅',
    '二十连击！全服第一 🥇',
    '满分节奏，停不下来 🎊',
    '20 题！你就是词汇之神 👑',
    '封神现场！20 连对 🔥',
  ],
}

const GENERAL_PRAISE = [
  '真棒！✨', '厉害！💪', '完美！💎', '轻松！😎',
  '天才！🧠', '无敌！🏆', '稳！🎯', '太强了！🌈',
]

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
  dueWords.value = [...words]
  wordRetries.value = {}
  streak.value = 0
  bestStreak.value = 0
  praiseMsg.value = ''
  confettiPieces.value = []
  idx.value = 0
  flipped.value = false
  pendingUnknown.value = false
  current.value = dueWords.value[0]
  if (current.value) speak(current.value.english)
}

function bumpCard() {
  cardTick.value++
}

function showCurrent() {
  flipped.value = false
  pendingUnknown.value = false
  current.value = dueWords.value[idx.value] ?? null
  if (current.value) nextTick(() => speak(current.value.english))
}

function requeueCurrent() {
  const w = dueWords.value.splice(idx.value, 1)[0]
  dueWords.value.push(w)
  if (idx.value >= dueWords.value.length) idx.value = dueWords.value.length - 1
}

function removeCurrent() {
  const id = current.value?.id
  dueWords.value.splice(idx.value, 1)
  if (id) delete wordRetries.value[id]
  if (dueWords.value.length === 0) {
    current.value = null
    return
  }
  if (idx.value >= dueWords.value.length) idx.value = dueWords.value.length - 1
}

function retryHint() {
  const n = wordRetries.value[current.value?.id]
  if (!n) return ''
  return `还需认识 ${n} 次才能过关`
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function showPraise(msg) {
  praiseMsg.value = msg
  const p = []
  for (let i = 0; i < 10; i++) {
    p.push({ id: Date.now() + i, x: Math.random() * 100, e: ['🌟', '✨', '💫', '🎉', '💖', '🔥', '⭐'][i % 7] })
  }
  confettiPieces.value = p
  setTimeout(() => { praiseMsg.value = ''; confettiPieces.value = [] }, 800)
}

function checkStreakPraise() {
  const s = streak.value
  if (PRAISE_POOL[s]) showPraise(pickRandom(PRAISE_POOL[s]))
  else if (s > 20 && s % 5 === 0) showPraise(pickRandom(GENERAL_PRAISE))
}

function onCorrectAnswer() {
  streak.value++
  if (streak.value > bestStreak.value) bestStreak.value = streak.value
  checkStreakPraise()
}

function resetStreak() {
  streak.value = 0
}

function markKnow() {
  if (!current.value || pendingUnknown.value) return
  onCorrectAnswer()
  const id = current.value.id
  const left = wordRetries.value[id]

  if (left != null && left > 0) {
    wordRetries.value[id] = left - 1
    api.markProgress(id, 2)
    if (wordRetries.value[id] > 0) {
      bumpCard()
      requeueCurrent()
      showCurrent()
      return
    }
  }

  api.markProgress(id, 1)
  bumpCard()
  removeCurrent()
  showCurrent()
}

function markUnknown() {
  if (!current.value || pendingUnknown.value) return
  resetStreak()
  flipped.value = true
  pendingUnknown.value = true
}

function advanceAfterUnknown() {
  if (!pendingUnknown.value || !current.value) return
  resetStreak()
  const id = current.value.id
  wordRetries.value[id] = 2
  api.markProgress(id, 3)
  bumpCard()
  requeueCurrent()
  showCurrent()
}

function flip() {
  if (pendingUnknown.value) {
    advanceAfterUnknown()
    return
  }
  flipped.value = !flipped.value
  if (flipped.value) speak(current.value.english)
}

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
    <div class="card" v-if="dueWords.length > 0 && !current">
      <h3 style="margin-bottom:10px">📅 今日待复习 (艾宾浩斯) · {{ dueWords.length }} 词</h3>
      <button class="btn btn-purple" @click="startReview(dueWords)">开始复习</button>
    </div>
    <div class="card" v-else-if="dueWords.length === 0 && !current">
      <p style="color:var(--dim)">✅ 今日无到期复习，干得漂亮！</p>
    </div>

    <div v-if="current" style="text-align:center">
      <div class="card-stage review-stage">
        <Transition name="fade" mode="out-in">
          <div
            :key="current.id + '-' + idx + '-' + cardTick"
            class="word-card-wrap"
            @click="flip"
          >
            <div class="big-card" :class="{ revealed: flipped || pendingUnknown }">
              <div class="en">{{ current.english }}</div>
              <div class="ph">{{ current.sent }}</div>
              <div v-if="flipped || pendingUnknown" class="cn">{{ current.chinese }}</div>
              <div v-else class="hint">👆 点击查看释义</div>
              <div v-if="(flipped || pendingUnknown) && wordRetries[current.id]" class="retry-badge">{{ retryHint() }}</div>
              <div v-else-if="pendingUnknown" class="retry-badge warn">再看一遍，待会儿还要出现 2 次</div>
            </div>
          </div>
        </Transition>
      </div>

      <div v-if="!pendingUnknown" class="action-row">
        <button class="btn-act btn-know" @click="markKnow">✅ 认识</button>
        <button class="btn-act btn-unk" @click="markUnknown">❌ 不认识</button>
      </div>
      <div v-else class="action-row">
        <button class="btn-act btn-next" @click="advanceAfterUnknown">👉 记住了，下一个</button>
      </div>

      <div class="nav-row">
        <span class="prog">{{ idx + 1 }} / {{ dueWords.length }}</span>
        <span v-if="streak >= 2" class="retry-hint">🔥 {{ streak }} 连对</span>
        <span v-if="wordRetries[current.id]" class="retry-hint">{{ retryHint() }}</span>
      </div>

      <div v-if="praiseMsg" class="praise">{{ praiseMsg }}</div>
      <div v-for="c in confettiPieces" :key="c.id" class="confetti" :style="{ left: c.x + '%', top: (Math.random() * 20) + '%' }">{{ c.e }}</div>
    </div>

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

    <div v-if="wrongWords.length > 0 && !current" class="card" style="margin-top:16px">
      <h3 style="margin-bottom:10px">❌ 不认识 · {{ wrongWords.length }} 词</h3>
      <div style="margin-bottom:10px"><button class="btn btn-purple" @click="startReview(wrongWords)">复习这些</button></div>
      <div class="card-grid">
        <div class="word-card" v-for="w in wrongWords" :key="w.id">
          <div class="en">{{ w.english }}</div>
          <div class="ph">{{ w.sent }}</div>
          <div class="cn">{{ w.chinese }}</div>
          <button class="btn btn-sm" style="margin-top:8px" @click="unmark(w)">移出</button>
        </div>
      </div>
    </div>

    <div v-if="favs.length > 0 && !current" class="card" style="margin-top:16px">
      <h3 style="margin-bottom:10px">⭐ 收藏 · {{ favs.length }} 词</h3>
      <div class="card-grid">
        <div class="word-card" v-for="w in favs" :key="w.id">
          <div class="en">{{ w.english }}</div>
          <div class="ph">{{ w.sent }}</div>
          <div class="cn">{{ w.chinese }}</div>
          <button class="btn btn-sm" style="margin-top:8px" @click="unfav(w)">取消</button>
        </div>
      </div>
    </div>
  </template>
</template>

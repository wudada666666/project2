<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../api'

const phase = ref('welcome')
const targetCount = ref(20)
const queue = ref([])          // 待背词队列（不认识会追加回来）
const originalIds = ref(new Set())  // 本轮原始 20 词的 id
const idx = ref(0)
const flipped = ref(false)
const current = ref(null)

const correctCount = ref(0)
const wrongCount = ref(0)
const streak = ref(0)
const bestStreak = ref(0)
const timerSec = ref(0)
let timer = null
let lastWasWrong = false
const repeatCount = ref({})  // 每个词重复次数

const lastSession = ref(null)
const totalStats = ref(null)
const praiseMsg = ref('')
const confettiPieces = ref([])
const totalMastered = ref(0)
const pendingUnknown = ref(false)

// ── TTS 发音 ──
function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'en-US'
  u.rate = 0.85
  u.pitch = 1
  speechSynthesis.speak(u)
}

// ── 音效 ──
let audioCtx = null
function getAudioCtx() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); return audioCtx }
function beep(freq, dur, type = 'sine') {
  try {
    const ctx = getAudioCtx()
    const o = ctx.createOscillator()
    const g = ctx.createGain()
    o.type = type; o.frequency.value = freq
    g.gain.setValueAtTime(0.3, ctx.currentTime)
    g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + dur)
    o.connect(g); g.connect(ctx.destination)
    o.start(); o.stop(ctx.currentTime + dur)
  } catch {}
}
function soundCorrect() { beep(880, 0.12); setTimeout(() => beep(1100, 0.15), 120) }
function soundWrong() { beep(200, 0.3, 'sawtooth') }

// ── 初始化 ──
onMounted(async () => {
  try { const { data } = await api.lastSession(); lastSession.value = data } catch {}
  try { const { data } = await api.totalStats(); totalStats.value = data } catch {}
  try { const { data } = await api.getStats(); totalMastered.value = data.mastered } catch {}
})
onUnmounted(() => clearInterval(timer))

function startTimer() { timerSec.value = 0; clearInterval(timer); timer = setInterval(() => timerSec.value++, 1000) }

async function startStudy() {
  const { data } = await api.getRandomWords(targetCount.value)
  queue.value = data
  originalIds.value = new Set(data.map(w => w.id))
  repeatCount.value = {}
  idx.value = 0; correctCount.value = 0; wrongCount.value = 0
  streak.value = 0; bestStreak.value = 0; flipped.value = false
  phase.value = 'studying'; current.value = queue.value[0]
  startTimer()
  nextTick(() => speak(current.value.english))
}

// ── 认识：从队列移除，标记待复习（status=2），不计入掌握进度 ──
function markKnow() {
  if (!current.value) return
  soundCorrect()
  correctCount.value++
  streak.value++
  if (streak.value > bestStreak.value) bestStreak.value = streak.value
  if (streak.value === 5) showPraise('连续 5 个！太强了 🔥')
  else if (streak.value === 10) showPraise('连对 10 题！神挡神 🌟')
  else if (streak.value >= 15 && streak.value % 5 === 0) showPraise(getRandomPraise())
  lastWasWrong = false
  api.markProgress(current.value.id, 2)  // status=2: 待复习（认识）

  // 从队列中移除
  queue.value.splice(idx.value, 1)
  if (queue.value.length === 0) { finishSession(); return }
  if (idx.value >= queue.value.length) idx.value = queue.value.length - 1
  flipped.value = false
  current.value = queue.value[idx.value]
  nextTick(() => speak(current.value.english))
}

// ── 斩!：立即掌握（status=1），计入进度 ──
function markMastered() {
  if (!current.value) return
  soundCorrect()
  correctCount.value++
  totalMastered.value++  // 总掌握数立即 +1
  streak.value++
  if (streak.value > bestStreak.value) bestStreak.value = streak.value
  if (streak.value === 5) showPraise('连斩 5 词！🔥')
  else if (streak.value === 10) showPraise('十连斩！无人能挡 🌟')
  else if (streak.value >= 15 && streak.value % 5 === 0) showPraise(getRandomPraise())
  lastWasWrong = false
  api.markProgress(current.value.id, 1)

  queue.value.splice(idx.value, 1)
  if (queue.value.length === 0) { finishSession(); return }
  if (idx.value >= queue.value.length) idx.value = queue.value.length - 1
  flipped.value = false
  current.value = queue.value[idx.value]
  nextTick(() => speak(current.value.english))
}

// ── 不认识：先展示释义，再点才翻到下一词 ──
function markUnknown() {
  if (!current.value || pendingUnknown.value) return
  soundWrong()
  lastWasWrong = true
  streak.value = 0
  flipped.value = true           // 显示中文释义
  pendingUnknown.value = true    // 进入「待翻页」状态
}

function advanceAfterUnknown() {
  if (!pendingUnknown.value || !current.value) return
  pendingUnknown.value = false
  wrongCount.value++
  api.markProgress(current.value.id, 3)

  const wid = current.value.id
  repeatCount.value[wid] = (repeatCount.value[wid] || 0) + 1
  if (repeatCount.value[wid] < 3) {
    queue.value.push(current.value)
  }

  queue.value.splice(idx.value, 1)
  if (queue.value.length === 0) { finishSession(); return }
  if (idx.value >= queue.value.length) idx.value = queue.value.length - 1
  flipped.value = false
  current.value = queue.value[idx.value]
  nextTick(() => speak(current.value.english))
}

function flip() {
  if (pendingUnknown.value) { advanceAfterUnknown(); return }
  flipped.value = !flipped.value
  if (flipped.value) speak(current.value.english)
}

function goPrev() { if (idx.value > 0) { idx.value--; flipped.value = false; lastWasWrong = false; current.value = queue.value[idx.value]; speak(current.value.english) } }
function goNext() { if (idx.value < queue.value.length - 1) { idx.value++; flipped.value = false; lastWasWrong = false; current.value = queue.value[idx.value]; speak(current.value.english) } }

// 触屏滑动
let touchX = 0
function onTouchStart(e) { touchX = e.touches[0].clientX }
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - touchX
  if (Math.abs(dx) > 60) { if (dx < 0) goNext(); else goPrev() }
}

function finishSession() {
  clearInterval(timer)
  phase.value = 'finished'
  const total = correctCount.value + wrongCount.value
  if (timerSec.value > 0 && total > 0) {
    api.saveSession(total, correctCount.value, wrongCount.value, timerSec.value)
    api.lastSession().then(({ data }) => { lastSession.value = data })
    api.totalStats().then(({ data }) => { totalStats.value = data })
  }
  if (correctCount.value >= total * 0.8) showBigCelebration()
}

function getRandomPraise() { return ['真棒！✨','厉害！💪','完美！💎','轻松！😎','天才！🧠','无敌！🏆'][Math.floor(Math.random()*6)] }
function showPraise(msg) { praiseMsg.value = msg; const p = []; for (let i = 0; i < 10; i++) p.push({ id: Date.now()+i, x: Math.random()*100, e: ['🌟','✨','💫','🎉','💖','🔥','⭐'][i%7] }); confettiPieces.value = p; setTimeout(() => { praiseMsg.value=''; confettiPieces.value=[] }, 800) }
function showBigCelebration() { const p=[]; for(let i=0;i<25;i++)p.push({id:Date.now()+i,x:Math.random()*100,e:['🎉','🎊','🏆','💎','🌟','✨','💖','🔥','👏','🥇'][i%10]});confettiPieces.value=p;setTimeout(()=>confettiPieces.value=[],1200) }
function again() { phase.value = 'welcome' }
</script>

<template>
  <!-- ── 欢迎 ── -->
  <div v-if="phase==='welcome'" class="welcome">
    <div class="hero">📚</div>
    <h1>Ready to study?</h1>
    <p class="sub">背完就斩，不认识就再来 🔪</p>

    <div v-if="lastSession && lastSession.total > 0" class="last-box">
      <div class="st"><div class="v">{{ lastSession.total }}</div><div class="l">上次背词</div></div>
      <div class="st"><div class="v">{{ lastSession.accuracy }}%</div><div class="l">正确率</div></div>
      <div class="st"><div class="v">{{ Math.floor(lastSession.duration/60) }}分{{ lastSession.duration%60 }}秒</div><div class="l">用时</div></div>
    </div>
    <div v-else class="no-rec">第一次背词？加油！认识的点「斩」不认识会反复出现 🔄</div>

    <div v-if="totalStats && totalStats.total_words > 0" style="margin-bottom:18px;color:var(--dim);font-size:12px">
      累计 {{ totalStats.total_words }} 词 · 掌握 {{ totalStats.mastered }} 词 · {{ totalStats.sessions }} 次练习
    </div>

    <div class="setup-row">
      <label>本轮词量：</label>
      <select v-model="targetCount">
        <option :value="10">10 个</option>
        <option :value="20">20 个</option>
        <option :value="30">30 个</option>
        <option :value="50">50 个</option>
        <option :value="100">100 个</option>
      </select>
    </div>
    <button class="btn-start" @click="startStudy">🚀 开始背诵</button>
  </div>

  <!-- ── 背诵中 ── -->
  <div v-if="phase==='studying' && current" class="study-wrap">
    <div class="study-header">
      <div class="scoreboard">
        <div class="score good"><span class="icon">✅</span> {{ correctCount }}</div>
        <div class="score bad"><span class="icon">❌</span> {{ wrongCount }}</div>
        <div class="score streak"><span class="icon">🔥</span> {{ streak }}</div>
        <div class="score" style="color:var(--dim)"><span class="icon">📦</span> {{ queue.length }}</div>
        <div class="score" style="color:var(--purple)"><span class="icon">🏆</span> {{ totalMastered }}</div>
      </div>
      <div class="timer">⏱ {{ Math.floor(timerSec/60) }}:{{ String(timerSec%60).padStart(2,'0') }}</div>
    </div>

    <div class="card-stage">
      <Transition :name="lastWasWrong ? 'slide' : 'slide'" mode="out-in">
        <div class="big-card" :key="current.id + '-' + idx" @click="flip" @touchstart="onTouchStart" @touchend="onTouchEnd">
          <div class="en">{{ current.english }}</div>
          <div class="ph">{{ current.sent }}</div>
          <div v-if="flipped" class="cn">{{ current.chinese }}</div>
          <div v-else-if="pendingUnknown" class="cn">{{ current.chinese }}</div>
          <div v-else class="hint">👆 点击查释义 · 再点听发音</div>
        </div>
      </Transition>
    </div>

    <div v-if="!pendingUnknown" class="action-row">
      <button class="btn-act btn-know" @click="markKnow">🤔 认识</button>
      <button class="btn-act btn-chop" @click="markMastered">⚔️ 斩!</button>
      <button class="btn-act btn-unk" @click="markUnknown">❌ 不认识</button>
    </div>
    <div v-else class="action-row">
      <button class="btn-act btn-next" @click="advanceAfterUnknown">👉 下一个</button>
    </div>

    <div class="nav-row">
      <button @click="goPrev">◀ 上一词</button>
      <span class="prog">第 {{ idx + 1 }} / {{ queue.length }} 词</span>
      <button @click="goNext">下一词 ▶</button>
    </div>
    <div class="swipe-hint">← 滑动翻页 →</div>

    <div v-if="praiseMsg" class="praise">{{ praiseMsg }}</div>
    <div v-for="c in confettiPieces" :key="c.id" class="confetti" :style="{ left: c.x + '%', top: (Math.random()*20) + '%' }">{{ c.e }}</div>
  </div>

  <!-- ── 完成 ── -->
  <div v-if="phase==='finished'" class="finish">
    <h2>{{ correctCount >= (correctCount+wrongCount)*0.8 ? '🎉 太强了！' : correctCount >= (correctCount+wrongCount)*0.5 ? '👍 继续加油！' : '💪 别灰心，会进步的！' }}</h2>
    <div class="big-pct" :style="{ color: correctCount >= (correctCount+wrongCount)*0.8 ? 'var(--green)' : 'var(--purple)' }">
      {{ correctCount+wrongCount>0 ? Math.round(correctCount/(correctCount+wrongCount)*100) : 0 }}%
    </div>
    <p style="color:var(--dim);margin-bottom:18px">正确率</p>
    <div class="row">
      <div class="box"><div class="n">{{ correctCount+wrongCount }}</div><div class="l">总答题数</div></div>
      <div class="box"><div class="n" style="color:var(--green)">{{ correctCount }}</div><div class="l">正确</div></div>
      <div class="box"><div class="n" style="color:var(--red)">{{ wrongCount }}</div><div class="l">不认识</div></div>
      <div class="box"><div class="n" style="color:var(--coral)">{{ bestStreak }}</div><div class="l">最长连对</div></div>
      <div class="box"><div class="n">{{ Math.floor(timerSec/60) }}:{{ String(timerSec%60).padStart(2,'0') }}</div><div class="l">用时</div></div>
    </div>
    <button class="btn-start" @click="again">🔄 再来一轮</button>
  </div>
</template>

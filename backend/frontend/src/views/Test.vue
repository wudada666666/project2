<script setup>
import { ref, onMounted } from 'vue'
import api, { getDeepseekKey, setDeepseekKey } from '../api'

const mode = ref('choice')
const words = ref([])
const current = ref(null)
const idx = ref(0)
const result = ref('')

// Choice
const options = ref([])
const selected = ref(null)
const answered = ref(false)
const correctId = ref(null)

// Spell
const spellAnswer = ref('')
const spellFeedback = ref('')
const spellCorrect = ref(false)
const spellSubmitted = ref(false)

// Sentence
const sentenceText = ref('')
const aiLoading = ref(false)
const aiFeedback = ref('')
const deepseekKey = ref(getDeepseekKey())
const keySaved = ref(false)
const freeUses = ref(null)

function saveApiKey() {
  setDeepseekKey(deepseekKey.value)
  keySaved.value = true
  setTimeout(() => { keySaved.value = false }, 1500)
}

async function loadFreeUses() {
  try { const { data } = await api.getFreeUses(); freeUses.value = data } catch {}
}

onMounted(() => { loadWords(); loadFreeUses() })

async function loadWords() {
  const { data } = await api.getRandomWords(20)
  words.value = data
  idx.value = 0
  next()
}

async function next() {
  result.value = ''
  selected.value = null
  answered.value = false
  spellAnswer.value = ''
  spellFeedback.value = ''
  spellCorrect.value = false
  spellSubmitted.value = false
  sentenceText.value = ''
  aiFeedback.value = ''

  if (idx.value >= words.value.length) {
    await loadWords()
    return
  }
  current.value = words.value[idx.value]
  correctId.value = current.value.id

  const others = words.value.filter(w => w.id !== current.value.id).slice(0, 3)
  options.value = [...others, current.value].sort(() => Math.random() - 0.5)
}

function choose(opt) {
  if (answered.value) return
  selected.value = opt.id
  answered.value = true
  if (opt.id === correctId.value) {
    result.value = '✅ 正确！'
    api.markProgress(current.value.id, 1)
  } else {
    result.value = `❌ 错误！正确答案是: ${current.value.english}`
    api.markProgress(current.value.id, 3)
  }
}

async function submitSpell() {
  if (spellSubmitted.value) return
  spellSubmitted.value = true
  const { data } = await api.spellCheck(current.value.id, spellAnswer.value)
  spellFeedback.value = data.message
  spellCorrect.value = data.correct
  api.markProgress(current.value.id, data.correct ? 1 : 3)
}

async function submitSentence() {
  if (!sentenceText.value.trim()) return
  aiLoading.value = true
  aiFeedback.value = ''
  try {
    const { data } = await api.checkSentence(current.value.english, sentenceText.value)
    aiFeedback.value = data.feedback
    loadFreeUses()
  } catch (e) {
    aiFeedback.value = e.response?.data?.detail || 'AI 服务暂不可用'
  }
  aiLoading.value = false
}

async function nextQuestion() { idx.value++; await next() }
</script>

<template>
  <div class="test-page">
    <h1 class="page-title">📝 测验模式</h1>

    <div class="test-toolbar">
      <div class="mode-tabs">
        <button class="mode-tab" :class="mode==='choice'?'active':''" @click="mode='choice'">
          <span class="mode-icon">📋</span>
          <span>选择题</span>
        </button>
        <button class="mode-tab" :class="mode==='spell'?'active':''" @click="mode='spell'">
          <span class="mode-icon">✍️</span>
          <span>拼写测验</span>
        </button>
        <button class="mode-tab" :class="mode==='sentence'?'active':''" @click="mode='sentence'">
          <span class="mode-icon">💬</span>
          <span>造句检测</span>
        </button>
      </div>
      <button class="btn btn-outline btn-sm shuffle-btn" @click="loadWords">🔀 换一批</button>
    </div>

    <!-- 选择题 -->
    <div v-if="mode==='choice' && current" class="test-card">
      <div class="test-question">
        <span class="q-badge">选择题</span>
        <p class="q-text">{{ current.chinese }}</p>
      </div>
      <div class="test-options">
        <button v-for="o in options" :key="o.id" class="test-option"
          :class="{ correct: answered && o.id === correctId, wrong: answered && selected === o.id && o.id !== correctId }"
          @click="choose(o)">
          <span class="opt-letter">{{ 'ABCD'[options.indexOf(o)] }}</span>
          <span class="opt-text">{{ o.english }}</span>
          <span v-if="answered && o.id === correctId" class="opt-icon">✅</span>
          <span v-if="answered && selected === o.id && o.id !== correctId" class="opt-icon">❌</span>
        </button>
      </div>
      <div v-if="result" class="test-result" :class="result.includes('✅')?'correct':'wrong'">
        {{ result }}
      </div>
      <div v-if="answered" class="test-next">
        <button class="btn btn-primary" @click="nextQuestion">下一题 →</button>
      </div>
    </div>

    <!-- 拼写 -->
    <div v-if="mode==='spell' && current" class="test-card">
      <div class="test-question">
        <span class="q-badge">拼写测验</span>
        <p class="q-text">{{ current.chinese }}</p>
        <p class="q-phonetic">{{ current.sent }}</p>
      </div>
      <div class="spell-area">
        <input class="spell-input" v-model="spellAnswer" :disabled="spellSubmitted"
          placeholder="输入英文拼写…" @keydown.enter="submitSpell" />
        <div v-if="spellFeedback" class="spell-feedback" :class="spellCorrect?'correct':'wrong'">
          <span class="feedback-icon">{{ spellCorrect ? '✅' : '❌' }}</span>
          {{ spellFeedback }}
        </div>
      </div>
      <div class="test-next">
        <button v-if="!spellSubmitted" class="btn btn-primary" @click="submitSpell">提交答案</button>
        <button v-if="spellSubmitted" class="btn btn-primary" @click="nextQuestion">下一题 →</button>
      </div>
    </div>

    <!-- 造句 -->
    <div v-if="mode==='sentence' && current" class="test-card">
      <div class="api-key-box">
        <div v-if="freeUses && freeUses.remaining > 0" class="free-uses-info">
          🎁 免费额度：剩余 <strong>{{ freeUses.remaining }}</strong> / {{ freeUses.limit }} 次
        </div>
        <div v-else-if="freeUses && freeUses.remaining <= 0" class="free-uses-info exhausted">
          免费额度已用完，请填写自己的 API Key 继续使用
        </div>
        <label>🔑 DeepSeek API Key（造句检测专用，仅存本地浏览器）</label>
        <div class="api-key-row">
          <input v-model="deepseekKey" type="password" placeholder="sk-..." @change="saveApiKey" />
          <button class="btn btn-sm btn-purple" @click="saveApiKey">{{ keySaved ? '已保存 ✓' : '保存' }}</button>
        </div>
        <p class="api-key-hint">拼写测验为本地校验，不需要 API Key。造句检测调用 DeepSeek，注册即送 10 次免费额度。</p>
      </div>
      <div class="test-question">
        <span class="q-badge">造句检测</span>
        <p class="q-text">用 <strong class="highlight-word">{{ current.english }}</strong> 造句</p>
        <p class="q-phonetic">{{ current.chinese }}</p>
      </div>
      <div class="sentence-area">
        <textarea class="sentence-textarea" v-model="sentenceText" placeholder="输入英语句子…" rows="4"></textarea>
        <div class="sentence-actions">
          <button class="btn btn-primary" @click="submitSentence" :disabled="aiLoading">
            {{ aiLoading ? '⏳ AI 检测中…' : '🚀 提交检测' }}
          </button>
          <button class="btn btn-outline" @click="nextQuestion">跳过此词</button>
        </div>
      </div>
      <div v-if="aiFeedback" class="ai-feedback">
        <div class="ai-feedback-header">💡 AI 反馈</div>
        <div class="ai-feedback-body">{{ aiFeedback }}</div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!current" class="test-empty">
      <div class="empty-icon">📝</div>
      <h3>加载中…</h3>
    </div>
  </div>
</template>

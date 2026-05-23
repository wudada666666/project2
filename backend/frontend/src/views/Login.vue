<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { setAuth, getToken } from '../api'

const router = useRouter()
const tab = ref('login')
const username = ref('')
const password = ref('')
const captchaAnswer = ref('')
const captchaId = ref('')
const captchaQuestion = ref('')
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  if (getToken()) {
    router.replace('/')
    return
  }
  await refreshCaptcha()
})

async function refreshCaptcha() {
  try {
    const { data } = await api.getCaptcha()
    captchaId.value = data.captcha_id
    captchaQuestion.value = data.question
    captchaAnswer.value = ''
  } catch {
    error.value = '验证码加载失败'
  }
}

async function submit() {
  error.value = ''
  if (!username.value.trim() || !password.value || !captchaAnswer.value.trim()) {
    error.value = '请填写完整信息'
    return
  }
  loading.value = true
  const payload = {
    username: username.value.trim(),
    password: password.value,
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value.trim(),
  }
  try {
    const { data } = tab.value === 'login'
      ? await api.login(payload)
      : await api.register(payload)
    setAuth(data.token, data.username)
    router.replace('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
    await refreshCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>✨ CET-6 背词</h1>
      <p class="auth-sub">登录后开始学习，进度按账户保存</p>

      <div class="auth-tabs">
        <button :class="{ active: tab === 'login' }" @click="tab = 'login'">登录</button>
        <button :class="{ active: tab === 'register' }" @click="tab = 'register'">注册</button>
      </div>

      <div class="auth-form">
        <label>用户名</label>
        <input v-model="username" placeholder="3-20 位字母、数字或下划线" autocomplete="username" />

        <label>密码</label>
        <input v-model="password" type="password" placeholder="至少 6 位" autocomplete="current-password" />

        <label>验证码</label>
        <div class="captcha-row">
          <span class="captcha-q">{{ captchaQuestion }}</span>
          <input v-model="captchaAnswer" placeholder="计算结果" inputmode="numeric" @keydown.enter="submit" />
          <button type="button" class="btn btn-sm" @click="refreshCaptcha">换一题</button>
        </div>

        <p v-if="error" class="auth-error">{{ error }}</p>

        <button class="btn-start" :disabled="loading" @click="submit">
          {{ loading ? '处理中…' : (tab === 'login' ? '登录' : '注册') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page{min-height:80vh;display:flex;align-items:center;justify-content:center;padding:20px}
.auth-card{background:var(--card);border-radius:var(--radius);padding:36px 32px;box-shadow:var(--shadow-lg);width:100%;max-width:420px}
.auth-card h1{text-align:center;font-size:28px;margin-bottom:6px}
.auth-sub{text-align:center;color:var(--dim);font-size:14px;margin-bottom:24px}
.auth-tabs{display:flex;gap:8px;margin-bottom:22px;background:#f3f0ff;padding:4px;border-radius:14px}
.auth-tabs button{flex:1;border:none;background:transparent;padding:10px;border-radius:10px;font-weight:700;cursor:pointer;color:var(--dim)}
.auth-tabs button.active{background:#fff;color:var(--purple);box-shadow:var(--shadow)}
.auth-form label{display:block;font-size:13px;color:var(--dim);margin:12px 0 6px;font-weight:600}
.auth-form input{width:100%;padding:12px 14px;border:2px solid var(--border);border-radius:12px;font-size:15px;outline:none;background:var(--bg)}
.auth-form input:focus{border-color:var(--purple)}
.captcha-row{display:flex;align-items:center;gap:8px}
.captcha-q{min-width:100px;font-weight:800;font-size:18px;color:var(--purple);background:#f5f0ff;padding:10px 12px;border-radius:10px;text-align:center}
.captcha-row input{flex:1}
.auth-error{color:var(--red);font-size:14px;margin:12px 0 0;text-align:center}
.auth-card .btn-start{width:100%;margin-top:20px}
</style>

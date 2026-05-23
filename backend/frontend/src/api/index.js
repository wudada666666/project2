import axios from 'axios'

const api = axios.create({ baseURL: '' })

const TOKEN_KEY = 'cet6_token'
const USER_KEY = 'cet6_user'
const API_KEY_STORAGE = 'deepseek_api_key'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getUsername() {
  return localStorage.getItem(USER_KEY) || ''
}

export function getDeepseekKey() {
  return localStorage.getItem(API_KEY_STORAGE) || ''
}

export function setDeepseekKey(key) {
  if (key) localStorage.setItem(API_KEY_STORAGE, key.trim())
  else localStorage.removeItem(API_KEY_STORAGE)
}

export function setAuth(token, username) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, username)
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  const dsKey = getDeepseekKey()
  if (dsKey && config.url?.includes('/api/ai/')) {
    config.headers['X-DeepSeek-Key'] = dsKey
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/api/auth/')) {
      clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export default {
  getCaptcha() { return api.get('/api/auth/captcha') },
  register(data) { return api.post('/api/auth/register', data) },
  login(data) { return api.post('/api/auth/login', data) },
  me() { return api.get('/api/auth/me') },

  getWords(page = 1, size = 20) { return api.get('/api/words', { params: { page, size } }) },
  searchWords(q) { return api.get('/api/words/search', { params: { q } }) },
  getWord(id) { return api.get(`/api/words/${id}`) },
  getRandomWords(count = 20) { return api.get('/api/words/random', { params: { count } }) },
  getReviewDue() { return api.get('/api/words/review-due') },
  spellCheck(wordId, answer) { return api.post('/api/words/spell-check', null, { params: { word_id: wordId, answer } }) },
  markProgress(wordId, status) { return api.post('/api/progress/mark', { word_id: wordId, status }) },
  getPendingReview() { return api.get('/api/progress/pending-review') },
  confirmReview(wordId) { return api.post('/api/progress/confirm-review', { word_id: wordId }) },
  getStats() { return api.get('/api/progress/stats') },
  getWrongWords() { return api.get('/api/progress/wrong') },
  toggleFavorite(wordId, action = 'add') { return api.post('/api/progress/favorites', { word_id: wordId, action }) },
  getFavorites() { return api.get('/api/progress/favorites') },
  checkSentence(word, sentence) { return api.post('/api/ai/check-sentence', { word, sentence }) },
  getFreeUses() { return api.get('/api/ai/free-uses') },
  saveSession(total, correct, wrong, duration) { return api.post('/api/progress/session', { total, correct, wrong, duration }) },
  lastSession() { return api.get('/api/progress/session/last') },
  totalStats() { return api.get('/api/progress/session/total') },
}

import axios from 'axios'

const api = axios.create({ baseURL: '' })

export default {
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
  saveSession(total, correct, wrong, duration) { return api.post('/api/progress/session', { total, correct, wrong, duration }) },
  lastSession() { return api.get('/api/progress/session/last') },
  totalStats() { return api.get('/api/progress/session/total') },
}

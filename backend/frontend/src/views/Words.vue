<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'

const words = ref([])
const total = ref(0)
const page = ref(1)
const size = 20
const search = ref('')

async function load() {
  if (search.value) {
    const { data } = await api.searchWords(search.value)
    words.value = data
    total.value = data.length
  } else {
    const { data } = await api.getWords(page.value, size)
    words.value = data.items
    total.value = data.total
  }
}

function mark(w, status) {
  api.markProgress(w.id, status)
  w.ref = status
}
function fav(w) {
  api.toggleFavorite(w.id, 'add')
  w.fav = true
}

onMounted(load)
watch([search, page], load)

const totalPages = ref(0)
watch(total, t => { totalPages.value = Math.ceil(t / size) })
</script>

<template>
  <h1 class="page-title">📖 单词本</h1>

  <div class="toolbar">
    <div class="search-bar" style="flex: 1; margin-bottom: 0">
      <input v-model="search" placeholder="搜索英文或中文…" />
    </div>
    <span style="font-size:13px;color:var(--text-secondary)">正序 A-Z · {{ total }} 词</span>
  </div>

  <div class="card">
    <div class="table-wrap">
      <table>
        <thead><tr><th>#</th><th>英文</th><th>音标</th><th>中文释义</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="(w, i) in words" :key="w.id">
            <td>{{ (page - 1) * size + i + 1 }}</td>
            <td style="font-weight: 600">{{ w.english }}</td>
            <td style="font-family: Courier New,monospace;font-size:13px;color:var(--text-secondary)">{{ w.sent }}</td>
            <td style="font-size:13px;max-width:280px">{{ w.chinese }}</td>
            <td>
              <div class="btn-group">
                <button class="btn btn-success btn-sm" @click="mark(w, 1)">掌握</button>
                <button class="btn btn-purple btn-sm" @click="mark(w, 2)">待复习</button>
                <button class="btn btn-danger btn-sm" @click="mark(w, 3)">不认识</button>
                <button class="btn btn-outline btn-sm" @click="fav(w)">⭐</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="!search">
      <button @click="page--" :disabled="page<=1">上一页</button>
      <span>第 {{ page }} / {{ totalPages }} 页 (共 {{ total }} 词)</span>
      <button @click="page++" :disabled="page>=totalPages">下一页</button>
    </div>
  </div>
</template>

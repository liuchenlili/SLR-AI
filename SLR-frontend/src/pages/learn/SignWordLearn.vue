<template>
  <div class="word-learn-page">
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-header">
        <h3 class="search-title">手语词汇库</h3>
        <p class="search-subtitle">浏览学习丰富的手语词汇内容</p>
      </div>
      <div class="search-controls">
        <div class="search-input-wrapper">
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索手语词汇..."
            class="search-input"
            @keydown.enter="onSearch"
          />
          <button class="search-btn" @click="onSearch">
            🔍
          </button>
        </div>
        <button class="reset-btn" @click="reloadList">重置</button>
      </div>
    </div>

    <!-- 词汇卡片网格 -->
    <div class="words-grid" v-if="!loading && wordList.length > 0">
      <div 
        v-for="word in displayWords" 
        :key="word.id"
        class="word-card"
        @click="showDetail(word.id)"
      >
        <div class="video-wrapper">
          <video 
            :src="word.videoUrl" 
            class="word-video"
            muted
            @mouseenter="playVideo"
            @mouseleave="pauseVideo"
          />
          <div class="video-overlay">
            <span class="play-icon">▶️</span>
          </div>
        </div>
        <div class="word-content">
          <h4 class="word-title">{{ word.word }}</h4>
          <p class="word-meaning">{{ word.chineseMeaning }}</p>
          <p class="word-desc">{{ word.actionDesc }}</p>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && wordList.length === 0" class="empty-state">
      <span class="empty-icon">📚</span>
      <h3>暂无词汇</h3>
      <p>没有找到相关的手语词汇</p>
    </div>

    <!-- 分页 -->
    <div v-if="wordList.length > pageSize" class="pagination">
      <button 
        class="page-btn"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      <button 
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detailVisible" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ detailItem?.word }}</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        <div class="modal-body" v-if="detailItem">
          <div class="detail-video-wrapper">
            <video 
              :src="detailItem.videoUrl" 
              controls 
              class="detail-video"
              autoplay
            />
          </div>
          <div class="detail-info">
            <div class="info-item">
              <label class="info-label">中文释义</label>
              <p class="info-value">{{ detailItem.chineseMeaning }}</p>
            </div>
            <div class="info-item">
              <label class="info-label">动作说明</label>
              <p class="info-value">{{ detailItem.actionDesc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import { getById, listAll, search } from '@/api/signWordController.ts'

const keyword = ref('')
const wordList = ref<any[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const detailItem = ref<any>(null)
const currentPage = ref(1)
const pageSize = ref(12)

// 计算属性
const totalPages = computed(() => Math.ceil(wordList.value.length / pageSize.value))
const displayWords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return wordList.value.slice(start, end)
})

// 方法
const fetchList = async () => {
  loading.value = true
  try {
    const res = await listAll()
    wordList.value = res.data || []
    currentPage.value = 1
  } finally {
    loading.value = false
  }
}

const reloadList = async () => {
  keyword.value = ''
  await fetchList()
}

const onSearch = async () => {
  if (!keyword.value) return fetchList()
  loading.value = true
  try {
    const res = await search({ keyword: keyword.value })
    wordList.value = res.data || []
    currentPage.value = 1
    if (wordList.value.length === 0) {
      message.info('无相关结果')
    }
  } finally { 
    loading.value = false 
  }
}

const showDetail = async (id: number) => {
  loading.value = true
  try {
    const res = await getById({ id })
    detailItem.value = res.data || null
    detailVisible.value = true
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  detailVisible.value = false
  detailItem.value = null
}

const changePage = (page: number) => {
  currentPage.value = page
}

const playVideo = (event: Event) => {
  const video = event.target as HTMLVideoElement
  video.play()
}

const pauseVideo = (event: Event) => {
  const video = event.target as HTMLVideoElement
  video.pause()
  video.currentTime = 0
}

onMounted(fetchList)
</script>

<style scoped>
.word-learn-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #faf8f3 0%, #f5f1e8 100%);
  padding: 24px;
}

.search-section {
  background: white;
  border-radius: 20px;
  padding: 32px 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
  text-align: center;
}

.search-header {
  margin-bottom: 24px;
}

.search-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}

.search-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.search-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #faf8f3;
  border: 2px solid #e8e5dd;
  border-radius: 12px;
  padding: 0;
  transition: all 0.3s ease;
  min-width: 300px;
}

.search-input-wrapper:focus-within {
  border-color: #6a9f7a;
  background: white;
  box-shadow: 0 0 0 3px rgba(106, 159, 122, 0.1);
}

.search-input {
  flex: 1;
  height: 48px;
  border: none;
  background: transparent;
  padding: 0 16px;
  font-size: 16px;
  outline: none;
  color: #2c3e50;
}

.search-input::placeholder {
  color: #95a5a6;
}

.search-btn {
  height: 48px;
  width: 48px;
  border: none;
  background: #6a9f7a;
  color: white;
  border-radius: 0 10px 10px 0;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  background: #5a8a6a;
}

.reset-btn {
  height: 48px;
  padding: 0 20px;
  border: 2px solid #e8e5dd;
  background: white;
  color: #6c757d;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  border-color: #6a9f7a;
  color: #6a9f7a;
}

.words-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.word-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
  transition: all 0.3s ease;
  cursor: pointer;
}

.word-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: #6a9f7a;
}

.video-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f8f9fa;
  overflow: hidden;
}

.word-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.word-card:hover .word-video {
  transform: scale(1.05);
}

.video-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.word-card:hover .video-overlay {
  opacity: 1;
}

.play-icon {
  color: white;
  font-size: 16px;
}

.word-content {
  padding: 20px;
}

.word-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.word-meaning {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.word-desc {
  font-size: 13px;
  color: #95a5a6;
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e5dd;
  margin-bottom: 32px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f1f1;
  border-top: 4px solid #6a9f7a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #6a9f7a;
  font-weight: 500;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e5dd;
  margin-bottom: 32px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.empty-state h3 {
  font-size: 18px;
  color: #495057;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.empty-state p {
  font-size: 14px;
  color: #7f8c8d;
  margin: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
}

.page-btn {
  height: 40px;
  padding: 0 16px;
  border: 2px solid #e8e5dd;
  border-radius: 10px;
  background: white;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.page-btn:hover:not(:disabled) {
  border-color: #6a9f7a;
  color: #6a9f7a;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #7f8c8d;
  font-size: 14px;
  padding: 0 16px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 24px 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f1f1;
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f8f9fa;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 16px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #e9ecef;
  color: #495057;
}

.modal-body {
  padding: 0 24px 24px;
}

.detail-video-wrapper {
  margin-bottom: 24px;
}

.detail-video {
  width: 100%;
  max-height: 300px;
  border-radius: 12px;
}

.detail-item {
  margin-bottom: 20px;
}

.detail-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-value {
  color: #6c757d;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #6a9f7a;
}

@media (max-width: 768px) {
  .word-learn-page {
    padding: 16px;
  }
  
  .search-controls {
    flex-direction: column;
  }
  
  .search-input-wrapper {
    min-width: 100%;
  }
  
  .words-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .search-section {
    padding: 24px 20px;
  }
  
  .search-title {
    font-size: 24px;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

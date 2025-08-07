<template>
  <div class="practice-record-page">
    <div class="content-container">
      <!-- 页面头部 -->
      <div class="header-section">
        <h1 class="page-title">📊 练习记录</h1>
        <p class="page-subtitle">查看你的手语练习历史和AI评估建议</p>
      </div>

      <!-- 搜索区域 -->
      <div class="search-section">
        <div class="search-container">
          <div class="search-input-wrapper">
            <input
              v-model="searchParams.target_text"
              type="text"
              placeholder="搜索练习目标..."
              class="search-input"
              @keydown.enter="doSearch"
            />
            <button class="search-btn" @click="doSearch">
              🔍 搜索
            </button>
          </div>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="records-container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载练习记录中...</p>
        </div>

        <div v-else-if="dataList.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <div class="empty-text">还没有练习记录</div>
          <div class="empty-subtext">开始练习手语来创建你的第一个记录吧</div>
        </div>

        <div v-else class="records-grid">
          <div
            v-for="record in dataList"
            :key="record.id"
            class="record-card"
          >
            <div class="record-header">
              <div class="record-target">
                <span class="target-icon">🎯</span>
                <span class="target-text">{{ record.targetText }}</span>
              </div>
              <div class="record-time">
                {{ dayjs(record.createTime).format('MM-DD HH:mm') }}
              </div>
            </div>

            <div class="record-content">
              <!-- 视频区域 -->
              <div class="video-section">
                <video 
                  v-if="record.videoUrl"
                  :src="record.videoUrl" 
                  controls 
                  class="practice-video"
                  preload="metadata"
                />
                <div v-else class="no-video">
                  📹 暂无视频
                </div>
              </div>

              <!-- 预测结果 -->
              <div class="prediction-section">
                <div class="section-title">🤖 AI识别结果</div>
                <div class="prediction-list">
                  <div
                    v-for="(item, index) in formatPredict(record.predictJson)"
                    :key="index"
                    class="prediction-item"
                    :class="{ 'top-prediction': index === 0 }"
                  >
                    <span class="prediction-rank">{{ index + 1 }}</span>
                    <span class="prediction-label">{{ item.label }}</span>
                    <span class="prediction-confidence">{{ item.confidence }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="record-actions">
              <button 
                class="advice-btn"
                @click="showAdvice(record)"
              >
                💡 查看AI建议
              </button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="pagination.total > pagination.pageSize" class="pagination-container">
          <button 
            class="page-btn"
            :disabled="pagination.current === 1"
            @click="changePage(pagination.current - 1)"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ pagination.current }} 页，共 {{ Math.ceil(pagination.total / pagination.pageSize) }} 页
          </span>
          <button 
            class="page-btn"
            :disabled="pagination.current >= Math.ceil(pagination.total / pagination.pageSize)"
            @click="changePage(pagination.current + 1)"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- AI建议弹窗 -->
      <div v-if="adviceModalVisible" class="modal-overlay" @click="closeAdviceModal">
        <div class="advice-modal" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">💡 AI教学建议</h3>
            <button class="modal-close" @click="closeAdviceModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="advice-content" v-html="formatAdvice(currentAdvice)"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue'
import { listMyRecords, listRecordByPage } from '@/api/practiceController'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'

const dataList = ref<API.PracticeRecord[]>([])
const loading = ref(false)
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})
const loginUserStore = useLoginUserStore()
const searchParams = reactive<API.PracticeRecordQueryRequest>({
  current: 1,
  pageSize: 10,
  user_id: loginUserStore.loginUser.id,
  target_text: '',
})

const adviceModalVisible = ref(false)
const currentAdvice = ref('')

/** 格式化 AI建议，支持 markdown 或换行 */
function formatAdvice(text: string) {
  if (!text) return '暂无AI建议'
  return text
    .replace(/###\s*(.*)/g, '<div class="advice-heading">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^(.*)$/, '<p>$1</p>')
}

/** 格式化预测结果为对象数组 */
function formatPredict(json: string | undefined) {
  if (!json) return []
  try {
    const parsed = JSON.parse(json);

    // 检查results是否存在且为数组
    if (Array.isArray(parsed.results)) {
      return parsed.results.map((item: any, index: number) => {
        // 处理每个子数组 [label, confidence]
        const label = item[0] || `未知标签${index + 1}`;
        const confidence = item[1] || '0%';

        // 提取百分比数字部分并格式化
        const confidenceNumber = parseFloat(confidence.replace('%', ''));
        return {
          label,
          confidence: `${confidenceNumber.toFixed(1)}%`
        };
      });
    }
    // 如果没有results字段或格式不正确，返回空数组
    return [];
  } catch (error) {
    console.error('JSON解析错误:', error);
    return [];
  }
}

function showAdvice(record: any) {
  currentAdvice.value = record.aiAdvice || ''
  adviceModalVisible.value = true
}

function closeAdviceModal() {
  adviceModalVisible.value = false
  currentAdvice.value = ''
}

function changePage(page: number) {
  pagination.value.current = page
  fetchData()
}

async function doSearch() {
  pagination.value.current = 1
  await fetchData()
}

async function fetchData() {
  loading.value = true
  try {
    searchParams.current = pagination.value.current
    searchParams.pageSize = pagination.value.pageSize
    
    const res = await listRecordByPage({
      ...searchParams,
    })
    
    if (res.data.code === 0 && res.data.data) {
      dataList.value = res.data.data.records ?? []
      pagination.value.total = res.data.data.total ?? 0
    } else {
      message.error('获取练习记录失败')
    }
  } catch (error) {
    message.error('获取练习记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.practice-record-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #faf8f3 0%, #f5f1e8 100%);
  padding: 24px;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin: 0;
}

.search-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #faf8f3;
  border: 2px solid #e8e5dd;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  max-width: 400px;
  width: 100%;
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
  padding: 0 20px;
  border: none;
  background: #6a9f7a;
  color: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover {
  background: #5a8a6a;
}

.records-container {
  margin-bottom: 40px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e5dd;
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

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.empty-text {
  font-size: 18px;
  color: #495057;
  margin-bottom: 8px;
  font-weight: 500;
}

.empty-subtext {
  font-size: 14px;
  color: #7f8c8d;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.record-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
  overflow: hidden;
  transition: all 0.3s ease;
}

.record-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-color: #6a9f7a;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f1f1f1;
}

.record-target {
  display: flex;
  align-items: center;
  gap: 8px;
}

.target-icon {
  font-size: 16px;
}

.target-text {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.record-time {
  font-size: 12px;
  color: #7f8c8d;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
}

.record-content {
  padding: 20px;
}

.video-section {
  margin-bottom: 20px;
}

.practice-video {
  width: 100%;
  max-height: 200px;
  border-radius: 12px;
  background: #f8f9fa;
}

.no-video {
  height: 120px;
  background: #f8f9fa;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
  font-size: 14px;
}

.prediction-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.prediction-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prediction-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #faf8f3;
  border-radius: 8px;
  border: 1px solid #f0ede4;
  transition: all 0.3s ease;
}

.prediction-item.top-prediction {
  background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
  border-color: #6a9f7a;
}

.prediction-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #6a9f7a;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.top-prediction .prediction-rank {
  background: #27ae60;
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
}

.prediction-label {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

.prediction-confidence {
  font-size: 13px;
  font-weight: 600;
  color: #6a9f7a;
  background: white;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #e8e5dd;
}

.top-prediction .prediction-confidence {
  color: #27ae60;
  border-color: #27ae60;
}

.record-actions {
  padding: 16px 20px;
  border-top: 1px solid #f1f1f1;
  background: #fafafa;
}

.advice-btn {
  width: 100%;
  height: 40px;
  border: none;
  background: #6a9f7a;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.advice-btn:hover {
  background: #5a8a6a;
  transform: translateY(-1px);
}

.pagination-container {
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

.advice-modal {
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
  font-size: 20px;
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

.advice-content {
  color: #495057;
  line-height: 1.7;
  font-size: 15px;
}

.advice-content :deep(p) {
  margin-bottom: 12px;
}

.advice-content :deep(.advice-heading) {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 16px 0 8px;
  padding-left: 12px;
  border-left: 3px solid #6a9f7a;
}

.advice-content :deep(strong) {
  color: #2c3e50;
  font-weight: 600;
}

.advice-content :deep(em) {
  color: #6a9f7a;
  font-style: italic;
}

@media (max-width: 768px) {
  .practice-record-page {
    padding: 16px;
  }
  
  .records-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .search-section {
    padding: 20px;
  }
  
  .pagination-container {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

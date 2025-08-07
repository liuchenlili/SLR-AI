<template>
  <div class="ai-qna-page">
    <div class="content-container">
      <!-- 页面头部 -->
      <div class="header-section">
        <h1 class="page-title">🤖 AI手语助手</h1>
        <p class="page-subtitle">智能问答，专业解答手语学习相关问题</p>
      </div>

      <!-- 问答区域 -->
      <div class="qna-container">
        <!-- 问题输入区 -->
        <div class="question-section">
          <div class="input-container">
            <div class="input-label">💭 有什么手语问题想要咨询？</div>
            <textarea
              v-model="question"
              class="question-input"
              rows="4"
              placeholder="例如：&#10;• 团结手语怎么做？&#10;• 如何提高手语学习效率？&#10;• 手语表达中的面部表情有什么要求？"
              @keydown.enter.exact.prevent="handleAsk"
            />
            <div class="input-actions">
              <button 
                class="ask-btn" 
                :class="{ loading: loading }" 
                :disabled="!question || loading"
                @click="handleAsk"
              >
                <span v-if="!loading">✨ 提问</span>
                <span v-else>🤔 思考中...</span>
              </button>
              <button 
                v-if="question" 
                class="clear-btn" 
                @click="clearQuestion"
              >
                🗑️ 清空
              </button>
            </div>
          </div>
        </div>

        <!-- 回答展示区 -->
        <div v-if="answer" class="answer-section">
          <div class="answer-container">
            <div class="answer-header">
              <div class="answer-label">🎯 AI助手回答</div>
              <div class="answer-meta">刚刚回复</div>
            </div>
            <div class="answer-content" v-html="formatAnswer(answer)"></div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!answer && !loading" class="empty-state">
          <div class="empty-icon">💡</div>
          <div class="empty-text">还没有提问哦</div>
          <div class="empty-subtext">输入你的手语学习问题，AI助手会为你详细解答</div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-animation">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div class="loading-text">AI正在思考你的问题...</div>
          </div>
        </div>
      </div>

      <!-- 使用提示 -->
      <div class="tips-section">
        <div class="tips-header">💡 使用小贴士</div>
        <div class="tips-grid">
          <div class="tip-item">
            <div class="tip-icon">🎯</div>
            <div class="tip-content">
              <div class="tip-title">具体问题</div>
              <div class="tip-desc">描述越具体，回答越准确</div>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">📖</div>
            <div class="tip-content">
              <div class="tip-title">学习方法</div>
              <div class="tip-desc">可以询问手语学习技巧</div>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">🤝</div>
            <div class="tip-content">
              <div class="tip-title">动作指导</div>
              <div class="tip-desc">获取具体手语动作说明</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { askAi } from '@/api/practiceController'
import { message } from 'ant-design-vue'

const question = ref('')
const answer = ref('')
const loading = ref(false)

const handleAsk = async () => {
  if (!question.value.trim()) {
    message.warning('请输入问题')
    return
  }
  loading.value = true
  answer.value = ''
  try {
    const res = await askAi({ question: question.value })
    answer.value = res.data?.answer || res.data || 'AI未返回答复'
    message.success('已获取AI回答')
  } catch (e: any) {
    answer.value = e?.response?.data?.message || e.message || '提问失败'
    message.error('提问失败，请重试')
  } finally {
    loading.value = false
  }
}

const clearQuestion = () => {
  question.value = ''
  answer.value = ''
}

function formatAnswer(text: string) {
  if (!text) return ''
  return text
    .replace(/###\s*(.*)/g, '<div class="answer-heading">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^(.*)$/, '<p>$1</p>')
}
</script>

<style scoped>
.ai-qna-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #faf8f3 0%, #f5f1e8 100%);
  padding: 24px;
}

.content-container {
  max-width: 800px;
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
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
  margin-bottom: 0;
}

.qna-container {
  margin-bottom: 40px;
}

.question-section {
  margin-bottom: 32px;
}

.input-container {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
}

.input-label {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 16px;
}

.question-input {
  width: 100%;
  border: 2px solid #e8e5dd;
  border-radius: 12px;
  padding: 16px;
  font-size: 16px;
  line-height: 1.5;
  background: #faf8f3;
  transition: all 0.3s ease;
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

.question-input:focus {
  outline: none;
  border-color: #6a9f7a;
  background: white;
  box-shadow: 0 0 0 3px rgba(106, 159, 122, 0.1);
}

.question-input::placeholder {
  color: #95a5a6;
  line-height: 1.6;
}

.input-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  justify-content: flex-end;
}

.ask-btn, .clear-btn {
  height: 44px;
  padding: 0 20px;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.ask-btn {
  background: #6a9f7a;
  color: white;
}

.ask-btn:hover:not(:disabled) {
  background: #5a8a6a;
  transform: translateY(-1px);
}

.ask-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.ask-btn.loading {
  background: #5a8a6a;
}

.clear-btn {
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #e8e5dd;
}

.clear-btn:hover {
  background: #e9ecef;
  border-color: #d1c7b7;
}

.answer-section {
  margin-bottom: 32px;
}

.answer-container {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e5dd;
  border-left: 4px solid #6a9f7a;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f1f1;
}

.answer-label {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.answer-meta {
  font-size: 12px;
  color: #95a5a6;
}

.answer-content {
  color: #495057;
  line-height: 1.7;
  font-size: 15px;
}

.answer-content :deep(p) {
  margin-bottom: 12px;
}

.answer-content :deep(.answer-heading) {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 16px 0 8px;
  padding-left: 12px;
  border-left: 3px solid #6a9f7a;
}

.answer-content :deep(strong) {
  color: #2c3e50;
  font-weight: 600;
}

.answer-content :deep(em) {
  color: #6a9f7a;
  font-style: italic;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e5dd;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.7;
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
  line-height: 1.5;
}

.loading-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.loading-dots {
  display: flex;
  gap: 8px;
}

.loading-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6a9f7a;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

.loading-text {
  font-size: 16px;
  color: #6a9f7a;
  font-weight: 500;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.tips-section {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e5dd;
}

.tips-header {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #faf8f3;
  border-radius: 12px;
  border: 1px solid #f0ede4;
}

.tip-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.tip-desc {
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .ai-qna-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .input-container, .answer-container {
    padding: 20px;
  }
  
  .input-actions {
    flex-direction: column;
  }
  
  .ask-btn, .clear-btn {
    width: 100%;
    justify-content: center;
  }
  
  .tips-grid {
    grid-template-columns: 1fr;
  }
}
</style>

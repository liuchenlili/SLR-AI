<template>
  <div class="learn-page">
    <div class="page-header">
      <h1 class="page-title">手语学习</h1>
      <p class="page-subtitle">系统化学习手语知识，提升沟通技能</p>
    </div>

    <div class="learn-container">
      <div class="learn-tabs">
        <div class="tab-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-button"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <span class="tab-emoji">{{ tab.emoji }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <div class="tab-content">
          <div v-if="activeTab === 'vocab'" class="tab-panel">
            <SignWordLearn />
          </div>
          <div v-if="activeTab === 'ai'" class="tab-panel">
            <SignAiQna />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import SignWordLearn from './SignWordLearn.vue'
import SignAiQna from './SignAiQna.vue'

const activeTab = ref('vocab')

const tabs = ref([
  {
    key: 'vocab',
    label: '词汇学习',
    emoji: '📚'
  },
  {
    key: 'ai',
    label: 'AI问答',
    emoji: '🤖'
  }
])
</script>

<style scoped>
.learn-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  background: #fefefe;
  min-height: calc(100vh - 80px);
}

.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: #64748b;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
}

.learn-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
}

.tab-nav {
  display: flex;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  margin-right: 8px;
}

.tab-button:hover {
  color: #2c3e50;
  background: rgba(255, 255, 255, 0.5);
}

.tab-button.active {
  color: #2c3e50;
  background: white;
  border-bottom-color: #64748b;
}

.tab-emoji {
  font-size: 1rem;
}

.tab-label {
  font-weight: 500;
}

.tab-content {
  padding: 0;
}

.tab-panel {
  padding: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .learn-page {
    padding: 20px 16px;
  }

  .tab-nav {
    padding: 0 16px;
    flex-wrap: wrap;
  }

  .tab-button {
    flex: 1;
    justify-content: center;
    min-width: 120px;
  }

  .tab-panel {
    padding: 20px 16px;
  }
}
</style>

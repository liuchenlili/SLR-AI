<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            智能手语教学平台
          </h1>
          <p class="hero-description">
            基于深度学习的手语识别与教学系统，让沟通无障碍，让学习更轻松
          </p>
          <div class="hero-actions">
            <router-link to="/learn" class="btn-primary">开始学习</router-link>
            <router-link to="/real" class="btn-secondary">实时识别</router-link>
          </div>
        </div>
        <div class="hero-visual">
          <div class="visual-card">
            <div class="gesture-icon">👋</div>
            <p class="visual-text">用心连接无声世界</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-container">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.id">
            <div class="feature-header">
              <h3 class="feature-title">{{ feature.title }}</h3>
              <span class="feature-emoji">{{ feature.emoji }}</span>
            </div>
            <p class="feature-description">{{ feature.description }}</p>
            <router-link :to="feature.link" class="feature-link">
              前往体验
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Models Section -->
    <section class="models-section">
      <div class="section-container">
        <h2 class="section-title">支持的模型</h2>
        <div class="models-grid">
          <div class="model-card" v-for="model in models" :key="model.name">
            <div class="model-header">
              <h3 class="model-name">{{ model.name }}</h3>
              <span class="model-accuracy">准确率: {{ model.accuracy }}%</span>
            </div>
            <p class="model-description">{{ model.description }}</p>
            <div class="model-features">
              <span v-for="tag in model.tags" :key="tag" class="model-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
        <div class="models-action">
          <router-link to="/models" class="btn-outline">查看详细指标</router-link>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="section-container">
        <div class="stats-grid">
          <div class="stat-item" v-for="stat in stats" :key="stat.label">
            <div class="stat-number">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="section-container">
        <div class="cta-content">
          <h2 class="cta-title">开始你的手语学习之旅</h2>
          <p class="cta-description">
            无论你是初学者还是想要提升技能，我们的平台都能为你提供个性化的学习体验
          </p>
          <div class="cta-actions">
            <router-link to="/user/register" class="btn-primary">立即注册</router-link>
            <router-link to="/practice" class="btn-secondary">练习测试</router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const features = ref([
  {
    id: 1,
    emoji: '📚',
    title: '视频学习',
    description: '丰富的手语视频教程，从基础到进阶，系统化学习手语表达',
    link: '/learn'
  },
  {
    id: 2,
    emoji: '🎥',
    title: '实时识别',
    description: '基于AI的实时手语识别，即时反馈学习效果',
    link: '/real'
  },
  {
    id: 3,
    emoji: '🤖',
    title: '智能练习',
    description: '个性化练习方案，AI评估指导，提升学习效率',
    link: '/practice'
  },
  {
    id: 4,
    emoji: '📊',
    title: '学习分析',
    description: '详细的学习数据分析，追踪进步轨迹',
    link: '/practice/history'
  }
])

const models = ref([
  {
    name: 'SignFormer',
    accuracy: 95.2,
    description: '基于Transformer架构的手语识别模型，具有优秀的时序建模能力',
    tags: ['Transformer', '高精度', '实时']
  },
  {
    name: 'R(2+1)D',
    accuracy: 92.8,
    description: '3D CNN模型，擅长捕捉手语动作的空间-时间特征',
    tags: ['3D CNN', '稳定', '快速']
  },
  {
    name: 'LSTM',
    accuracy: 89.5,
    description: '长短期记忆网络，适合序列化手语动作识别',
    tags: ['RNN', '经典', '可靠']
  }
])

const stats = ref([
  { value: '1000+', label: '手语词汇' },
  { value: '95%+', label: '识别准确率' },
  { value: '500+', label: '注册用户' },
  { value: '24/7', label: '在线服务' }
])
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #fefcf8;
}

/* Hero Section */
.hero-section {
  padding: 80px 0 100px;
  background: linear-gradient(160deg, #fefcf8 0%, #f7f3eb 100%);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    /* 手势图案 - 使用Unicode手势符号创建重复背景 */
    radial-gradient(circle at 20% 20%, rgba(92, 127, 103, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(92, 127, 103, 0.02) 0%, transparent 50%),
    radial-gradient(circle at 40% 60%, rgba(92, 127, 103, 0.02) 0%, transparent 50%);
  background-size: 300px 300px, 400px 400px, 350px 350px;
  background-position: 0 0, 200px 100px, 100px 200px;
  z-index: 1;
}

.hero-section::after {
  content: '🤚 ✋ 👋 🤲 👍 🤞 ✌️ 🤟 🤙';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 3rem;
  color: rgba(92, 127, 103, 0.15);
  letter-spacing: 4rem;
  line-height: 5rem;
  text-align: center;
  white-space: nowrap;
  z-index: 1;
  animation: float 20s ease-in-out infinite;
  pointer-events: none;
  user-select: none;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 80px;
  position: relative;
  z-index: 2;
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: #2c2c2c;
  letter-spacing: -0.02em;
}

.hero-description {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2.5rem;
  line-height: 1.7;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn-primary {
  display: inline-block;
  padding: 14px 28px;
  background: #5c7f67;
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
  border: none;
  box-shadow: 0 2px 8px rgba(92, 127, 103, 0.15);
}

.btn-primary:hover {
  background: #4a6b54;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(92, 127, 103, 0.2);
  color: white;
}

.btn-secondary {
  display: inline-block;
  padding: 14px 28px;
  background: white;
  color: #5c7f67;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
  border: 1px solid #e5e5e5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  background: #f9f9f9;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  color: #5c7f67;
}

.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.visual-card {
  width: 280px;
  height: 280px;
  background: white;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.gesture-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  filter: grayscale(20%);
}

.visual-text {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
  font-weight: 500;
}

/* Features Section */
.features-section {
  padding: 100px 0;
  background: white;
  position: relative;
}

.features-section::before {
  content: '👌 🤏 ☝️ 👈 👉 👆 👇 ✊';
  position: absolute;
  top: 20%;
  right: 5%;
  font-size: 2rem;
  color: rgba(92, 127, 103, 0.08);
  letter-spacing: 2rem;
  line-height: 3rem;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  z-index: 1;
  pointer-events: none;
  user-select: none;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 2;
}

.section-title {
  text-align: center;
  font-size: 2.25rem;
  font-weight: 600;
  margin-bottom: 3rem;
  color: #2c2c2c;
  letter-spacing: -0.02em;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  padding: 32px 24px;
  border-radius: 16px;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #e5e5e5;
}

.feature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c2c2c;
  margin: 0;
}

.feature-emoji {
  font-size: 1.5rem;
  opacity: 0.8;
}

.feature-description {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  font-size: 0.95rem;
}

.feature-link {
  color: #5c7f67;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.feature-link:hover {
  color: #4a6b54;
}

/* Models Section */
.models-section {
  padding: 100px 0;
  background: #faf9f6;
  position: relative;
}

.models-section::before {
  content: '🤖 📊 🎯 ⚡ 🔍 📈';
  position: absolute;
  bottom: 10%;
  left: 5%;
  font-size: 1.8rem;
  color: rgba(92, 127, 103, 0.1);
  letter-spacing: 2rem;
  z-index: 1;
  pointer-events: none;
  user-select: none;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 3rem;
}

.model-card {
  background: white;
  padding: 32px;
  border-radius: 16px;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.model-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.model-name {
  font-size: 1.375rem;
  font-weight: 600;
  color: #2c2c2c;
  margin: 0;
}

.model-accuracy {
  background: #7bb3a0;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.model-description {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  font-size: 0.95rem;
}

.model-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.model-tag {
  background: #f3f6f4;
  color: #5c7f67;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.models-action {
  text-align: center;
}

.btn-outline {
  display: inline-block;
  padding: 14px 28px;
  background: transparent;
  color: #5c7f67;
  text-decoration: none;
  border-radius: 12px;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
  border: 1px solid #5c7f67;
}

.btn-outline:hover {
  background: #5c7f67;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(92, 127, 103, 0.2);
}

/* Stats Section */
.stats-section {
  padding: 80px 0;
  background: white;
  position: relative;
}

.stats-section::before {
  content: '📈 📊 💯 🏆';
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.5rem;
  color: rgba(92, 127, 103, 0.06);
  letter-spacing: 3rem;
  z-index: 1;
  pointer-events: none;
  user-select: none;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  text-align: center;
}

.stat-item {
  background: white;
  padding: 32px 24px;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #5c7f67;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.stat-label {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.95rem;
}

/* CTA Section */
.cta-section {
  padding: 100px 0;
  background: #faf9f6;
  position: relative;
}

.cta-section::before {
  content: '🚀 ✨ 🎯 💫';
  position: absolute;
  bottom: 20%;
  right: 10%;
  font-size: 1.6rem;
  color: rgba(92, 127, 103, 0.07);
  letter-spacing: 2rem;
  z-index: 1;
  pointer-events: none;
  user-select: none;
}

.cta-content {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.cta-title {
  font-size: 2.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #2c2c2c;
  letter-spacing: -0.02em;
}

.cta-description {
  font-size: 1.125rem;
  color: #6b7280;
  margin-bottom: 2.5rem;
  line-height: 1.7;
}

.cta-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 48px;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cta-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn-primary,
  .btn-secondary,
  .btn-outline {
    width: 100%;
    max-width: 280px;
  }
  
  .section-container {
    padding: 0 20px;
  }
}

@media (max-width: 480px) {
  .hero-content {
    padding: 0 20px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.875rem;
  }
  
  .cta-title {
    font-size: 1.875rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .visual-card {
    width: 240px;
    height: 240px;
  }
}

/* 手势浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translate(-50%, -50%) rotate(0deg);
    opacity: 0.15;
  }
  25% {
    transform: translate(-48%, -52%) rotate(2deg);
    opacity: 0.08;
  }
  50% {
    transform: translate(-52%, -48%) rotate(-2deg);
    opacity: 0.18;
  }
  75% {
    transform: translate(-48%, -52%) rotate(1deg);
    opacity: 0.1;
  }
}
</style>

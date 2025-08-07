

<template>
  <div class="realtime-page">
    <div class="page-header">
      <h1 class="page-title">实时手语识别</h1>
      <p class="page-subtitle">使用摄像头进行实时手语识别，即时获得反馈结果</p>
    </div>
    
    <div class="realtime-container">
      <div class="streamlit-wrapper">
        <iframe
          src="http://localhost:8501"
          class="streamlit-frame"
          frameborder="0">
        </iframe>
      </div>
    </div>
    
    <div class="help-section">
      <h3 class="help-title">使用说明</h3>
      <div class="help-content">
        <div class="help-item">
          <span class="help-icon">📹</span>
          <span class="help-text">确保摄像头权限已开启</span>
        </div>
        <div class="help-item">
          <span class="help-icon">💡</span>
          <span class="help-text">保持充足的光线环境</span>
        </div>
        <div class="help-item">
          <span class="help-icon">👋</span>
          <span class="help-text">手势清晰可见，动作标准</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">

</script>
<style scoped>
.realtime-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  background: #fefefe;
  min-height: calc(100vh - 80px);
}

.page-header {
  margin-bottom: 32px;
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

.realtime-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
  margin-bottom: 32px;
}

.streamlit-wrapper {
  position: relative;
  width: 100%;
  height: 800px;
}

.streamlit-frame {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 16px;
}

.help-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
}

.help-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-title::before {
  content: '💡';
  font-size: 1.2rem;
}

.help-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.help-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.help-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.help-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.help-text {
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .realtime-page {
    padding: 20px 16px;
  }
  
  .streamlit-wrapper {
    height: 600px;
  }
  
  .help-content {
    grid-template-columns: 1fr;
  }
}
</style>

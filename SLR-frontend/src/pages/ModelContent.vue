<template>
  <div class="main-content">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">模型性能指标</h1>
          <p class="page-subtitle">深度学习模型的训练结果与性能评估</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-value">{{ store.models.length }}</div>
            <div class="stat-label">可用模型</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">95%+</div>
            <div class="stat-label">平均准确率</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="panel-title">
        模型配置
      </div>
      <div class="control-grid">
        <div class="control-group">
          <label class="control-label">
            选择模型
          </label>
          <a-select
            v-model:value="store.selectedModel"
            :options="modelOptions"
            placeholder="请选择模型"
            class="control-select"
            size="large"
          />
        </div>
        <div class="control-group">
          <label class="control-label">
            选择权重
          </label>
          <a-select
            v-model:value="store.selectedWeight"
            :options="weightOptions"
            placeholder="请选择权重"
            class="control-select"
            size="large"
          />
        </div>
      </div>
    </div>

    <!-- 指标展示区域 -->
    <div class="metrics-container" v-if="store.selectedModel">
      <div class="metrics-header">
        <h2 class="metrics-title">
          {{ store.selectedModel }} 性能分析
        </h2>
        <div class="model-badge">{{ store.selectedWeight || '默认权重' }}</div>
      </div>

      <a-tabs
        v-if="!store.prediction"
        v-model:activeKey="activeKey"
        @change="handleTabChange"
        class="metrics-tabs"
        type="card"
      >
        <a-tab-pane key="acc" tab="准确率曲线">
          <div class="chart-wrapper">
            <div class="chart-header">
              <h3 class="chart-title">训练准确率变化</h3>
              <p class="chart-desc">模型在训练过程中的准确率提升曲线</p>
            </div>
            <div class="chart-container">
              <EchartLine
                ref="accLine"
                :data-url="`/python/metrics/acc?model=${encodeURIComponent(store.selectedModel)}`"
              />
            </div>
          </div>
        </a-tab-pane>
        <a-tab-pane key="loss" tab="损失曲线">
          <div class="chart-wrapper">
            <div class="chart-header">
              <h3 class="chart-title">训练损失变化</h3>
              <p class="chart-desc">模型训练过程中损失函数的收敛情况</p>
            </div>
            <div class="chart-container">
              <EchartLine
                ref="lossLine"
                :data-url="`/python/metrics/loss?model=${encodeURIComponent(store.selectedModel)}`"
              />
            </div>
          </div>
        </a-tab-pane>
        <a-tab-pane key="net" tab="网络结构">
          <div class="chart-wrapper">
            <div class="chart-header">
              <h3 class="chart-title">模型架构图</h3>
              <p class="chart-desc">神经网络的层次结构和连接关系</p>
            </div>
            <div class="network-container">
              <iframe class="net-frame" :srcdoc="netHtml" />
            </div>
          </div>
        </a-tab-pane>
        <a-tab-pane key="conf" tab="混淆矩阵">
          <div class="chart-wrapper">
            <div class="chart-header">
              <h3 class="chart-title">分类效果矩阵</h3>
              <p class="chart-desc">模型对各类别的识别准确性分析</p>
            </div>
            <div class="confusion-container">
              <img :src="confImage" class="conf-matrix" alt="混淆矩阵" />
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- 空状态 -->
    <div v-if="!store.selectedModel" class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">📋</div>
        <h3 class="empty-title">选择模型开始分析</h3>
        <p class="empty-desc">请在上方选择一个模型来查看其性能指标和分析结果</p>
      </div>
    </div>

    <!-- 识别结果 -->
    <div v-if="store.prediction" class="prediction-result">
      <div class="result-header">
        <h3 class="result-title">
          识别结果
        </h3>
        <div class="result-meta">识别时间: {{ new Date().toLocaleTimeString() }}</div>
      </div>
      <div class="result-grid">
        <div
          v-for="(item, index) in store.prediction.results"
          :key="index"
          class="result-card"
          :class="{ 'top-result': index === 0 }"
        >
          <div class="result-rank">{{ index + 1 }}</div>
          <div class="result-content">
            <a
              :href="`https://www.spreadthesign.com/zh.hans.cn/search/?q=${item[0]}`"
              target="_blank"
              class="result-link"
            >
              {{ item[0] }}
            </a>
            <div class="result-confidence">
              <span class="confidence-label">置信度</span>
              <div class="confidence-bar">
                <div
                  class="confidence-fill"
                  :style="{ width: `${parseFloat(item[1]) * 100}%` }"
                ></div>
              </div>
              <span class="confidence-value">{{ (parseFloat(item[1]) * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick, computed } from 'vue'

import EchartLine from '@/components/EchartLine.vue'
import { getNetworkGraph, getConfusionMatrix, predict } from '@/api/predictionController.ts'
import { message } from 'ant-design-vue'
import router from '@/router'
import { useConfigStore } from '@/stores/cslConfig.ts'

const store = useConfigStore()
const netHtml = ref('')
const confImage = ref('')
const loading = ref(false)
const activeKey = ref('acc')
const accLine = ref()
const lossLine = ref()
let stream: MediaStream | null = null
let recorder: MediaRecorder | null = null
const fps = ref(0)
let lastTime = Date.now()
const recordedChunks = ref<Blob[]>([])
const recording = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)

watch(() => store.realtimeFrame, () => {
  // 计算FPS
  const now = Date.now()
  fps.value = 1000 / (now - lastTime)
  lastTime = now
})
// 自动监听模型变化，加载权重并默认选中第一个权重
const fetchWeights = async () => {
  await store.fetchWeights()
}
watch(
  () => store.selectedModel,
  async (val) => {
    if (val) {
      await fetchWeights()
      store.selectedWeight = store.weights[0] || ''
    }
  },
  { immediate: true },
)
const fpsText = computed(() => store.isRealtime && fps.value > 0 ? fps.value.toFixed(1) + ' Vid/s' : '')
const fetchData = async () => {
  if (!store.selectedModel) return
  const netRes = await getNetworkGraph({ model: store.selectedModel })
  netHtml.value = netRes.data
  const imgRes = await getConfusionMatrix({ model: store.selectedModel })
  confImage.value = imgRes.data
}
watch(() => store.selectedModel, val => {
  store.setPrediction(null)     // 清空预测结果
  fetchData()                   // 原有fetchData不变
}, { immediate: true })


function handleTabChange(key: string) {
  nextTick(() => {
    if (key === 'acc' && accLine.value?.resize) accLine.value.resize()
    if (key === 'loss' && lossLine.value?.resize) lossLine.value.resize()
  })
}
const handleClearPrediction = () => {
  store.setPrediction(null)

}

// 点击识别
const handlePredict = async () => {
  if (
    !store.selectedModel ||
    !store.selectedWeight ||
    (store.selectedVideoStyle === '上传视频' && !store.uploadedVideo) ||
    (store.selectedVideoStyle === '录制视频' && !store.recordedVideo) ||
    (store.selectedVideoStyle === 'CSL测试集' && !store.selectedCSLVideo)
  ) {
    message.warning('请配置模型、权重和视频')
    return
  }

  loading.value = true
  try {
    let res
    if (store.selectedVideoStyle === 'CSL测试集') {
      // 传递测试视频路径
      res = await predict({
        model: store.selectedModel,
        weight: store.selectedWeight,
        videoStyle: 'CSL测试集',
        centercrop: false,
        videoPath: `data/ptov/${store.selectedCSLVideo}`,
      })
      console.log(res.data)
    } else if (store.selectedVideoStyle === '上传视频') {
      // 上传视频
      res = await predict(
        {
          model: store.selectedModel,
          weight: store.selectedWeight,
          videoStyle: store.selectedVideoStyle,
          centercrop: false,
        },
        store.uploadedVideo,
      )
      console.log(res.data)
    } else if (store.selectedVideoStyle === '录制视频') {
      res = await predict(
        {
          model: store.selectedModel,
          weight: store.selectedWeight,
          videoStyle: '录制视频',
          centercrop: false,
        },
        store.recordedVideo,
      )
      console.log(res.data)
    }
    store.setPrediction(res.data)
    message.success('识别完成')
  } catch (e) {
    message.error('识别失败，请检查配置')
  } finally {
    loading.value = false
  }
}
const modelOptions = computed(() =>
  store.models.map((model) => ({ value: model, label: model })),
)
const weightOptions = computed(() =>
  store.weights.map((weight) => ({ value: weight, label: weight })),
)
const videoStyleOptions = computed(() =>
  store.videoStyles.map((style) => ({ value: style, label: style })),
)
const cslVideoOptions = computed(() =>
  store.cslVideos.map((video) => ({ value: video, label: video })),
)

const handleUpload = async ({ file }: { file: File }) => {
  store.setUploadedVideo(file)
}
const videoPreviewUrl = computed(() => {
  if (store.selectedVideoStyle === '上传视频' && store.uploadedVideo) {
    return URL.createObjectURL(store.uploadedVideo)
  }
  if (store.selectedVideoStyle === 'CSL测试集' && store.selectedCSLVideo) {
    return `/data/ptov/${store.selectedCSLVideo}`
  }
  return ''
})
// ============= 录制相关 =============
const startRecording = async () => {
  stream = await navigator.mediaDevices.getUserMedia({ video: true })
  if (videoRef.value) videoRef.value.srcObject = stream
  recorder = new MediaRecorder(stream, { mimeType: 'video/webm' }) // webm格式
  recordedChunks.value = []
  recording.value = true
  recorder.ondataavailable = (e: BlobEvent) => recordedChunks.value.push(e.data)
  recorder.onstop = () => {
    recording.value = false
    if (stream) stream.getTracks().forEach((track) => track.stop())
    const blob = new Blob(recordedChunks.value, { type: 'video/webm' })
    if (blob.size < 1024) {
      message.error('录制失败，文件为空')
      return
    }
    store.setRecordedVideo(new File([blob], 'recorded.webm', { type: 'video/webm' }))
  }
  recorder.start()
  message.success('开始录制')
}

const stopRecording = () => {
  if (recorder && recording.value) {
    recorder.stop()
    message.success('录制结束')
  }
}

const startRealtime = () => {
  // 检查模型和权重是否已选择
  if (!store.selectedModel || !store.selectedWeight) {
    message.warning('请先选择模型和权重')
    return
  }
  message.success('进入实时识别')
  // 切换到实时识别模式
  store.selectedVideoStyle = '实时识别'
  router.push({
    path: '/',
  })
}
const stopRealtime = () => {

  store.selectedVideoStyle = '';
  message.success('已退出实时识别');
}
</script>

<style scoped>
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  background: #fafafa;
  min-height: calc(100vh - 80px);
}

/* 页面头部 */
.page-header {
  margin-bottom: 32px;
  background: white;
  border-radius: 12px;
  padding: 32px;
  border: 1px solid #e5e5e5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 2.2rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #2c3e50;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 1rem;
  color: #6c757d;
  margin: 0;
  line-height: 1.6;
}

.header-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 100px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
  color: #495057;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

/* 控制面板 */
.control-panel {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e5e5;
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 1.2rem;
}

.control-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: #555;
  display: flex;
  align-items: center;
  gap: 6px;
}

.label-icon {
  font-size: 1rem;
}

.control-select {
  border-radius: 12px !important;
  border: 2px solid #e5e5e5 !important;
  font-size: 0.95rem !important;
}

.control-select:hover {
  border-color: #6c757d !important;
}

.control-select:focus {
  border-color: #495057 !important;
  box-shadow: 0 0 0 3px rgba(73, 80, 87, 0.1) !important;
}

/* 指标容器 */
.metrics-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e5e5;
  margin-bottom: 32px;
}

.metrics-header {
  padding: 24px 32px;
  background: #f8f9fa;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metrics-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-badge {
  background: #6c757d;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* 标签页样式 */
.metrics-tabs :deep(.ant-tabs-nav) {
  background: transparent;
  margin: 0 24px;
  padding: 0;
  border-bottom: 1px solid #e5e5e5;
}

.metrics-tabs :deep(.ant-tabs-tab) {
  padding: 16px 24px;
  margin: 0 4px 0 0;
  border: none;
  border-radius: 12px 12px 0 0;
  color: #666;
  font-weight: 500;
  font-size: 0.95rem;
  background: transparent;
  transition: all 0.3s ease;
}

.metrics-tabs :deep(.ant-tabs-tab:hover) {
  color: #495057;
  background: #f8f9fa;
}

.metrics-tabs :deep(.ant-tabs-tab-active) {
  color: #2c3e50;
  background: white;
  border-bottom: 2px solid #495057;
  font-weight: 600;
}

.metrics-tabs :deep(.ant-tabs-content-holder) {
  padding: 0;
}

/* 图表包装器 */
.chart-wrapper {
  padding: 32px;
  background: white;
  border-radius: 0;
}

.chart-header {
  margin-bottom: 32px;
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  position: relative;
  overflow: hidden;
}

.chart-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #6c757d 0%, #495057 100%);
}

.chart-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 12px 0;
  letter-spacing: -0.02em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.chart-desc {
  color: #6c757d;
  font-size: 1rem;
  margin: 0;
  line-height: 1.6;
  font-weight: 400;
}

/* 图表容器样式 */
.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  margin: 0 auto;
  max-width: 100%;
  min-height: 450px;
  position: relative;
  overflow: hidden;
}

.chart-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.03) 0%, rgba(73, 80, 87, 0.05) 100%);
  pointer-events: none;
}

.chart-container > * {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.network-container, .confusion-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 450px;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.network-container::before, .confusion-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.03) 0%, rgba(73, 80, 87, 0.05) 100%);
  pointer-events: none;
}

.network-container > *, .confusion-container > * {
  position: relative;
  z-index: 1;
}

.net-frame {
  width: 100%;
  height: 500px;
  border: none;
  border-radius: 12px;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.net-frame:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.conf-matrix {
  max-width: 100%;
  max-height: 600px;
  width: auto;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  background: white;
  transition: all 0.3s ease;
  padding: 8px;
}

.conf-matrix:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e5e5;
}

.empty-content {
  text-align: center;
  max-width: 400px;
  padding: 40px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.empty-desc {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

/* 识别结果 */
.prediction-result {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e5e5e5;
}

.result-header {
  padding: 24px 32px;
  background: #495057;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-meta {
  font-size: 0.9rem;
  opacity: 0.9;
}

.result-grid {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e5e5e5;
  transition: all 0.3s ease;
}

.result-card:hover {
  background: #f8f9fa;
  border-color: #6c757d;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(108, 117, 125, 0.15);
}

.result-card.top-result {
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-color: #f39c12;
}

.result-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #495057;
  color: white;
  border-radius: 50%;
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(73, 80, 87, 0.3);
}

.result-card.top-result .result-rank {
  background: #f39c12;
  box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
}

.result-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-link {
  color: #333;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: color 0.2s ease;
}

.result-link:hover {
  color: #495057;
  text-decoration: underline;
}

.result-confidence {
  display: flex;
  align-items: center;
  gap: 12px;
}

.confidence-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
  min-width: 60px;
}

.confidence-bar {
  flex: 1;
  height: 8px;
  background: #e5e5e5;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: #6c757d;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.confidence-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #495057;
  min-width: 50px;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }

  .header-stats {
    gap: 24px;
  }

  .control-grid {
    grid-template-columns: 1fr;
  }

  .chart-wrapper {
    padding: 20px;
  }

  .chart-header {
    padding: 20px;
    margin-bottom: 24px;
  }

  .chart-title {
    font-size: 1.2rem;
  }

  .chart-container {
    padding: 16px;
    min-height: 350px;
  }

  .chart-container > * {
    min-height: 300px;
  }

  .network-container, .confusion-container {
    min-height: 350px;
    padding: 16px;
  }

  .result-grid {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .page-header {
    padding: 24px;
  }

  .page-title {
    font-size: 2rem;
  }

  .control-panel {
    padding: 24px;
  }

  .chart-wrapper {
    padding: 20px;
  }

  .result-grid {
    padding: 20px;
  }

  .result-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .result-rank {
    align-self: flex-start;
  }

  .result-confidence {
    width: 100%;
  }
}
</style>

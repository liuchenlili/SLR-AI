<template>
  <div class="practice-page">
    <div class="page-header">
      <h1 class="page-title">手语练习</h1>
      <p class="page-subtitle">通过智能练习提升手语技能，获得个性化指导建议</p>
    </div>

    <div class="practice-container">
      <!-- 模型配置 -->
      <div class="model-config">
        <h3 class="section-title">模型配置</h3>
        <div class="config-grid">
          <div class="config-group">
            <label class="config-label">选择模型</label>
            <select v-model="store.selectedModel" class="config-select">
              <option value="">请选择模型</option>
              <option v-for="model in store.models" :key="model" :value="model">
                {{ model }}
              </option>
            </select>
          </div>
          <div class="config-group">
            <label class="config-label">选择权重</label>
            <select v-model="store.selectedWeight" class="config-select">
              <option value="">请选择权重</option>
              <option v-for="weight in store.weights" :key="weight" :value="weight">
                {{ weight }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- 练习模式选择 -->
      <div class="mode-selector">
        <h3 class="section-title">选择练习模式</h3>
        <div class="mode-options">
          <div
            v-for="mode in practiceModes"
            :key="mode.value"
            class="mode-option"
            :class="{ active: selectedMode === mode.value }"
            @click="selectMode(mode.value)"
          >
            <span class="mode-emoji">{{ mode.emoji }}</span>
            <span class="mode-label">{{ mode.label }}</span>
            <p class="mode-desc">{{ mode.description }}</p>
          </div>
        </div>
      </div>

      <!-- 录制视频练习 -->
      <div v-if="selectedMode === 'record'" class="practice-section">
        <div class="practice-card">
          <h3 class="card-title">录制练习</h3>
          <div class="practice-content">
            <div class="input-group">
              <label class="input-label">练习目标</label>
              <input
                v-model="targetText"
                placeholder="请输入本次练习目标，例如：你好"
                class="text-input"
              />
            </div>

            <div class="video-section">
              <video
                ref="videoRef"
                :src="previewUrl"
                :controls="!!previewUrl"
                autoplay
                muted
                class="video-player"
              />
              <div class="video-controls">
                <button
                  class="btn-primary"
                  @click="startRecording"
                  :disabled="recording"
                >
                  {{ recording ? '录制中...' : '开始录制' }}
                </button>
                <button
                  class="btn-secondary"
                  @click="stopRecording"
                  :disabled="!recording"
                >
                  结束录制
                </button>
              </div>
            </div>

            <button
              class="btn-submit"
              @click="submitPractice"
              :disabled="!targetText || !recordedVideo || loading || !store.selectedModel || !store.selectedWeight"
            >
              {{ loading ? '分析中...' : '提交并获取建议' }}
            </button>
          </div>
        </div>

        <!-- 结果展示 -->
        <div v-if="predictionResult || aiAdvice" class="result-section">
          <div class="result-card">
            <h3 class="card-title">识别结果</h3>
            <div v-if="predictionResult" class="prediction-list">
              <div
                v-for="(item, index) in predictionResult"
                :key="index"
                class="prediction-item"
              >
                <span class="rank">{{ index + 1 }}</span>
                <span class="word">{{ item[0] }}</span>
                <span class="confidence">{{ item[1] }}</span>
              </div>
            </div>
          </div>

          <div v-if="aiAdvice" class="advice-card">
            <h3 class="card-title">AI 指导建议</h3>
            <div class="advice-content" v-html="formatAdvice(aiAdvice)"></div>
          </div>
        </div>
      </div>

      <!-- 上传视频练习 -->
      <div v-if="selectedMode === 'upload'" class="practice-section">
        <div class="practice-card">
          <h3 class="card-title">上传视频</h3>
          <div class="upload-area" @click="triggerFileInput">
            <input
              ref="fileInput"
              type="file"
              accept="video/*"
              @change="handleFileUpload"
              style="display: none"
            />
            <div class="upload-placeholder">
              <span class="upload-icon">📁</span>
              <p class="upload-text">点击选择视频文件</p>
              <p class="upload-hint">支持 MP4, AVI, MOV 格式</p>
            </div>
          </div>

          <div v-if="uploadedVideo" class="video-preview">
            <video :src="uploadedVideoUrl" controls class="video-player" />
          </div>
          <div v-if="uploadedVideo" style="display: flex; align-items: flex-end; justify-content: center;margin-top: 10px">
            <button
              v-if="question==''"
              class="btn-primary"
              @click="analyzeUploadedVideo"
              :disabled="loading || !store.selectedModel || !store.selectedWeight"
            >
              {{ loading ? '分析中...' : '开始分析' }}
            </button>
            <button
              v-else
              class="btn-primary"
              style="margin-top: 20px;margin-left: 12px"
              @click="handleAsk"
              :disabled="question==''"
            > {{ loading ? '获取中...' : '获取智能评价' }}</button>
          </div>
          <div v-if="predictionResult" class="result-card" >
            <h3 class="card-title">识别结果</h3>
            <div v-if="predictionResult" class="prediction-list">
              <div
                v-for="(item, index) in predictionResult"
                :key="index"
                class="prediction-item"
              >
                <span class="rank">{{ index + 1 }}</span>
                <span class="word">{{ item[0] }}</span>
                <span class="confidence">{{ item[1] }}</span>
              </div>
            </div>
          </div>
          <div v-if="answer" style="margin-top: 24px;">
            <a-typography-title :level="5">AI答复</a-typography-title>
            <div style="background: #fafafa; padding: 14px 18px; border-radius: 6px;">
              <a-typography-paragraph>
                <div v-html="formatAdvice(answer)"></div>
              </a-typography-paragraph>
            </div>
          </div>


        </div>
      </div>

      <!-- CSL测试集练习 -->
      <div v-if="selectedMode === 'test'" class="practice-section">
        <div class="practice-card">
          <h3 class="card-title">CSL测试集</h3>
          <div class="test-selection">
            <label class="input-label">选择测试视频</label>
            <select v-model="selectedTestVideo" class="select-input">
              <option value="">请选择测试视频</option>
              <option v-for="video in testVideos" :key="video" :value="video">
                {{ video }}
              </option>
            </select>
          </div>

          <div v-if="selectedTestVideo" class="video-preview" >
            <video :src="`/data/ptov/${selectedTestVideo}`" controls class="video-player" />
          </div>
          <div  v-if="selectedTestVideo"  style="display: flex;margin-top: 20px;justify-content: center;">
            <button
              class="btn-primary"
              @click="analyzeTestVideo"
              :disabled="loading || !store.selectedModel || !store.selectedWeight"
            >
              {{ loading ? '分析中...' : '开始分析' }}
            </button>
          </div>
          <div v-if="predictionResult" class="result-card"  >
            <h3 class="card-title">识别结果</h3>
            <div v-if="predictionResult" class="prediction-list">
              <div
                v-for="(item, index) in predictionResult"
                :key="index"
                class="prediction-item"
              >
                <span class="rank">{{ index + 1 }}</span>
                <span class="word">{{ item[0] }}</span>
                <span class="confidence">{{ item[1] }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { useConfigStore } from '@/stores/cslConfig.ts'
import { predict } from '@/api/predictionController.ts'
import { addPracticeRecord, askAi, fullPredict } from '@/api/practiceController.ts'

const store = useConfigStore()

// 响应式数据
const selectedMode = ref('record')
const targetText = ref('')
const videoRef = ref<HTMLVideoElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const recording = ref(false)
const loading = ref(false)
const previewUrl = ref('')
const recordedVideo = ref<File | null>(null)
const uploadedVideo = ref<File | null>(null)
const selectedTestVideo = ref('')
const predictionResult = ref(null)
const aiAdvice = ref('')
const answer = ref('')
const question = ref('')
const recordedChunks = ref<Blob[]>([])
const predictionParsed = ref<any>(null)
let recorder: MediaRecorder | null = null
// 计算属性
const uploadedVideoUrl = computed(() => {
  return uploadedVideo.value ? URL.createObjectURL(uploadedVideo.value) : ''
})

// 练习模式配置
const practiceModes = ref([
  {
    value: 'record',
    label: '录制练习',
    emoji: '📹',
    description: '使用摄像头录制手语动作，获得实时反馈'
  },
  {
    value: 'upload',
    label: '上传视频',
    emoji: '📁',
    description: '上传已有的手语视频进行分析'
  },
  {
    value: 'test',
    label: 'CSL测试集',
    emoji: '🧪',
    description: '使用标准测试集评估识别准确性'
  }
])

const testVideos = ref([
  '000.mp4', '001.mp4', '002.mp4', '003.mp4', '004.mp4',
  '005.mp4', '006.mp4', '007.mp4', '008.mp4', '009.mp4'
])

// 方法
const selectMode = (mode: string) => {
  selectedMode.value = mode
  resetAll()
}

const resetAll = () => {
  predictionResult.value = null
  aiAdvice.value = ''
  targetText.value = ''
  recordedVideo.value = null
  uploadedVideo.value = null
  selectedTestVideo.value = ''
  previewUrl.value = ''
  question.value = ''
  answer.value = ''
}


const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
    recorder = new MediaRecorder(stream, { mimeType: 'video/webm' })
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
      recordedVideo.value = new File([blob], 'practice_record.webm', { type: 'video/webm' })
      if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
      previewUrl.value = URL.createObjectURL(recordedVideo.value)
      console.log('预览URL:', previewUrl.value)
    }
    recorder.start()
    message.success('开始录制')
  } catch (error) {
    message.error('无法访问摄像头')
  }
}

const stopRecording = () => {
  if (videoRef.value && videoRef.value.srcObject) {
    const stream = videoRef.value.srcObject as MediaStream
    stream.getTracks().forEach(track => track.stop())
  }
  if (recorder && recording.value) {
    recorder.stop()
    console.log('目标', targetText.value, '视频', recordedVideo.value)
    message.success('录制结束')
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    uploadedVideo.value = file
    message.success('视频上传成功')
  }
}

const submitPractice = async () => {
  if (!store.selectedModel || !store.selectedWeight) {
    message.warning('请先选择模型和权重')
    return
  }

  if (!targetText.value || !recordedVideo.value) {
    message.warning('请完成录制并填写练习目标')
    return
  }

  loading.value = true
  aiAdvice.value = ''
  try {
    // 这里应该调用识别API
    // const res = await predict({
    //   model: store.selectedModel,
    //   weight: store.selectedWeight,
    //   videoStyle: '录制视频',
    //   centercrop: false,
    // }, recordedVideo.value)
    // 1.  只需要提交目标文本（和其它参数）
    const params = {
      targetText: targetText.value,
      model: store.selectedModel, // 如需指定
      weight: store.selectedWeight,
      videoStyle: '录制视频',
      centercrop: false,
    }
    // 2. body 可为空对象
    const body = {}
    // 3. 直接调用 fullPredict
    const res = await fullPredict(params, body, recordedVideo.value)
    if (res.data.prediction) {
      try {
        predictionParsed.value = JSON.parse(res.data.prediction)
        predictionResult.value = predictionParsed.value.results
      } catch {
        predictionResult.value = null
      }
    }
    console.log("http://localhost:8000/videos/"+predictionParsed.value.filename)
    message.success('练习提交成功')
    aiAdvice.value = res.data.aiAdvice || 'AI未返回建议'
    await addPracticeRecord({
      targetText: targetText.value,
      aiAdvice: aiAdvice.value,
      predictJson: res.data.prediction,
      videoUrl:"http://localhost:8000/videos/"+predictionParsed.value.filename,
    })
    message.success('已获取AI建议并保存记录')
  } catch (error) {
    message.error('提交失败，请重试')
  } finally {
    loading.value = false
  }
}


const handleAsk = async () => {
  if (!question.value) {
    message.warning('请输入问题')
    return
  }
  loading.value = true
  answer.value = ''
  try {
    const res = await askAi({ question: question.value })
    // 兼容后端返回格式
    answer.value = res.data?.answer || res.data || 'AI未返回答复'
    message.success('已获取AI回答')
  } catch (e: any) {
    answer.value = e?.response?.data?.message || e.message || '提问失败'
    message.error('提问失败，请重试')
  } finally {
    loading.value = false
  }
}
const analyzeUploadedVideo = async () => {
  if (!store.selectedModel || !store.selectedWeight) {
    message.warning('请先选择模型和权重')
    return
  }

  if (!uploadedVideo.value) return

  loading.value = true
  try {
    // 调用分析API
    const res = await predict({
      model: store.selectedModel,
      weight: store.selectedWeight,
      videoStyle: '上传视频',
      centercrop: false,
    }, uploadedVideo.value)

    message.success('分析完成')
    predictionResult.value = res.data.results
    question.value="上传视频文件，通过算法预测结果为"+res.data.results+",请给出合理的智能指导意见。"
    store.setPrediction(res.data)
  } catch (error) {
    message.error('分析失败，请重试')
  } finally {
    loading.value = false
  }
}

const analyzeTestVideo = async () => {
  if (!store.selectedModel || !store.selectedWeight) {
    message.warning('请先选择模型和权重')
    return
  }

  if (!selectedTestVideo.value) return

  loading.value = true
  try {
    // 调用分析API
    const res = await predict({
      model: store.selectedModel,
      weight: store.selectedWeight,
      videoStyle: 'CSL测试集',
      centercrop: false,
      videoPath: `data/ptov/${selectedTestVideo.value}`,
    })

    message.success('分析完成')
    predictionResult.value = res.data.results

    store.setPrediction(res.data)
  } catch (error) {
    message.error('分析失败，请重试')
  } finally {
    loading.value = false
  }
}

const formatAdvice = (advice: string) => {
  return advice.replace(/\n/g, '<br>')
}

// 监听模型变化，自动加载权重
watch(
  () => store.selectedModel,
  async (val) => {
    if (val) {
      await store.fetchWeights()
      store.selectedWeight = store.weights[0] || ''
      store.prediction=null // 清空预测结果
      question.value = '';
      answer.value = '';
      aiAdvice.value = '';
    }
  },
  { immediate: true }
)
onMounted(async () => {
  // 如果还没有选中模型，自动选择第一个
  if (!store.selectedModel && store.models.length > 0) {
    store.selectedModel = store.models[0]
  }
  // 加载权重
  if (store.selectedModel) {
    await store.fetchWeights()
  }
})
</script>

<style scoped>
.practice-page {
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

.practice-container {
  max-width: 800px;
  margin: 0 auto;
}

.mode-selector {
  margin-bottom: 32px;
}

.model-config {
  margin-bottom: 32px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.config-select {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
  background: #fefefe;
}

.config-select:focus {
  outline: none;
  border-color: #64748b;
  box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.1);
  background: white;
}

.mode-selector {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
}

.mode-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.mode-option {
  padding: 20px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.mode-option:hover {
  border-color: #94a3b8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mode-option.active {
  border-color: #64748b;
  background: #f8fafc;
}

.mode-emoji {
  font-size: 2rem;
  display: block;
  margin-bottom: 8px;
}

.mode-label {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  display: block;
  margin-bottom: 4px;
}

.mode-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.practice-section {
  margin-top: 32px;
}

.practice-card,
.result-card,
.advice-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
  margin-bottom: 20px;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-group {
  margin-bottom: 24px;
}

.input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.text-input,
.select-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.text-input:focus,
.select-input:focus {
  outline: none;
  border-color: #64748b;
  box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.1);
}

.video-section {
  margin-bottom: 24px;
}

.video-player {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.video-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: #94a3b8;
  background: #f8fafc;
}

.upload-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 1rem;
  font-weight: 500;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.upload-hint {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.btn-primary,
.btn-secondary,
.btn-submit {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: #64748b;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #475569;
  transform: translateY(-1px);
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-submit {
  background: #2c3e50;
  color: white;
  width: 100%;
  padding: 16px;
  font-size: 1rem;
}

.btn-submit:hover:not(:disabled) {
  background: #1a252f;
  transform: translateY(-1px);
}

.btn-primary:disabled,
.btn-secondary:disabled,
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.prediction-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prediction-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #64748b;
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.word {
  flex: 1;
  font-weight: 500;
  color: #2c3e50;
}

.confidence {
  font-size: 0.875rem;
  color: #64748b;
  padding: 4px 8px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.advice-content {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  line-height: 1.6;
  color: #475569;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .practice-page {
    padding: 20px 16px;
  }

  .mode-options {
    grid-template-columns: 1fr;
  }

  .video-controls {
    flex-direction: column;
    align-items: center;
  }
}

.video-preview {
  display: flex;
  justify-content: center;
  margin-top: 10px;
  width: 100%;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
</style>

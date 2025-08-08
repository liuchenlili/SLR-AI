<!-- RealtimePage.vue -->

<template>
  <div class="page">
    <div class="header">
      <h1>实时手语识别</h1>
      <p>左侧实时识别，右侧扣子智能体给出建议</p>
    </div>

    ```
    <div class="card">
      <!-- 配置 -->
      <div class="config">
        <div class="field">
          <label>模型</label>
          <a-select v-model:value="store.selectedModel" :options="modelOptions" size="large" />
        </div>
        <div class="field">
          <label>权重</label>
          <a-select
            v-model:value="store.selectedWeight"
            :options="weightOptions"
            size="large"
            :key="store.selectedModel"
          />
        </div>
        <div class="field">
          <label>阈值（0~1）</label>
          <input type="range" min="0" max="1" step="0.01" v-model.number="thres" />
          <span class="thres">{{ thres.toFixed(2) }}</span>
        </div>
        <div class="btns">
          <button class="btn start" :disabled="running" @click="start">启动识别</button>
          <button class="btn stop" :disabled="!running" @click="stop">停止识别</button>
        </div>
      </div>

      <!-- 三列：画面 / 结果 / 建议 -->
      <div class="preview-wrap">
        <!-- 画面 -->
        <div class="preview">
          <img v-if="frameUrl" :src="frameUrl" class="img" />
          <div v-else class="placeholder">等待推流中…</div>
        </div>

        <!-- 结果 -->
        <div class="result">
          <div class="line">
            <span class="k">识别结果：</span><span class="v main">{{ label || '—' }}</span>
          </div>
          <div class="line">
        <span class="k">置信度：</span
        ><span class="v">{{ (confidence * 100).toFixed(1) }}%</span>
          </div>
          <ul v-if="results.length" class="topk">
            <li v-for="(it, idx) in results" :key="idx">
              <a
                :href="`https://www.spreadthesign.com/zh.hans.cn/search/?q=${it[0]}`"
                target="_blank"
              >
                {{ idx + 1 }}. {{ it[0] }} - {{ it[1] }}
              </a>
            </li>
          </ul>
        </div>

        <!-- 建议（扣子） -->
        <div class="advice">
          <div class="advice-header">
            <div class="title">AI 实时建议（扣子）</div>
            <div class="right">
              <a-switch v-model:checked="autoAdvice" /><span
              style="margin-left: 8px; color: #63728b"
            >自动</span
            >
            </div>
          </div>

          <a-textarea
            v-model:value="question"
            :rows="3"
            placeholder="可输入你的疑问，例如：这个手型哪里不对？"
            style="margin: 8px 0"
          />

          <div class="advice-btns">
            <a-button type="primary" :disabled="!label || !running" @click="fetchAdvice(true)">
              生成建议
            </a-button>
            <span v-if="adviceLoading" class="loading">生成中…</span>
          </div>

          <a-card v-if="advice" size="small" style="margin-top: 8px">
            <pre class="advice-text">{{ advice }}</pre>
          </a-card>
        </div>
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
    ```

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount, watch } from 'vue'
import { useConfigStore } from '@/stores/cslConfig.ts'
import { getAdvice } from '@/api/advice.ts'

const store = useConfigStore()
const modelOptions = computed(() => store.models.map((m) => ({ value: m, label: m })))
const weightOptions = computed(() => store.weights.map((w) => ({ value: w, label: w })))

// 模型切换时刷新权重
watch(
  () => store.selectedModel,
  async (val) => {
    if (val) {
      await store.fetchWeights(val)
      store.selectedWeight = ''
      store.selectedWeight = store.weights[0] || ''
    }
  },
  { immediate: true },
)

// ================== 实时识别 ==================
const running = ref(false)
const ws = ref<WebSocket | null>(null)
const WS_URL = 'ws://localhost:8001/ws/recognize'

const frameUrl = ref('')
const label = ref('')
const confidence = ref(0)
const results = ref<[string, string][]>([])
const thres = ref(0.75)

// recent（传给建议后端用于上下文）
const recent = ref<string[][]>([])
const RECENT_MIN_CONF = 0.6
const MAX_RECENT = 10

// 自动建议（每 1 分钟一次）
const autoAdvice = ref(false)
const MIN_INTERVAL = 1800 // 节流兜底（自动模式不依赖它，但手动/实时触发会用到）
const MIN_CONF = 0.45
let lastLabel = ''
let lastAdviceAt = 0
const advice = ref('')
const adviceLoading = ref(false)
const question = ref('')

// 中断控制器：取消并发中的建议请求
let adviceAbort: AbortController | null = null
// 自动模式定时器（每 30s 触发一次）
let autoTimer: number | null = null

function start() {
  if (running.value) return
  frameUrl.value = ''
  label.value = ''
  confidence.value = 0
  results.value = []
  advice.value = ''
  recent.value = []

  ws.value = new WebSocket(WS_URL)
  running.value = true

  ws.value.onopen = () => {
    ws.value?.send(
      JSON.stringify({
        model: store.selectedModel,
        weight: store.selectedWeight,
        thres: thres.value,
      }),
    )
  }

  ws.value.onmessage = (evt) => {
    const data = JSON.parse(evt.data)
    frameUrl.value = data.image || ''
    label.value = data.label ?? ''
    confidence.value = Number(data.confidence ?? 0)
    results.value = Array.isArray(data.results) ? data.results : []

    // 维护 recent（只收高置信 & 去重）
    if (label.value && label.value !== 'NULL' && confidence.value >= RECENT_MIN_CONF) {
      const pct = (confidence.value * 100).toFixed(1) + '%'
      const head = recent.value[0]
      if (!head || head[0] !== label.value || head[1] !== pct) {
        recent.value.unshift([label.value, pct])
        if (recent.value.length > MAX_RECENT) recent.value.pop()
      }
    }
    // 这里不再用“来帧触发自动建议”，自动模式改为定时器驱动
  }

  ws.value.onclose = () => {
    running.value = false
    cleanupAdviceFlow()
    ws.value = null
  }

  ws.value.onerror = () => {
    running.value = false
    cleanupAdviceFlow()
    ws.value?.close()
    ws.value = null
  }
}

function stop() {
  // 1) 关闭 WS
  ws.value?.close()
  ws.value = null
  running.value = false

  // 2) 关闭自动建议 & 清理节流状态
  autoAdvice.value = false
  lastLabel = ''
  lastAdviceAt = 0

  // 3) 清理建议请求与定时器
  cleanupAdviceFlow()

  // 4) 清空 UI
  frameUrl.value = ''
  label.value = ''
  confidence.value = 0
  results.value = []
  advice.value = ''
}

function cleanupAdviceFlow() {
  if (adviceAbort) {
    adviceAbort.abort()
    adviceAbort = null
  }
  if (autoTimer) {
    clearInterval(autoTimer)
    autoTimer = null
  }
}

onBeforeUnmount(stop)

// 自动开关：开启时立即拉一次，随后每 5 秒拉一次；关闭时清理
watch(autoAdvice, (on) => {
  if (!on) {
    cleanupAdviceFlow()
    return
  }
  // 开启
  if (running.value && label.value && label.value !== 'NULL') {
    fetchAdvice() // 立即来一次
  }
  // 每隔 5 秒生成一次（force 跳过节流）
  autoTimer = window.setInterval(() => {
    if (running.value && autoAdvice.value && label.value && label.value !== 'NULL') {
      fetchAdvice()
    }
  }, 5000)
})

// ================== 建议 ==================
async function fetchAdvice(force = false) {
  // 停止识别后：任何情况下都不生成（硬约束）
  if (!running.value) return

  // 自动模式：关了“自动”就不走；手动(force)可以继续
  if (!force && !autoAdvice.value) return

  if (!label.value || label.value === 'NULL') return

  const now = Date.now()
  if (!force) {
    if (label.value === lastLabel && now - lastAdviceAt < MIN_INTERVAL) return
    if (confidence.value < MIN_CONF) return
  }

  // 取消上一个未完成的建议请求
  if (adviceAbort) {
    adviceAbort.abort()
  }
  adviceAbort = new AbortController()

  adviceLoading.value = true
  try {
    const data = await getAdvice(
      {
        label: label.value,
        confidence: confidence.value,
        recent: recent.value,
        question: (question.value || '').trim(),
        user_id: 'spring_client',
      },
      adviceAbort.signal,
    ) // 传入 signal
    advice.value = data.advice || ''
    lastLabel = label.value
    lastAdviceAt = now
  } catch (e: any) {
    if (e?.name === 'AbortError') {
      // 被取消：静默
    } else {
      console.error(e)
      advice.value = '(获取建议失败)'
    }
  } finally {
    // 若本次已被取消，避免误改 loading 状态
    if (!adviceAbort || !adviceAbort.signal.aborted) {
      adviceLoading.value = false
    }
  }
}
</script>

<style scoped>
.page {
  max-width: 1140px;
  margin: 0 auto;
  padding: 28px 16px 48px;
}
.header {
  text-align: center;
  margin-bottom: 22px;
}
.header h1 {
  margin: 0 0 6px;
  font-size: 28px;
  color: #24324b;
}
.header p {
  margin: 0;
  color: #65748b;
}
.card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 14px;
  box-shadow: 0 2px 14px rgba(0, 0, 0, 0.04);
  padding: 18px;
  margin-bottom: 18px;
}
.config {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  align-items: end;
}
.field {
  display: flex;
  flex-direction: column;
}
.field label {
  font-size: 13px;
  color: #4e5969;
  margin-bottom: 6px;
}
.field input[type='range'] {
  width: 100%;
}
.thres {
  margin-left: 8px;
  color: #2b5cff;
  font-weight: 600;
}
.btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.btn {
  padding: 8px 22px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: 0.15s;
}
.btn.start {
  background: #2b5cff;
  color: #fff;
}
.btn.stop {
  background: #a7b4d6;
  color: #fff;
}
.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.preview-wrap {
  display: grid;
  grid-template-columns: 1.3fr 1fr 1.2fr;
  gap: 18px;
  margin-top: 18px;
}
.preview {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f9fc;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  min-height: 320px;
}
.img {
  width: 100%;
  max-width: 520px;
  border-radius: 10px;
  object-fit: cover;
}
.placeholder {
  color: #9aa6b2;
}
.result {
  border: 1px solid #eef2f7;
  border-radius: 12px;
  padding: 16px;
  background: #fbfcff;
}
.line {
  margin-bottom: 8px;
}
.k {
  color: #5b6b7b;
}
.v {
  color: #22324a;
  font-weight: 600;
}
.v.main {
  color: #ff6a00;
}
.topk {
  margin: 12px 0 0;
  padding-left: 16px;
}
.topk a {
  color: #3156d6;
  text-decoration: none;
}
.topk a:hover {
  text-decoration: underline;
}
.advice {
  border: 1px solid #eef2f7;
  border-radius: 12px;
  padding: 14px;
  background: #fffdfa;
  display: flex;
  flex-direction: column;
}
.advice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  font-weight: 700;
  color: #2c3e50;
}
.advice-btns {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 6px 0;
}
.loading {
  color: #a0a8b8;
  font-size: 12px;
}
.advice-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: ui-monospace, Menlo, Consolas, monospace;
}
@media (max-width: 1100px) {
  .preview-wrap {
    grid-template-columns: 1fr;
  }
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
</style>

<template>

  <div class="main-content"  >
    <h1 class="main-title">Sign Language Recognition System</h1>
    <div class="main-subtitle">{{ store.selectedModel }} 网络的展示</div>
      <div style="display: flex; align-items: flex-end; margin-bottom: 20px;">
        <!-- 左侧按钮 -->
<!--        <div style="display: flex; align-items: flex-end;">-->
<!--          <a-button-->
<!--            type="primary"-->
<!--            :loading="loading"-->
<!--            style="margin-top: 20px"-->
<!--            @click="handlePredict"-->
<!--          >开始识别</a-button>-->
<!--          <a-button-->
<!--            danger-->
<!--            style="margin-left: 12px;"-->
<!--            @click="handleClearPrediction"-->
<!--          >重置结果</a-button>-->
<!--        </div>-->
        <!-- 右侧表单 横向排布 -->
        <a-form layout="inline" style="display: flex; align-items: flex-end;margin-top: 20px">
          <a-form-item label="选择模型">
            <a-select
              v-model:value="store.selectedModel"
              :options="modelOptions"
              placeholder="选择模型"
              style="width: 130px"
            />
          </a-form-item>
          <a-form-item label="选择权重">
            <a-select
              v-model:value="store.selectedWeight"
              :options="weightOptions"
              placeholder="选择权重"
              style="width: 150px"
            />
          </a-form-item>
          <div style="width: 100%;margin-top: 20px"></div>
<!--          <a-form-item label="选择视频方式">-->
<!--            <a-select-->
<!--              v-model:value="store.selectedVideoStyle"-->
<!--              :options="videoStyleOptions"-->
<!--              placeholder="选择视频"-->
<!--              style="width: 120px"-->
<!--            />-->
<!--          </a-form-item>-->
<!--          <a-form-item v-if="store.selectedVideoStyle === '上传视频'" label="上传视频">-->
<!--            <a-upload :customRequest="handleUpload" :show-upload-list="false">-->
<!--              <a-button style="width: 120px">上传视频</a-button>-->
<!--            </a-upload>-->
<!--          </a-form-item>-->
<!--          <a-form-item v-if="store.selectedVideoStyle === '录制视频'" label="录制视频">-->
<!--            <a-button @click="startRecording" :disabled="recording" style="margin-right: 6px;">开始录制</a-button>-->
<!--            <a-button @click="stopRecording" :disabled="!recording">停止录制</a-button>-->
<!--          </a-form-item>-->
<!--          <a-form-item v-if="store.selectedVideoStyle === 'CSL测试集'" label="选择测试视频">-->
<!--            <a-select-->
<!--              v-model:value="store.selectedCSLVideo"-->
<!--              :options="cslVideoOptions"-->
<!--              placeholder="选择测试视频"-->
<!--              style="width: 120px"-->
<!--            />-->
<!--          </a-form-item>-->

        </a-form>
<!--        &lt;!&ndash; 视频预览区（建议放在操作区下方，紧接其后） &ndash;&gt;-->
<!--        <div v-if="videoPreviewUrl" style="padding: 16px 0 0 0; max-width: 60px;">-->
<!--          <div style="font-size: 13px; margin-bottom: 6px;">当前视频预览：</div>-->
<!--          <video-->
<!--            :src="videoPreviewUrl"-->
<!--            controls-->
<!--            style="width: 100%; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.06)"-->
<!--          />-->
<!--        </div>-->
<!--        <div v-if="store.recordedVideo">-->
<!--          <div style="font-size: 13px; margin-bottom: 6px">录制预览：</div>-->
<!--          <video-->
<!--            :src="store.recordedVideo && URL.createObjectURL(store.recordedVideo)"-->
<!--            controls-->
<!--            style="width: 100%; border-radius: 6px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06)"-->
<!--          />-->
<!--        </div>-->
      </div>

      <a-tabs
        v-if="store.selectedModel&&!store.prediction"
        v-model:activeKey="activeKey"
        @change="handleTabChange"
        style="margin-top: 24px"
      >
        <a-tab-pane key="acc" tab="acc曲线图">
          <EchartLine
            ref="accLine"
            :data-url="`/python/metrics/acc?model=${encodeURIComponent(store.selectedModel)}`"
          />
        </a-tab-pane>
        <a-tab-pane key="loss" tab="loss曲线图">
          <EchartLine
            ref="lossLine"
            :data-url="`/python/metrics/loss?model=${encodeURIComponent(store.selectedModel)}`"
          />
        </a-tab-pane>
        <a-tab-pane key="net" tab="网络可视化">
          <iframe class="net-frame" :srcdoc="netHtml" />
        </a-tab-pane>
        <a-tab-pane key="conf" tab="Confusion Matrix">
          <img :src="confImage" class="conf-matrix" />
        </a-tab-pane>
      </a-tabs>

      <div v-if="store.prediction" style="margin-top: 36px">
        <a-typography-title :level="5">识别结果</a-typography-title>
        <a-list bordered :data-source="store.prediction.results">
          <template #renderItem="{ item, index }">
            <a-list-item>
              <a
                :href="`https://www.spreadthesign.com/zh.hans.cn/search/?q=${item[0]}`"
                target="_blank"
              >
                {{ index + 1 }}. {{ item[0] }} - 置信度: {{ item[1] }}
              </a>
            </a-list-item>
          </template>
        </a-list>
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
  padding: 48px 64px;
}
.main-title {
  font-size: 2.7rem;
  font-weight: 700;
  color: #353844;
  margin-bottom: 8px;
}
.main-subtitle {
  color: #7d7d7d;
  font-size: 1rem;
}
.net-frame {
  width: 100%;
  height: 500px;
  border: none;
}
.conf-matrix {
  max-width: 700px;
  width: 100%;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.realtime-block {
  margin-bottom: 36px;
  background: #f8fafc;
  padding: 24px 32px;
  border-radius: 12px;
  border: 1px solid #e8e8ec;
  max-width: 360px;
}
.realtime-demo {
  padding-top: 0; /* 确保顶部内边距为0 */
  margin-top: 0;
}
.realtime-demo a-button {
  margin-bottom: 10px; /* 确保按钮顶部外边距为0 */
}
</style>

<template>
  <div id="globalSider">
    <a-layout-sider
      v-if="loginUserStore.loginUser.id"
      class="sider-custom"
      width="240px"
      breakpoint="lg"
      collapsed-width="0"
      theme="light"
      collapsible
      v-model:collapsed="collapsed"
      v-show="configStore.selectedVideoStyle !== '实时识别'"
    >

      <div style="display: flex; flex-direction: column; height: 100%">
        <a-typography-title :level="5" style="text-align: center; margin-bottom: 8px"
          >配置</a-typography-title
        >
        <div>
          <a-form layout="vertical" class="sider-form">
            <a-form-item label="选择模型">
              <a-select
                v-model:value="configStore.selectedModel"
                :options="modelOptions"
                placeholder="选择模型"
              />
            </a-form-item>
            <a-form-item label="选择权重">
              <a-select
                v-model:value="configStore.selectedWeight"
                :options="weightOptions"
                placeholder="选择权重"
              />
            </a-form-item>
            <a-form-item v-if="!isPracticePage" label="选择视频方式">
              <a-select
                v-model:value="configStore.selectedVideoStyle"
                :options="videoStyleOptions"
                placeholder="选择视频"
              />
            </a-form-item>

            <!-- 上传视频 -->
            <a-form-item
              v-if="!isPracticePage && configStore.selectedVideoStyle === '上传视频'"
              label="上传视频"
            >
              <div style="display: flex; justify-content: center">
                <a-upload :customRequest="handleUpload" :show-upload-list="false" class="w-full">
                  <a-button style="width: 180px" block>上传视频</a-button>
                </a-upload>
              </div>
            </a-form-item>

            <!-- 录制视频 -->
            <a-form-item
              v-if="!isPracticePage && configStore.selectedVideoStyle === '录制视频'"
              label="录制视频"
            >
              <video ref="videoRef" autoplay style="width: 100%; margin-bottom: 8px" />
              <a-space direction="vertical" style="width: 100%">
                <a-button block @click="startRecording" :disabled="recording">开始录制</a-button>
                <a-button block @click="stopRecording" :disabled="!recording">停止录制</a-button>
              </a-space>
              <div v-if="configStore.recordedVideo" style="margin-top: 12px">
                <div style="font-size: 13px; margin-bottom: 6px">录制预览：</div>
                <video
                  :src="configStore.recordedVideo && URL.createObjectURL(configStore.recordedVideo)"
                  controls
                  style="width: 100%; border-radius: 6px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06)"
                />
              </div>
            </a-form-item>

            <!-- 测试集 -->
            <a-form-item
              v-if="!isPracticePage && configStore.selectedVideoStyle === 'CSL测试集'"
              label="选择测试视频"
            >
              <a-select
                v-model:value="configStore.selectedCSLVideo"
                :options="cslVideoOptions"
                placeholder="选择测试视频"
              />
            </a-form-item>
          </a-form>

          <div v-if="!isPracticePage && videoPreviewUrl" style="padding: 16px 16px 0 16px">
            <div style="font-size: 13px; margin-bottom: 6px">当前视频预览：</div>
            <video
              :src="videoPreviewUrl"
              controls
              style="width: 100%; border-radius: 6px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06)"
            />
          </div>
        </div>
        <div style="flex: 1"></div>
        <!-- 实时识别 -->
        <div style="padding: 24px 16px 20px 16px">
          <a-button  type="primary"  block @click="startRealtime">实时识别</a-button>
        </div>
      </div>
    </a-layout-sider>
  </div>
</template>

<script lang="ts" setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { useConfigStore } from '../stores/cslConfig'
import { message } from 'ant-design-vue'
import { useRoute } from 'vue-router'
import router from '@/router'
const route = useRoute()

const loginUserStore = useLoginUserStore()
const configStore = useConfigStore()
const videoRef = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null
let recorder: MediaRecorder | null = null
const recordedChunks = ref<Blob[]>([])
const recording = ref(false)
const collapsed = ref(false)
let ws: WebSocket | null = null
const realtimeLoading = ref(false)
const isPracticePage = computed(() => route.path.includes('/practice'))

const videoPreviewUrl = computed(() => {
  if (configStore.selectedVideoStyle === '上传视频' && configStore.uploadedVideo) {
    return URL.createObjectURL(configStore.uploadedVideo)
  }
  if (configStore.selectedVideoStyle === 'CSL测试集' && configStore.selectedCSLVideo) {
    return `/data/ptov/${configStore.selectedCSLVideo}`
  }
  return ''
})

const modelOptions = computed(() =>
  configStore.models.map((model) => ({ value: model, label: model })),
)
const weightOptions = computed(() =>
  configStore.weights.map((weight) => ({ value: weight, label: weight })),
)
const videoStyleOptions = computed(() =>
  configStore.videoStyles.map((style) => ({ value: style, label: style })),
)
const cslVideoOptions = computed(() =>
  configStore.cslVideos.map((video) => ({ value: video, label: video })),
)

// 自动监听模型变化，加载权重并默认选中第一个权重
const fetchWeights = async () => {
  await configStore.fetchWeights()
}
watch(
  () => configStore.selectedModel,
  async (val) => {
    if (val) {
      await fetchWeights()
      configStore.selectedWeight = configStore.weights[0] || ''
    }
  },
  { immediate: true },
)
watch(
  () => configStore.selectedVideoStyle,
  (val) => {
    if (val === '上传视频') {
      configStore.selectedCSLVideo = ''
    } else if (val === 'CSL测试集') {
      configStore.uploadedVideo = null
      configStore.recordedVideo = null
    } else if (val === '录制视频') {
      configStore.uploadedVideo = null
      configStore.selectedCSLVideo = ''
    } else {
      configStore.uploadedVideo = null
      configStore.selectedCSLVideo = ''
      configStore.recordedVideo = null
    }
  },
)

const handleUpload = async ({ file }: { file: File }) => {
  configStore.setUploadedVideo(file)
}

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
    configStore.setRecordedVideo(new File([blob], 'recorded.webm', { type: 'video/webm' }))
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
  if (!configStore.selectedModel || !configStore.selectedWeight) {
    message.warning('请先选择模型和权重')
    return
  }
  message.success('进入实时识别')
  // 切换到实时识别模式
  configStore.selectedVideoStyle = '实时识别'
  router.push({
    path: '/',
  })
  // if (!configStore.selectedModel || !configStore.selectedWeight) {
  //   message.warning('请先选择模型和权重')
  //   return
  // }
  // if (ws) ws.close()
  // realtimeLoading.value = true
  // ws = new WebSocket('ws://localhost:8000/ws/recognize')
  // ws.onopen = () => {
  //   configStore.startRealtime()
  //   // 向后端发送模型和权重（重要）
  //   ws!.send(
  //     JSON.stringify({
  //       model: configStore.selectedModel,
  //       weight: configStore.selectedWeight,
  //       thres:configStore.realtimeThres,
  //     }),
  //   )
  //   realtimeLoading.value = false
  // }
  // ws.onmessage = (event) => {
  //   const data = JSON.parse(event.data)
  //   console.log(data);
  //   configStore.updateRealtimeResult(data.image, data.label, data.confidence)
  // }
  // ws.onclose = () => {
  //   configStore.stopRealtime()
  //   ws = null
  //   message.info('实时识别已断开')
  // }
  // ws.onerror = (e) => {
  //   realtimeLoading.value = false
  //   configStore.stopRealtime()
  //   ws = null
  //   message.error('实时识别连接失败')
  // }
}

const stopRealtime = () => {
  if (ws) ws.close()
  ws = null
  configStore.stopRealtime()
}
onBeforeUnmount(() => {
  if (ws) ws.close()
  ws = null
  configStore.stopRealtime()
})
</script>

<style scoped>
#globalSider .ant-layout-sider {
}
.sider-custom {
  padding-top: 0;
}
.sider-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  padding: 24px 0 12px 24px;
  background: #fff;
  margin-bottom: 8px;
  letter-spacing: 1px;
}
.sider-form {
  padding: 0 16px 24px 16px;
}
.video-preview-block {
  padding: 0 16px 0 16px;
}
.video-preview-title {
  font-size: 13px;
  margin-bottom: 4px;
  color: #888;
}
.video-preview {
  width: 100%;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
:deep(.ant-form-item-label > label) {
  color: #57606a;
  font-weight: 500;
}
:deep(.ant-form-item) {
  margin-bottom: 18px;
}
:deep(.ant-select-selector),
:deep(.ant-upload),
:deep(.ant-btn) {
  border-radius: 7px !important;
}
:deep(.ant-select-selector),
:deep(.ant-upload),
:deep(.ant-btn) {
  border-radius: 6px !important;
}
</style>

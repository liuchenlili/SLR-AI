<template>
  <div class="realtime-demo" v-if="store.selectedVideoStyle === '实时识别'">
    <a-button block @click="stopRealtime" style="margin-bottom: 5px">退出实时识别</a-button>
    <!-- 嵌入Streamlit实时识别界面 -->
    <iframe
      src="http://localhost:8501"
      width="100%" height="900px" frameborder="0">
    </iframe>

  </div>
  <div class="main-content" v-if="store.selectedVideoStyle !== '实时识别'" >
    <h1 class="main-title">Sign Language Recognition System</h1>
    <div class="main-subtitle">{{ store.selectedModel }} 网络的展示</div>
    <!--      <div v-if="store.selectedVideoStyle === '实时识别'" style="display:flex;justify-content:center;align-items:flex-start;margin-top:18px;">-->
<!--        <div style="width:80%;max-width:900px;">-->
<!--          <div style="display:flex;justify-content:space-between;font-size:2rem;font-weight:600;margin-bottom:8px;">-->
<!--            <span>预测词汇</span>-->
<!--            <span>Confidence Level</span>-->
<!--            <span>FPS</span>-->
<!--          </div>-->
<!--          <div style="display:flex;justify-content:space-between;align-items:center;font-size:1.1rem;margin-bottom:12px;">-->
<!--            <span style="width:180px;">{{ store.realtimeLabel || 'NULL' }}</span>-->
<!--            <span style="width:180px;">{{store.realtimeConfidence ? store.realtimeLabel+(store.realtimeConfidence*100).toFixed(2)+'%' : "..." }}</span>-->
<!--            <span style="width:120px;">{{ fpsText }}</span>-->
<!--          </div>-->
<!--          <div v-if="store.realtimeFrame" style="width:100%;text-align:center;">-->
<!--            <img :src="store.realtimeFrame" style="max-width:100%;height:auto;min-height:400px;object-fit:contain;background:#f5f6fa;" />-->
<!--            <div style="margin-top:8px;color:#888;">Real Video</div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
      <div v-if="store.selectedVideoStyle !== '实时识别'">
        <a-button
          type="primary"
          :loading="loading"
          style="margin-bottom: 24px; margin-top: 20px"
          @click="handlePredict"
        >开始识别</a-button>
        <a-button
          danger
          style="margin-left: 12px; margin-bottom: 24px;"
          @click="handleClearPrediction"
        >重置结果</a-button>
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

  </div>
</template>

<script lang="ts" setup>
import { ref, watch, nextTick, onBeforeUnmount, computed, onUnmounted } from 'vue'
import { useConfigStore } from '@/stores/cslConfig'
import EchartLine from '@/components/EchartLine.vue'
import { getNetworkGraph, getConfusionMatrix, predict } from '@/api/predictionController.ts'
import { message } from 'ant-design-vue'

const store = useConfigStore()
const netHtml = ref('')
const confImage = ref('')
const loading = ref(false)
const activeKey = ref('acc')
const accLine = ref()
const lossLine = ref()
const realtimeLoading = ref(false)
let ws: WebSocket | null = null
const fps = ref(0)
let lastTime = Date.now()
watch(() => store.realtimeFrame, () => {
  // 计算FPS
  const now = Date.now()
  fps.value = 1000 / (now - lastTime)
  lastTime = now
})

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
// ======= 实时识别 WebSocket 相关 =======
// const videoRef = ref<HTMLVideoElement|null>(null)
// const ws = ref<WebSocket|null>(null)
// const realtimeLabel = ref('')
// const realtimeConfidence = ref(0)
// const realtimeOn = ref(false)
//
// let captureTimer: any = null
// const startRealtime = async () => {
//   if (realtimeOn.value) return
//   // 打开摄像头
//   const stream = await navigator.mediaDevices.getUserMedia({ video: true })
//   if (videoRef.value) videoRef.value.srcObject = stream
//
//   // 连接WebSocket
//   ws.value = new WebSocket('ws://localhost:8000/ws/recognize')
//   ws.value.onopen = () => {
//     realtimeOn.value = true
//     ws.value!.send(JSON.stringify({
//       model: store.selectedModel,
//       weight: store.selectedWeight,
//       thres: store.realtimeThres
//     }))
//     // 定时采集帧并推送
//     const canvas = document.createElement('canvas')
//     canvas.width = 128
//     canvas.height = 128
//     const ctx = canvas.getContext('2d')
//     captureTimer = setInterval(() => {
//       if (videoRef.value && ctx) {
//         ctx.drawImage(videoRef.value, 0, 0, 128, 128)
//         canvas.toBlob((blob) => {
//           if (!blob) return
//           const reader = new FileReader()
//           reader.onloadend = () => {
//             // @ts-ignore
//             ws.value && ws.value.send(JSON.stringify({ image: reader.result }))
//           }
//           reader.readAsDataURL(blob)
//         }, 'image/jpeg', 0.85)
//       }
//     }, 40) // 25帧/s
//     message.success('实时识别已开启')
//   }
//   ws.value.onmessage = (evt) => {
//     const data = JSON.parse(evt.data)
//     realtimeLabel.value = data.label
//     realtimeConfidence.value = data.confidence
//   }
//   ws.value.onclose = () => {
//     realtimeOn.value = false
//     realtimeLabel.value = ''
//     realtimeConfidence.value = 0
//     if (videoRef.value?.srcObject) {
//       // @ts-ignore
//       videoRef.value.srcObject.getTracks().forEach((track: any) => track.stop())
//     }
//     if (captureTimer) clearInterval(captureTimer)
//     message.info('实时识别已断开')
//   }
//   ws.value.onerror = () => {
//     realtimeOn.value = false
//     if (captureTimer) clearInterval(captureTimer)
//     message.error('WebSocket连接失败')
//   }
// }
//
// const stopRealtime = () => {
//   if (ws.value) ws.value.close()
//   ws.value = null
//   realtimeOn.value = false
//   if (captureTimer) clearInterval(captureTimer)
//   if (videoRef.value?.srcObject) {
//     // @ts-ignore
//     videoRef.value.srcObject.getTracks().forEach((track: any) => track.stop())
//   }
// }
// onUnmounted(() => {
//   stopRealtime()
// })
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

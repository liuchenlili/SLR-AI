<template>
  <a-layout style="min-height: 100vh">
    <GlobalSider class="sider" />
    <!-- 主内容区 -->
    <a-layout style="background: #fff; padding: 0 20px">
      <a-layout-content style="margin: 24px">
        <div class="practice-main">
          <a-card
            v-if="store.selectedVideoStyle === '录制视频'"
            title="练习录制与智能建议"
            :bordered="false"
          >
            <a-form layout="vertical">
              <a-form-item label="练习目标">
                <a-input
                  v-model:value="targetText"
                  placeholder="请输入本次练习目标，例如：团结"
                  style="max-width: 340px"
                />
              </a-form-item>

              <a-form-item label="视频录制">
                <video
                  ref="videoRef"
                  :src="previewUrl"
                  :controls="!!previewUrl"
                  autoplay
                  style="
                    width: 400px;
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px #f0f1f2;
                    margin-bottom: 8px;
                  "
                />
                <a-space>
                  <a-button type="primary" @click="startRecording" :disabled="recording"
                    >开始录制</a-button
                  >
                  <a-button @click="stopRecording" :disabled="!recording">结束录制</a-button>
                </a-space>
              </a-form-item>

              <a-button
                type="primary"
                @click="submitPractice"
                :loading="loading"
                :disabled="!targetText || !recordedVideo"
                style="margin-top: 12px"
                >提交并获取智能建议</a-button
              >
            </a-form>

            <div v-if="aiAdvice || predictionParsed" style="margin-top: 24px">
              <a-typography-title :level="5">算法预测结果</a-typography-title>
              <div v-if="predictionParsed">
                <a-list bordered :data-source="predictionParsed.results">
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

              <a-typography-title :level="5" style="margin-top: 18px"
                >AI教学建议</a-typography-title
              >
              <div style="background: #fafafa; padding: 14px 18px; border-radius: 6px">
                <a-typography-paragraph>
                  <div v-html="formatAdvice(aiAdvice)"></div>
                </a-typography-paragraph>
              </div>
            </div>
          </a-card>
          <a-card
            v-if="store.selectedVideoStyle === '上传视频'"
            title="上传视频"
            :bordered="false"
            style="margin-bottom: 24px"
          >
            <a-form layout="vertical">
              <a-form-item label="上传视频">
                <div style="display: flex; justify-content: center">
                  <a-upload :customRequest="handleUpload" :show-upload-list="false" class="w-full">
                    <a-button style="width: 180px" block>上传视频</a-button>
                  </a-upload>
                </div>
              </a-form-item>

              <div v-if="videoPreviewUrl" style="margin-top: 16px">
                <div style="font-size: 13px; margin-bottom: 6px">当前视频预览：</div>
                <video
                  :src="videoPreviewUrl"
                  controls
                  style="
                    width: 320px;
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px #f0f1f2;
                  "
                />
              </div>
              <div style="display: flex; align-items: flex-end; margin-bottom: 20px">
                <!-- 左侧按钮 -->
                <div style="display: flex; align-items: flex-end">
                  <a-button
                    type="primary"
                    style="margin-top: 20px"
                    @click="handlePredict"
                    >开始识别</a-button
                  >
                  <a-button danger style="margin-left: 12px" @click="handleClearPrediction">重置结果</a-button>
                  <a-button
                    type="primary"
                    :loading="loading"
                    style="margin-top: 20px;margin-left: 12px"
                    @click="handleAsk"
                    :disabled="question==''"
                  >获取智能评价</a-button>
                </div>
              </div>
            </a-form>
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
            <div v-if="answer" style="margin-top: 24px;">
              <a-typography-title :level="5">AI答复</a-typography-title>
              <div style="background: #fafafa; padding: 14px 18px; border-radius: 6px;">
                <a-typography-paragraph>
                  <div v-html="formatAnswer(answer)"></div>
                </a-typography-paragraph>
              </div>
            </div>
          </a-card>
          <a-card
            v-if="store.selectedVideoStyle === 'CSL测试集'"
            title="选择测试视频"
            :bordered="false"
            style="margin-bottom: 24px"
          >
            <a-form layout="vertical">
              <a-form-item label="选择测试视频">
                <a-select
                  v-model:value="store.selectedCSLVideo"
                  :options="cslVideoOptions"
                  placeholder="选择测试视频"
                  style="width: 220px"
                />
              </a-form-item>

              <div v-if="videoPreviewUrl" style="margin-top: 16px">
                <div style="font-size: 13px; margin-bottom: 6px">当前视频预览：</div>
                <video
                  :src="videoPreviewUrl"
                  controls
                  style="
                    width: 320px;
                    max-width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px #f0f1f2;
                  "
                />
              </div>
            </a-form>
            <div style="display: flex; align-items: flex-end; margin-bottom: 20px">
              <!-- 左侧按钮 -->
              <div style="display: flex; align-items: flex-end">
                <a-button
                  type="primary"
                  style="margin-top: 20px"
                  @click="handlePredict"
                  >开始识别</a-button
                >
                <a-button danger style="margin-left: 12px" @click="handleClearPrediction"
                  >重置结果</a-button
                >
              </div>
            </div>
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
          </a-card>
        </div>
      </a-layout-content>

      <a-layout-footer style="text-align: center">夜猫子工作室 ©2025</a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { addPracticeRecord, askAi, fullPredict } from '@/api/practiceController.ts'
import { useConfigStore } from '@/stores/cslConfig.ts'
import GlobalSider from '@/components/GlobalSider.vue'
import { predict } from '@/api/predictionController.ts'

const targetText = ref('')
const videoRef = ref<HTMLVideoElement | null>(null)
let stream: MediaStream | null = null
let recorder: MediaRecorder | null = null
const recordedChunks = ref<Blob[]>([])
const recording = ref(false)
const recordedVideo = ref<File | null>(null)
const loading = ref(false)
const aiAdvice = ref('')
const store = useConfigStore()
const previewUrl = ref('')
const predictionParsed = ref<any>(null)
const answer = ref('')
const question = ref('')

const startRecording = async () => {
  stream = await navigator.mediaDevices.getUserMedia({ video: true })
  if (videoRef.value) videoRef.value.srcObject = stream
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
}
// 监听 previewUrl 变化，自动切换为预览
watch(previewUrl, (val) => {
  if (videoRef.value) {
    if (val) {
      // 显示录制的文件
      videoRef.value.srcObject = null
      videoRef.value.src = val
      videoRef.value.controls = true
      videoRef.value.autoplay = false
    } else {
      // 切回摄像头
      if (stream) {
        videoRef.value.srcObject = stream
        videoRef.value.controls = false
        videoRef.value.autoplay = true
      }
    }
  }
})

const stopRecording = () => {
  if (recorder && recording.value) {
    recorder.stop()
    console.log('目标', targetText.value, '视频', recordedVideo.value)
    message.success('录制结束')
  }
}

// 注意：后端接口为 /practice/fullPredict，参数 targetText + file
const submitPractice = async () => {
  if (!targetText.value || !recordedVideo.value) {
    message.warning('请填写目标并录制视频')
    return
  }
  loading.value = true
  aiAdvice.value = ''
  try {
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
    // res: AxiosResponse<{ prediction: string, aiAdvice: string }>
    if (res.data.prediction) {
      try {
        predictionParsed.value = JSON.parse(res.data.prediction)
      } catch {
        predictionParsed.value = null
      }
    }
    console.log('AI建议完整返回：', res)
    aiAdvice.value = res.data.aiAdvice || 'AI未返回建议'
    console.log(predictionParsed.value.filename)
    console.log(res.data)
    await addPracticeRecord({
      targetText: targetText.value,
      aiAdvice: aiAdvice.value,
      predictJson: res.data.prediction,
      videoUrl: 'http://localhost:8000/videos/' + predictionParsed.value.filename,
    })
    message.success('已获取AI建议并保存记录')
  } catch (e: any) {
    console.error('提交出错', e)
    if (e.response && e.response.data) {
      aiAdvice.value = e.response.data.aiAdvice || e.response.data || e.message
    }
    message.error('提交失败，请重试')
  } finally {
    loading.value = false
  }
}
function formatAdvice(text: string) {
  // 将AI建议的 ### 换成大号字体
  if (!text) return ''
  return text.replace(/###/g, '<br/><b style="font-size:16px;">▪</b> ').replace(/\n/g, '<br/>')
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
      question.value="上传视频文件，通过算法预测结果为"+res.data.results+",请给出合理的智能指导意见。"
      console.log(question.value)
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
const handleClearPrediction = () => {
  store.setPrediction(null)
}
watch(
  () => store.selectedModel,
  (val) => {
    store.setPrediction(null) // 清空预测结果
  },
  { immediate: true },
)
const videoPreviewUrl = computed(() => {
  if (store.selectedVideoStyle === '上传视频' && store.uploadedVideo) {
    return URL.createObjectURL(store.uploadedVideo)
  }
  if (store.selectedVideoStyle === 'CSL测试集' && store.selectedCSLVideo) {
    return `/data/ptov/${store.selectedCSLVideo}`
  }
  return ''
})
const handleUpload = async ({ file }: { file: File }) => {
  store.setUploadedVideo(file)
}
function formatAnswer(text: string) {
  if (!text) return ''
  // 可对AI返回做简单格式化（如带markdown的再完善）
  return text.replace(/###/g, '<br/><b style="font-size:16px;">▪</b> ').replace(/\n/g, '<br/>')
}
const cslVideoOptions = computed(() =>
  store.cslVideos.map((video) => ({ value: video, label: video })),
)
</script>

<style scoped>
.practice-main {
  max-width: 620px;
  margin: 36px auto;
}

.sider {
  background: #fff;
  padding-top: 20px;
  border-right: 0.5px solid #eee;
}
</style>

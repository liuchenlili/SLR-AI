<template>
  <div class="ai-qna-main">
    <a-card title="AI手语问答助手" :bordered="false">
      <a-form layout="vertical" @submit.prevent>
        <a-form-item label="请输入你的问题">
          <a-textarea
            v-model:value="question"
            rows="3"
            placeholder="比如：‘“团结”手语怎么做？’ 或 ‘如何提高手语学习效率？’"
            @keydown.enter.exact.prevent="handleAsk"
          />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" :loading="loading" @click="handleAsk" :disabled="!question">
            提问
          </a-button>
        </a-form-item>
      </a-form>
      <div v-if="answer" style="margin-top: 24px;">
        <a-typography-title :level="5">AI答复</a-typography-title>
        <div style="background: #fafafa; padding: 14px 18px; border-radius: 6px;">
          <a-typography-paragraph>
            <div v-html="formatAnswer(answer)"></div>
          </a-typography-paragraph>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { askAi } from '@/api/practiceController' // 按你的api文件实际路径
import { message } from 'ant-design-vue'

const question = ref('')
const answer = ref('')
const loading = ref(false)

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

function formatAnswer(text: string) {
  if (!text) return ''
  // 可对AI返回做简单格式化（如带markdown的再完善）
  return text.replace(/###/g, '<br/><b style="font-size:16px;">▪</b> ').replace(/\n/g, '<br/>')
}
</script>

<style scoped>
.ai-qna-main {
  max-width: 640px;
  margin: 36px auto;
}
</style>

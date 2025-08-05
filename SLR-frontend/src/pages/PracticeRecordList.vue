<template>
  <div id="practiceRecordPage">
    <!-- 搜索表单 -->
    <a-form layout="inline" :model="searchParams" @finish="doSearch">
      <a-form-item label="目标">
        <a-input v-model:value="searchParams.target_text" placeholder="输入练习目标" allow-clear />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit">搜索</a-button>
      </a-form-item>
    </a-form>
    <div style="margin-bottom: 16px" />

    <!-- 练习历史表格 -->
    <a-table
      :columns="columns"
      :data-source="dataList"
      :pagination="pagination"
      rowKey="id"
      @change="doTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'videoUrl'">
          <video :src="record.videoUrl" controls style="width: 120px; border-radius: 6px" />
        </template>
        <template v-else-if="column.dataIndex === 'aiAdvice'">
          <a-button @click="showAdvice(record)" type="primary">查看建议</a-button>
        </template>
        <template v-else-if="column.dataIndex === 'predictJson'">
          <a-popover title="预测详情" trigger="click">
            <template #content>
              <div class="p-4 max-w-md max-h-64 overflow-auto">
                <ul class="space-y-2">
                  <li
                    v-for="(item, index) in formatPredict(record.predictJson)"
                    :key="index"
                    class="relative pl-6"
                  >
                    <span class="absolute left-0 text-blue-600 font-medium">{{ index + 1 }}.</span>
                    <span class="font-medium text-gray-800">{{ item.label }}</span>
                    <span class="text-gray-500 ml-2">-</span>
                    <span class="text-green-600 font-medium">{{ item.confidence }}</span>
                  </li>
                </ul>
              </div>
            </template>
            <a-button type="primary">查看</a-button>
          </a-popover>
        </template>
        <template v-else-if="column.dataIndex === 'createTime'">
          {{ dayjs(record.createTime).format('YYYY-MM-DD HH:mm:ss') }}
        </template>
      </template>
    </a-table>

    <!-- AI建议弹窗 -->
    <a-modal v-model:visible="adviceModalVisible" title="AI 教学建议" footer="">
      <div v-html="formatAdvice(currentAdvice)" />
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive } from 'vue'
import { listMyRecords, listRecordByPage } from '@/api/practiceController'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'

const dataList = ref<API.PracticeRecord[]>([])
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
})
const loginUserStore = useLoginUserStore()
const searchParams = reactive<API.PracticeRecordQueryRequest>({
  current: 1,
  pageSize: 10,
  user_id: loginUserStore.loginUser.id,
  target_text: '',
})

const columns = [
  { title: '目标', dataIndex: 'targetText', key: 'targetText', width: 120 },
  { title: '时间', dataIndex: 'createTime', key: 'createTime', width: 160 },
  { title: '视频', dataIndex: 'videoUrl', key: 'videoUrl', width: 130 },
  { title: 'AI建议', dataIndex: 'aiAdvice', key: 'aiAdvice', width: 80 },
  { title: '预测', dataIndex: 'predictJson', key: 'predictJson', width: 80 },
]

const adviceModalVisible = ref(false)
const currentAdvice = ref('')

/** 格式化 AI建议，支持 markdown 或换行 */
function formatAdvice(text: string) {
  if (!text) return ''
  return text.replace(/###/g, '<br/><b style="font-size:16px;">▪</b> ').replace(/\n/g, '<br/>')
}
/** 格式化预测结果为对象数组 */
function formatPredict(json: string) {
  try {
    const parsed = JSON.parse(json);

    // 检查results是否存在且为数组
    if (Array.isArray(parsed.results)) {
      return parsed.results.map((item, index) => {
        // 处理每个子数组 [label, confidence]
        const label = item[0] || `未知标签${index + 1}`;
        const confidence = item[1] || '0%';

        // 提取百分比数字部分并格式化
        const confidenceNumber = parseFloat(confidence.replace('%', ''));
        return {
          label,
          confidence: `${confidenceNumber.toFixed(3)}%`
        };
      });
    }
    // 如果没有results字段或格式不正确，返回空数组
    return [];
  } catch (error) {
    console.error('JSON解析错误:', error);
    return [];
  }
}

function showAdvice(record: any) {
  currentAdvice.value = formatAdvice(record.aiAdvice)
  adviceModalVisible.value = true
}

async function doSearch() {
  await fetchData()
}
async function doTableChange(pager: any) {
  pagination.value.current = pager.current
  pagination.value.pageSize = pager.pageSize
  await fetchData()
}
async function fetchData() {
  const res = await listRecordByPage({
    ...searchParams,
  })
  console.log(res)
  if (res.data.code === 0 && res.data.data) {
    dataList.value = res.data.data.records ?? []
    pagination.value.total = res.data.data.total ?? 0
  } else {
    message.error('获取历史记录失败')
  }
}
onMounted(fetchData)
</script>

<style scoped>
#practiceRecordPage {
  margin: 10px auto;
  padding: 30px;
}
.ai-advice-content h3 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #1e40af;
}

.ai-advice-content div {
  margin-bottom: 0.75rem;
}

.ai-advice-content strong {
  font-weight: 600;
  color: #374151;
}

.ai-advice-content ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.ai-advice-content li {
  margin-bottom: 0.5rem;
}

.ant-table-thead > tr > th {
  background-color: #f3f4f6 !important;
  color: #1f2937 !important;
  font-weight: 600 !important;
}

.ant-pagination-item-active {
  border-color: #3b82f6 !important;
  background-color: #3b82f6 !important;
}

.ant-pagination-item-active a {
  color: #ffffff !important;
}

.ant-modal-content {
  border-radius: 12px !important;
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
}

.ant-modal-header {
  border-radius: 12px 12px 0 0 !important;
  background-color: #f9fafb !important;
  border-bottom: 1px solid #e5e7eb !important;
}

.ant-modal-title {
  font-weight: 600 !important;
  color: #1f2937 !important;
  font-size: 1.25rem !important;
}
</style>

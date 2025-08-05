<template>
  <div>
    <a-card>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <a-input-search v-model:value="keyword" @search="onSearch" placeholder="输入手语" style="width:320px"/>
        <a-button @click="reloadList" type="link">重置</a-button>
      </div>
      <a-table
        :columns="columns"
        :data-source="wordList"
        :loading="loading"
        row-key="id"
        style="margin-top:18px"
        :pagination="{ pageSize: 8 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'videoUrl'">
            <video :src="record.videoUrl" controls style="width:120px;max-width:100%;border-radius:8px;" />
          </template>
          <template v-if="column.dataIndex === 'action'">
            <a @click="showDetail(record.id)">详情</a>
          </template>
        </template>
      </a-table>
    </a-card>
    <!-- 详情弹窗 -->
    <a-modal v-model:open="detailVisible" title="手语词汇详情" width="480px" :footer="null">
      <div v-if="detailItem">
        <div style="font-size:20px;font-weight:600;">{{ detailItem.word }}</div>
        <video :src="detailItem.videoUrl" controls style="width:92%;margin:10px auto;display:block"/>
        <div><b>动作说明：</b>{{ detailItem.actionDesc }}</div>
        <div style="margin-top:6px;"><b>中文释义：</b>{{ detailItem.chineseMeaning }}</div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getById, listAll, search } from '@/api/signWordController.ts'

const keyword = ref('')
const wordList = ref<any[]>([])
const loading = ref(false)

const columns = [
  { title: '词汇', dataIndex: 'word', key: 'word' },
  { title: '视频', dataIndex: 'videoUrl', key: 'videoUrl' },
  { title: '动作说明', dataIndex: 'actionDesc', key: 'actionDesc', ellipsis: true },
  { title: '中文释义', dataIndex: 'chineseMeaning', key: 'chineseMeaning', ellipsis: true },
  { title: '操作', dataIndex: 'action', key: 'action' },
]

const fetchList = async () => {
  loading.value = true
  try {
    const res = await listAll()
    wordList.value = res.data || []
  } finally {
    loading.value = false
  }
}
const reloadList = async () => {
  keyword.value = ''
  await fetchList()
}
const onSearch = async () => {
  if (!keyword.value) return fetchList()
  loading.value = true
  try {
    const res = await search({ keyword: keyword.value })
    wordList.value = res.data || []
    if (wordList.value.length === 0) message.info('无相关结果')
  } finally { loading.value = false }
}

// 详情弹窗
const detailVisible = ref(false)
const detailItem = ref<any>(null)
const showDetail = async (id: number) => {
  loading.value = true
  try {
    const res = await getById({ id })
    detailItem.value = res.data || null
    detailVisible.value = true
  } finally {
    loading.value = false
  }
}

onMounted(fetchList)
</script>

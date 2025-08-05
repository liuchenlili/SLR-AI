<template>
  <div ref="chartRef" class="echart-line-container"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, nextTick, defineExpose } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import request from '@/request'

echarts.use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer,
])

const props = defineProps<{ dataUrl: string }>()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

// 主动resize方法（暴露给父组件）
const resize = () => {
  nextTick(() => {
    if (chart) chart.resize()
  })
}
defineExpose({ resize })

const renderChart = async () => {
  if (!chartRef.value) return
  const res = await request.get(props.dataUrl)
  const csvLines = res.data
  if (!csvLines || csvLines.length <= 1) return

  // 1. 解析 header
  const header = csvLines[0].split(',') // ['train','val']
  // 2. 解析每一行，得到 [[train, val], ...]
  const dataRows = csvLines.slice(1).map((line: string) => line.split(',').map(Number))
  // 3. x轴为[1,2,3,...]，即第几轮
  const epochs = dataRows.map((_, idx) => idx + 1)
  // 4. 构造 series
  const series = header.map((col, idx) => ({
    name: col,
    type: 'line',
    data: dataRows.map(row => row[idx]),
    smooth: true,
    symbol: 'none',
    lineStyle: {
      width: 3
    }
  }))

  chart = echarts.init(chartRef.value)
  chart.setOption({
    backgroundColor: '#fff',
    tooltip: { trigger: 'axis' },
    legend: {
      data: header,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
      icon: 'rect',
      itemWidth: 18,
      itemHeight: 8,
      textStyle: {
        fontSize: 15,
        fontWeight: 400,
      },
    },
    xAxis: {
      type: 'category',
      data: epochs,
      name: '', // 或 'epoch'
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#bfc1c4' } },
      axisLabel: { fontSize: 14, color: '#505366', margin: 8 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      splitNumber: 5,
      axisLine: { lineStyle: { color: '#bfc1c4' } },
      axisLabel: { fontSize: 14, color: '#505366' },
      splitLine: { lineStyle: { type: 'dashed', color: '#e5e7eb' } }
    },
    grid: { left: 48, right: 32, top: 24, bottom: 60 },
    series,
  })
}

onMounted(renderChart)
watch(() => props.dataUrl, () => {
  if (chart) chart.dispose()
  renderChart()
})
</script>

<style scoped>
.echart-line-container {
  width: 100%;
  height: 360px;
  background: #fff;
  border-radius: 6px;
}
</style>

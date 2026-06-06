<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { createChart, AreaSeries, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'
import { useData } from '../composables/useData'

const chartContainer = ref<HTMLDivElement>()
let chart: IChartApi | null = null
let seriesMap = new Map<string, ISeriesApi<'Area'>>()

const { selectedSeries, timeRange } = useData()

const COLORS = [
  '#2962ff', '#ff6d00', '#00e676', '#d500f9',
  '#ff1744', '#00b0ff', '#ffd600', '#1de9b6',
]

function filterByRange(data: { time: string; value: number }[]) {
  if (timeRange.value === 'all') return data
  const now = new Date()
  let cutoff: Date
  switch (timeRange.value) {
    case '1d': cutoff = new Date(now.getTime() - 86400000); break
    case '1w': cutoff = new Date(now.getTime() - 7 * 86400000); break
    case '1m': cutoff = new Date(now.getTime() - 30 * 86400000); break
    case '3m': cutoff = new Date(now.getTime() - 90 * 86400000); break
    case '6m': cutoff = new Date(now.getTime() - 180 * 86400000); break
    default: return data
  }
  return data.filter(d => new Date(d.time) >= cutoff)
}

function initChart() {
  if (!chartContainer.value) return
  chart = createChart(chartContainer.value, {
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a2e' },
      textColor: '#6b7f99',
    },
    grid: {
      vertLines: { color: '#1f2937' },
      horzLines: { color: '#1f2937' },
    },
    crosshair: { mode: 0 },
    rightPriceScale: { borderColor: '#2a3240' },
    timeScale: {
      borderColor: '#2a3240',
      timeVisible: true,
      secondsVisible: false,
    },
    handleScale: { axisPressedMouseMove: true },
    handleScroll: { vertTouchDrag: false },
  })
}

function renderSeries() {
  if (!chart) return

  for (const [, s] of seriesMap) {
    chart.removeSeries(s)
  }
  seriesMap.clear()

  selectedSeries.value.forEach((s, i) => {
    const filtered = filterByRange(s.data)
    const color = COLORS[i % COLORS.length]
    const areaSeries = chart!.addSeries(AreaSeries, {
      lineColor: color,
      topColor: color + '33',
      bottomColor: color + '05',
      lineWidth: 2,
      title: s.name,
    })
    areaSeries.setData(filtered.map(d => ({
      time: d.time.replace(' ', 'T'),
      value: d.value,
    })))
    seriesMap.set(s.key, areaSeries)
  })

  chart.timeScale().fitContent()
}

watch([selectedSeries, timeRange], () => {
  renderSeries()
}, { deep: true })

let ro: ResizeObserver | null = null

onMounted(() => {
  initChart()
  renderSeries()
  if (chartContainer.value) {
    ro = new ResizeObserver(() => {
      if (chart && chartContainer.value) {
        chart.applyOptions({
          width: chartContainer.value.clientWidth,
          height: chartContainer.value.clientHeight,
        })
      }
    })
    ro.observe(chartContainer.value)
  }
})

onUnmounted(() => {
  ro?.disconnect()
  chart?.remove()
  chart = null
})
</script>

<template>
  <div ref="chartContainer" class="flex-1 w-full" />
</template>

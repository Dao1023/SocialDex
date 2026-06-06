import { ref, computed } from 'vue'
import type { DexData, StockItem, TimeRange } from '../types'

const data = ref<DexData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const selectedKeys = ref<string[]>([])
const timeRange = ref<TimeRange>('all')

export function useData() {
  async function load() {
    loading.value = true
    error.value = null
    try {
      const resp = await fetch('./data.json')
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      data.value = await resp.json()
      if (data.value) {
        selectedKeys.value = ['index:蓝筹100']
      }
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  function getName(key: string): string {
    if (key.startsWith('tag:')) return key.slice(4)
    if (key.startsWith('author:')) return key.slice(7)
    if (key.startsWith('index:')) return key.slice(6)
    return key
  }

  const stockItems = computed<StockItem[]>(() => {
    if (!data.value) return []
    const items: StockItem[] = []
    for (const [key, summary] of Object.entries(data.value.summary)) {
      const kind = key.startsWith('tag:') ? 'tag'
        : key.startsWith('author:') ? 'author'
        : 'index'
      items.push({
        key,
        name: getName(key),
        latest: summary.latest,
        change_pct: summary.change_1d_pct,
        kind,
      })
    }
    return items.sort((a, b) => b.change_pct - a.change_pct)
  })

  const selectedSeries = computed(() => {
    if (!data.value) return []
    return selectedKeys.value
      .filter(k => k in data.value!.series)
      .map(k => ({
        key: k,
        name: getName(k),
        data: data.value!.series[k],
      }))
  })

  function toggleKey(key: string) {
    const idx = selectedKeys.value.indexOf(key)
    if (idx >= 0) {
      selectedKeys.value.splice(idx, 1)
    } else {
      selectedKeys.value.push(key)
    }
  }

  function selectKey(key: string) {
    selectedKeys.value = [key]
  }

  return {
    data,
    loading,
    error,
    selectedKeys,
    timeRange,
    stockItems,
    selectedSeries,
    load,
    getName,
    toggleKey,
    selectKey,
  }
}

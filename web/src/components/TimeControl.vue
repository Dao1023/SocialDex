<script setup lang="ts">
import { useData } from '../composables/useData'
import type { TimeRange } from '../types'

const { timeRange } = useData()

const ranges: { label: string; value: TimeRange }[] = [
  { label: '1天', value: '1d' },
  { label: '1周', value: '1w' },
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '全部', value: 'all' },
]
</script>

<template>
  <div class="flex items-center gap-1 px-4 py-2 border-t border-base-300 bg-base-100">
    <button
      v-for="r in ranges"
      :key="r.value"
      class="btn btn-xs"
      :class="timeRange === r.value ? 'btn-primary' : 'btn-ghost'"
      @click="timeRange = r.value"
    >
      {{ r.label }}
    </button>
  </div>
</template>

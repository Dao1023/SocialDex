<script setup lang="ts">
import { ref, computed } from 'vue'
import { useData } from '../composables/useData'
import type { StockItem } from '../types'

const { stockItems, selectedKeys, selectKey, toggleKey } = useData()

type Filter = 'all' | 'tag' | 'author' | 'index'
const filter = ref<Filter>('all')

const filteredItems = computed(() => {
  if (filter.value === 'all') return stockItems.value
  return stockItems.value.filter(i => i.kind === filter.value)
})

function isSelected(key: string): boolean {
  return selectedKeys.value.includes(key)
}

function handleClick(item: StockItem, e: MouseEvent) {
  if (e.ctrlKey || e.metaKey) {
    toggleKey(item.key)
  } else {
    selectKey(item.key)
  }
}

function formatChange(pct: number): string {
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}
</script>

<template>
  <div class="h-full flex flex-col">
    <div class="px-3 py-2 text-xs font-semibold opacity-50 uppercase">自选行情</div>

    <div class="tabs tabs-bordered px-2 text-xs mb-1">
      <a class="tab" :class="{ 'tab-active': filter === 'all' }" @click="filter = 'all'">全部</a>
      <a class="tab" :class="{ 'tab-active': filter === 'index' }" @click="filter = 'index'">指数</a>
      <a class="tab" :class="{ 'tab-active': filter === 'tag' }" @click="filter = 'tag'">板块</a>
      <a class="tab" :class="{ 'tab-active': filter === 'author' }" @click="filter = 'author'">个股</a>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div
        v-for="item in filteredItems"
        :key="item.key"
        class="px-3 py-2 cursor-pointer border-b border-base-200 hover:bg-base-200 transition-colors"
        :class="{ 'bg-base-200': isSelected(item.key) }"
        @click="handleClick(item, $event)"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium truncate">{{ item.name }}</span>
          <span
            class="text-xs font-mono"
            :class="item.change_pct >= 0 ? 'text-red-400' : 'text-green-400'"
          >
            {{ formatChange(item.change_pct) }}
          </span>
        </div>
        <div class="text-xs opacity-50 font-mono mt-0.5">
          {{ item.latest.toFixed(2) }} 万
        </div>
      </div>
    </div>
  </div>
</template>

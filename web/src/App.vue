<script setup lang="ts">
import { onMounted } from 'vue'
import { useData } from './composables/useData'
import Sidebar from './components/Sidebar.vue'
import ChartPanel from './components/ChartPanel.vue'
import TimeControl from './components/TimeControl.vue'

const { data, loading, error, load } = useData()

onMounted(() => load())
</script>

<template>
  <div class="h-full flex flex-col" data-theme="dark">
    <div class="navbar bg-base-100 border-b border-base-300 px-4 min-h-[48px]">
      <div class="flex-1 gap-2">
        <span class="text-lg font-bold">SocialDex</span>
        <span class="text-xs opacity-40">社会思潮指数 - 基于自媒体粉丝量的板块轮动观察</span>
      </div>
      <div class="flex-none">
        <span v-if="data" class="text-xs opacity-40">
          更新至 {{ data.meta.updated_at.replace('T', ' ').slice(0, 16) }}
        </span>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <aside class="w-56 border-r border-base-300 bg-base-100 flex-shrink-0">
        <Sidebar />
      </aside>

      <main class="flex-1 flex flex-col bg-[#1a1a2e]">
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <div v-else-if="error" class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <p class="text-xl mb-2">数据加载失败</p>
            <p class="text-sm opacity-50">{{ error }}</p>
          </div>
        </div>

        <template v-else>
          <ChartPanel />
          <TimeControl />
        </template>
      </main>
    </div>
  </div>
</template>

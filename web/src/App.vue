<script setup lang="ts">
</script>

<template>
  <div class="h-full flex flex-col" data-theme="dark">
    <div class="navbar bg-base-100 border-b border-base-300 px-4 min-h-[48px]">
      <div class="flex-1 gap-2">
        <span class="text-lg font-bold">SocialDex</span>
        <span class="text-xs opacity-40">社会思潮指数</span>
      </div>
      <div class="flex-none">
        <span class="text-xs opacity-40">加载中...</span>
      </div>
    </div>
    <div class="flex flex-1 overflow-hidden">
      <div class="w-56 border-r border-base-300 bg-base-100 overflow-y-auto">
        <!-- Sidebar placeholder -->
      </div>
      <div class="flex-1 flex flex-col">
        <div class="flex-1 flex items-center justify-center opacity-30">
          加载中...
        </div>
      </div>
    </div>
  </div>
</template>

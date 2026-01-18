<template>
  <div class="flex items-center gap-3">
    <img src="/logo.png" alt="Team ShortCut" :class="sizeClass" />
    <span v-if="showText" :class="textClass">Team ShortCut</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showText: true,
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-8 w-auto'
    case 'lg':
      return 'h-16 w-auto'
    default:
      return 'h-12 w-auto'
  }
})

const textClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-lg font-bold text-blue-400'
    case 'lg':
      return 'text-3xl font-bold text-blue-400'
    default:
      return 'text-xl font-bold text-blue-400'
  }
})
</script>

<template>
  <div class="flex items-center gap-2">
    <img
      v-if="rankImage"
      :src="rankImage"
      :alt="`${tier} ${division}`"
      class="w-8 h-8 object-contain flex-shrink-0"
    />
    <span class="font-semibold" :class="textColor">
      {{ displayText }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  tier: string | null
  division?: string | null
  lp?: number | null
  showLp?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLp: true
})

const rankImages: Record<string, string> = {
  'IRON': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-iron.png',
  'BRONZE': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-bronze.png',
  'SILVER': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-silver.png',
  'GOLD': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-gold.png',
  'PLATINUM': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-platinum.png',
  'EMERALD': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-emerald.png',
  'DIAMOND': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-diamond.png',
  'MASTER': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-master.png',
  'GRANDMASTER': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-grandmaster.png',
  'CHALLENGER': 'https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/ranked-mini-regalia/ranked-mini-regalia-challenger.png'
}

const rankImage = computed(() => {
  if (!props.tier) return null
  return rankImages[props.tier.toUpperCase()] || null
})

const displayText = computed(() => {
  if (!props.tier) return 'Unranked'

  let text = props.tier
  if (props.division && props.tier !== 'MASTER' && props.tier !== 'GRANDMASTER' && props.tier !== 'CHALLENGER') {
    text += ` ${props.division}`
  }
  if (props.showLp && props.lp !== null && props.lp !== undefined) {
    text += ` - ${props.lp} LP`
  }
  return text
})

const textColor = computed(() => {
  if (!props.tier) return 'text-gray-500'

  const tierColors: Record<string, string> = {
    'IRON': 'text-gray-400',
    'BRONZE': 'text-amber-600',
    'SILVER': 'text-gray-300',
    'GOLD': 'text-yellow-400',
    'PLATINUM': 'text-cyan-400',
    'EMERALD': 'text-emerald-400',
    'DIAMOND': 'text-blue-400',
    'MASTER': 'text-purple-400',
    'GRANDMASTER': 'text-red-400',
    'CHALLENGER': 'text-orange-400'
  }

  return tierColors[props.tier.toUpperCase()] || 'text-gray-400'
})
</script>
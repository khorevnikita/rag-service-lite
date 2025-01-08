<template>
  <div>
    <el-input :model-value="settingValue" readonly />
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { SettingType } from '@/stores/settings'

defineProps({
  settingKey: {
    type: String as () => SettingType,
    required: true
  },
  settingValue: {
    type: String,
    required: false
  }
})
</script>

<style scoped></style>

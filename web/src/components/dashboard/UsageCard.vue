<template>
  <el-card>
    <div class="text-xsmall light-gray mb-1">{{ t('dashboard_usage') }}</div>
    <h2 class="mb-2">
      {{ roundExpense(spentCurrentMonth) }} /
      <span class="text-small">{{ roundExpense(spentTotal) }}</span>
    </h2>
    <div class="flex align-center column-gap-2 text-small light-gray">
      {{ t('dashboard_usage_sent_last_month', { amount: roundExpense(spentPreviousMonth) }) }}
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { roundExpense } from '@/plugins/helper'
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  spentCurrentMonth: {
    type: Number,
    default: 0
  },
  spentPreviousMonth: {
    type: Number,
    default: 0
  },
  spentTotal: {
    type: Number,
    default: 0
  }
})

const { t } = useI18n()
</script>

<style scoped lang="css"></style>

<template>
  <div class="mb-main-xs">
    <div class="flex justify-between align-center mb-4">
      <h4 class="text-h1">{{ t('token_usage') }}</h4>
    </div>

    <UsageLogList class="mb-2" />
  </div>
</template>

<script setup lang="ts">
import UsageLogList from '@/components/usage/UsageLogList.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<style scoped lang="scss"></style>

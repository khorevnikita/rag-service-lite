<template>
  <div class="flex column-gap-2 row-gap-1 flex-wrap">
    <el-tag :type="document.status === 'queued' ? '' : 'info'">{{ t('document_queued') }}</el-tag>
    <el-tag :type="document.status === 'reading' ? '' : 'info'">{{ t('document_reading') }}</el-tag>
    <el-tag :type="document.status === 'sliced' ? '' : 'info'">{{ t('document_indexing') }}</el-tag>
    <el-tag
      v-if="document.status !== 'failed'"
      :type="document.status === 'read' ? 'success' : 'info'"
    >
      {{ t('document_completed') }}
    </el-tag>
    <el-tag
      v-if="document.status === 'failed'"
      :type="document.status === 'failed' ? 'danger' : 'info'"
    >
      {{ t('document_failed') }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { IDocument } from '@/stores/document'
import { useI18n } from 'vue-i18n'

defineProps({
  document: {
    type: Object as () => IDocument,
    required: true
  }
})
const { t } = useI18n()
</script>

<style scoped></style>

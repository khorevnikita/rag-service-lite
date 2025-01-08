<template>
  <el-card>
    <div class="text-xsmall light-gray mb-1">{{ t('documents') }}</div>
    <h2 class="mb-2">{{ totalDocuments }}</h2>

    <div class="flex column-gap-1 row-gap-1 flex-wrap align-center">
      <el-tooltip effect="dark" :content="t('document_queued')" placement="top-start">
        <el-tag type="info">
          {{ statusDistribution.queued || 0 }}
        </el-tag>
      </el-tooltip>
      <el-icon>
        <ArrowRight />
      </el-icon>
      <el-tooltip effect="dark" :content="t('document_reading')" placement="top-start">
        <el-tag>
          {{ statusDistribution.reading || 0 }}
        </el-tag>
      </el-tooltip>
      <el-icon>
        <ArrowRight />
      </el-icon>
      <el-tooltip effect="dark" :content="t('document_indexing')" placement="top-start">
        <el-tag type="warning">
          {{ statusDistribution.sliced || 0 }}
        </el-tag>
      </el-tooltip>
      <el-icon>
        <ArrowRight />
      </el-icon>
      <el-tooltip effect="dark" :content="t('document_completed')" placement="top-start">
        <el-tag type="success">
          {{ statusDistribution.read || 0 }}
        </el-tag>
      </el-tooltip>

      <el-tooltip effect="dark" :content="t('document_failed')" placement="top-start">
        <el-tag class="ml-auto" type="danger">
          {{ statusDistribution.failed || 0 }}
        </el-tag>
      </el-tooltip>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'

interface IDistribution {
  queued: number
  reading: number
  sliced: number
  read: number
  failed: number
}

defineProps({
  totalDocuments: {
    type: Number,
    default: 0
  },
  statusDistribution: {
    type: Object as () => IDistribution,
    required: true
  }
})

const { t } = useI18n()
</script>

<style scoped lang="scss"></style>

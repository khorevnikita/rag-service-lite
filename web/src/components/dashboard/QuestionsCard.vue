<template>
  <el-card>
    <div class="text-xsmall light-gray mb-1">{{ t('dashboard_questions_graph') }}</div>
    <h2 class="mb-2">
      {{ totalCount }} /
      <span class="text-small">{{ totalDialogsCount }}</span>
    </h2>
    <div class="flex align-center column-gap-2 text-small">
      <div class="success">
        {{ likesCount }}
        <el-icon>
          <ArrowUp />
        </el-icon>
      </div>
      <div class="danger">
        {{ dislikesCount }}
        <el-icon>
          <ArrowDown />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  totalDialogsCount: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  },
  likesCount: {
    type: Number,
    default: 0
  },
  dislikesCount: {
    type: Number,
    default: 0
  }
})

const { t } = useI18n()
</script>

<style scoped lang="scss"></style>

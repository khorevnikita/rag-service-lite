<template>
  <el-card>
    <div class="text-xsmall light-gray mb-1">{{ t('dashboard_document_tag_distribution') }}</div>
    <el-table :data="data">
      <el-table-column prop="id" label="#" width="60" />
      <el-table-column prop="text" :label="t('tag')" />
      <el-table-column prop="count" :label="t('count')" width="80" />
    </el-table>
    <el-pagination
      layout="prev, pager, next"
      :hide-on-single-page="true"
      :page-count="pagesCount"
      v-model:current-page="page"
    />
  </el-card>
</template>

<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const store = useDashboardStore()

const { dashboardData } = storeToRefs(store)
const { t } = useI18n()
const take = 10
const page = ref(1)

const data = computed(() => {
  if (!dashboardData.value) return []
  const d = dashboardData.value.keyword_distribution
  return d.slice((page.value - 1) * take, page.value * take)
})

const pagesCount = computed(() => {
  if (!dashboardData.value) return 1
  return Math.ceil(dashboardData.value.keyword_distribution.length / take)
})
</script>

<style scoped lang="scss"></style>

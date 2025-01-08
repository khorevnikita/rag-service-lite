<template>
  <el-card>
    <div class="text-xsmall light-gray mb-1">Распределение вопросов по тегам</div>
    <el-table :data="data">
      <el-table-column prop="keyword" label="Тег">
        <template #default="{ row }">
          {{ row.keyword || 'Не определено' }}
        </template>
      </el-table-column>
      <el-table-column prop="count" label="Кол-во" width="60" />
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

const store = useDashboardStore()

const { dashboardData } = storeToRefs(store)

const take = 10
const page = ref(1)

const data = computed(() => {
  if (!dashboardData.value) return []
  const d = dashboardData.value.question_keyword_distribution
  return d.slice((page.value - 1) * take, page.value * take)
})

const pagesCount = computed(() => {
  if (!dashboardData.value) return 1
  return Math.ceil(dashboardData.value.question_keyword_distribution.length / take)
})
</script>

<style scoped lang="scss"></style>

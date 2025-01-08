<template>
  <div>
    <div class="mb-4">
      <div class="flex row-gap-2 column-gap-2 flex-wrap mb-3 flex-column flex-md-row">
        <el-date-picker v-model="usageRequest.date_from" :placeholder="t('from_date')" />
        <el-date-picker v-model="usageRequest.date_to" :placeholder="t('from_date')" />
      </div>
      <div>
        <el-button type="primary" @click="onSearch">{{ t('search') }}</el-button>
      </div>
    </div>
    <div>{{ t('found', { count: totalCount }) }}</div>
    <el-table :data="logs" style="width: 100%" stripe>
      <el-table-column prop="created_at" :label="t('date')" width="100">
        <template #default="{ row }">
          {{ moment(row.created_at).format('DD.MM.YYYY HH:mm') }}
        </template>
      </el-table-column>
      <el-table-column prop="source_key" :label="t('usage_subject')" min-width="100" />
      <el-table-column prop="operation" :label="t('usage_operation')" min-width="100" />
      <el-table-column prop="price" :label="t('usage_spent')" min-width="100">
        <template #default="{ row }">
          {{ roundExpense(row.price) }}
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      @current-change="onPageChanged"
      layout="prev, pager, next"
      :page-count="pagesCount"
    />
  </div>
</template>

<script setup lang="ts">
import { useUsageStore } from '@/stores/usage'
import type { IUsageRequest } from '@/stores/usage'
import { storeToRefs } from 'pinia'
import moment from 'moment'
import { ref } from 'vue'
import { roundExpense } from '@/plugins/helper'
import { useI18n } from 'vue-i18n'

const store = useUsageStore()
const { getUsageLogs } = store
const { logs, totalCount, pagesCount } = storeToRefs(store)
const skip = ref(0)
const limit = ref(30)
const { t } = useI18n()
const usageRequest = ref<IUsageRequest>({
  date_from: null,
  date_to: null,
  operation: null,
  document_id: null
})

getUsageLogs(usageRequest.value, skip.value, limit.value)

const onPageChanged = (page: number) => {
  skip.value = (page - 1) * limit.value
  getUsageLogs(usageRequest.value, skip.value, limit.value)
}

const onSearch = () => {
  skip.value = 1
  getUsageLogs(usageRequest.value, skip.value, limit.value)
}
</script>

<style scoped lang="scss"></style>

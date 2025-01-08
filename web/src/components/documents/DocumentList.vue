<template>
  <div>
    <div class="mb-3">
      <div class="flex flex-column flex-md-row row-gap-2 column-gap-2 mb-2">
        <el-input @keydown.enter="onSearch()" v-model="search" :placeholder="t('search')" />
        <el-select v-model="status" :placeholder="t('document_status')">
          <el-option value="" :label="t('all')"></el-option>
          <el-option value="queued" :label="t('document_queued')"></el-option>
          <el-option value="reading" :label="t('document_reading')"></el-option>
          <el-option value="sliced" :label="t('document_indexing')"></el-option>
          <el-option value="read" :label="t('document_completed')"></el-option>
          <el-option value="failed" :label="t('document_failed')"></el-option>
        </el-select>
        <KeywordSelector v-model="tag_filter" :placeholder="t('select_tag')" />
      </div>
      <div>
        <el-button type="primary" @click="onSearch()">{{ t('search') }}</el-button>
      </div>
    </div>
    <div class="mb-2">
      {{ t('found', { count: totalCount }) }}
      <el-button link @click="onSearch()">
        <el-icon>
          <Refresh />
        </el-icon>
      </el-button>
    </div>
    <div class="flex flex-column row-gap-2 mb-2">
      <DocumentListItem :document="document" v-for="(document, i) in documents" :key="i" />
    </div>
    <el-pagination
      @current-change="onPageChanged"
      layout="prev, pager, next"
      :page-count="pagesCount"
    />
  </div>
</template>

<script setup lang="ts">
import { useDocumentStore } from '@/stores/document'
import { storeToRefs } from 'pinia'
import DocumentListItem from '@/components/documents/DocumentListItem.vue'
import { ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import KeywordSelector from '@/components/forms/KeywordSelector.vue'
import { useI18n } from 'vue-i18n'

const store = useDocumentStore()
const { t } = useI18n()
const { getDocuments } = store
const { documents, pagesCount, totalCount } = storeToRefs(store)

const search = ref('')
const tag_filter = ref<string[]>([])
const status = ref<string>('')
const skip = ref(0)
const limit = ref(10)

const onPageChanged = (page: number) => {
  skip.value = (page - 1) * limit.value
  getDocuments(
    {
      search: search.value,
      keywords: tag_filter.value,
      status: status.value
    },
    skip.value,
    limit.value
  )
}

const onSearch = () => {
  skip.value = 0
  getDocuments(
    {
      search: search.value,
      keywords: tag_filter.value,
      status: status.value
    },
    skip.value,
    limit.value
  )
}

getDocuments(
  {
    search: search.value
  },
  skip.value,
  limit.value
)
</script>

<style scoped lang="scss"></style>

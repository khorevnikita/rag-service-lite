<template>
  <div class="flex flex-wrap row-gap-1 column-gap-2">
    <el-button v-if="document.url" class="m-0" link @click="download(document.url)" target="_blank"
      >{{ t('document_source_file') }}
    </el-button>
    <el-button
      v-if="document.content_url"
      class="m-0"
      link
      @click="download(document.content_url)"
      target="_blank"
      >{{ t('document_text_file') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { IDocument } from '@/stores/document'
import { download } from '@/plugins/storage'
import { useI18n } from 'vue-i18n'

defineProps({
  document: {
    type: Object as () => IDocument,
    required: true
  }
})

const { t } = useI18n()
</script>

<style scoped lang="scss"></style>

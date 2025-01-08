<template>
  <el-card>
    <p class="text-bold mb-2 break-word">
      {{
        t('document_title', {
          id: document.id,
          name: document.name,
          created_at: moment(document.created_at).format('DD.MM.YYYY')
        })
      }}
    </p>
    <div class="mb-3" v-if="document.keywords">
      <el-tag
        class="mr-2"
        size="small"
        effect="dark"
        round
        v-for="keyword in document.keywords"
        :key="keyword"
      >
        {{ keyword }}
      </el-tag>
    </div>
    <DocumentLinks class="mb-2" :document="document" />
    <div class="mb-2">
      <p>
        {{ t('paragraphs_count', { count: document.paragraphs_count }) }}
      </p>
      <!--
      <p>
        Количество обучающих пар: <b class="mr-1">{{ document.tunes_count }}</b>
      </p>
      -->
    </div>

    <p class="text-bold mb-1">{{ t('status') }}</p>
    <DocumentStatus :document="document" class="mb-2" />
    <el-divider />
    <div class="flex justify-between">
      <router-link class="el-button" :to="`/documents/${document.id}`">{{ t('more') }}</router-link>
      <el-button link @click="onDelete">
        <el-icon>
          <Delete />
        </el-icon>
        &nbsp; {{ t('delete') }}
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'
import moment from 'moment'
import { defineProps } from 'vue'
import type { IDocument } from '@/stores/document'
import { useDocumentStore } from '@/stores/document'
import DocumentStatus from '@/components/documents/elemets/DocumentStatus.vue'
import DocumentLinks from '@/components/documents/elemets/DocumentLinks.vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  document: {
    type: Object as () => IDocument,
    required: true
  }
})

const store = useDocumentStore()
const { destroy } = store
const { t } = useI18n()

const onDelete = () => {
  if (confirm(t('document_delete_confirmation', { id: props.document.id }))) {
    destroy(props.document)
  }
}
</script>

<style scoped lang="scss"></style>

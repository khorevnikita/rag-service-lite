<template>
  <div>
    <div class="mb-4">
      <FileUploader
        :show-file-list="false"
        class="mb-6"
        v-model="uploads"
        :hint="t('file_uploader_hint', { file_ext: '.pdf', size_value: 10 })"
        :on-change="onUploadChange"
      />
      <div class="mb-2">
        <p>{{ t('common_tags') }}</p>
        <KeywordSelector
          allow-create
          v-model="commonTags"
          :placeholder="t('common_tags_placeholder')"
        />
      </div>
    </div>
    <p class="mb-3" v-if="uploads.length > 0">{{ t('uploads') }}</p>
    <div>
      <div class="mb-2 flex column-gap-1" v-for="file in createRequest" :key="file.url">
        <el-input v-model="file.name" :placeholder="t('document_name')" />
        <KeywordSelector
          allow-create
          v-model="file.keywords"
          :placeholder="t('document_tags_placeholder')"
        />
        <el-button link @click="remove(file)">
          <el-icon>
            <Delete />
          </el-icon>
        </el-button>
      </div>
    </div>
    <p class="danger mb-2" v-if="errorMsg.length > 0">{{ errorMsg }}</p>
    <div class="flex column-gap-1">
      <el-button
        :disabled="createRequest.length === 0 || uploadingCount > 0"
        type="primary"
        @click="save()"
      >
        {{ t('save') }}
      </el-button>
      <div style="height: 32px">
        <PreLoader v-if="uploadingCount > 0" class="ml-2" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, ref, watch } from 'vue'
import { useDocumentStore } from '@/stores/document'
import type { ICreateDocumentRequest } from '@/stores/document'
import FileUploader from '@/components/forms/FileUploader.vue'
import KeywordSelector from '@/components/forms/KeywordSelector.vue'
import { Delete } from '@element-plus/icons-vue'
import PreLoader from '@/components/layout/PreLoader.vue'
import type { IUploadData } from '@/plugins/storage'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['created'])
const store = useDocumentStore()
const { createDocument } = store
const { t } = useI18n()
const uploads = ref<IUploadData[]>([])
const createRequest = ref<ICreateDocumentRequest[]>([])
const commonTags = ref<string[]>([])
const errorMsg = ref('')

const formRequest = () => {
  createRequest.value = uploads.value.map((upload: IUploadData, i: number) => {
    const keywords = [...commonTags.value, ...(createRequest.value[i].keywords || [])]
    return {
      name: upload.filename,
      url: upload.file_path,
      keywords: keywords
    }
  })
}

const save = async () => {
  formRequest()
  try {
    errorMsg.value = ''
    for (let req of createRequest.value) {
      await createDocument(req)
    }
    emit('created')
  } catch (e: any) {
    const body = e.response.data
    const msg = body.detail[0].msg
    console.log('cant save', msg)
    errorMsg.value = msg
  }
}

watch(
  uploads,
  () => {
    uploads.value.forEach((upload: IUploadData, i: number) => {
      if (!createRequest.value[i]) {
        createRequest.value[i] = {
          name: upload.filename,
          url: upload.file_path,
          keywords: []
        }
      }
    })
  },
  { deep: true }
)

const remove = (file: ICreateDocumentRequest) => {
  const idx = createRequest.value.indexOf(file)
  if (idx >= 0) {
    createRequest.value.splice(idx, 1)
  }
}

const uploadingCount = ref(0)
const onUploadChange = (a: any) => {
  if (['uploading', 'ready'].includes(a.status)) {
    uploadingCount.value++
  } else if (uploadingCount.value > 0) {
    uploadingCount.value--
  }
}
</script>

<style scoped lang="scss"></style>

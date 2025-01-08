<template>
  <div>
    <div class="mb-2 flex flex-wrap" v-if="request.files && request.files.length">
      <el-tag
        class="mr-2 mb-1"
        v-for="f in request.files"
        :key="f.file_path"
        closable
        :disable-transitions="false"
        @close="removeFile(f)"
      >
        {{ f.filename }}
      </el-tag>
    </div>
    <div class="flex column-gap-4 row-gap-2 align-center input-form">
      <el-input
        class="input-form-text order-2 order-md-0"
        :disabled="loading"
        v-model="request.text"
        type="text"
        :placeholder="t('new_question')"
        @keydown.enter="submit()"
      />
      <FileUploader
        v-model="request.files"
        :show-file-list="false"
        :drag="false"
        :on-change="onUploadChange"
        class="input-form-file"
      >
        <template #default>
          <el-button>
            <el-icon>
              <upload-filled />
            </el-icon>
          </el-button>
        </template>
      </FileUploader>

      <el-button class="input-form-submit" :disabled="loading" type="primary" @click="submit()">
        {{ t('send') }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuestionStore } from '@/stores/question'
import type { IQuestion } from '@/stores/question'
import type { ICreateQuestionRequest } from '@/stores/question'
import { defineEmits, defineProps, ref } from 'vue'
import FileUploader from '@/components/forms/FileUploader.vue'
import { UploadFilled } from '@element-plus/icons-vue'
import type { IUploadData } from '@/plugins/storage'
import { useI18n } from 'vue-i18n'

const questionStore = useQuestionStore()
const { createQuestion } = questionStore
const { t } = useI18n()

const props = defineProps({
  conversationId: {
    type: Number
  }
})

const emit = defineEmits(['sent'])
const request = ref<ICreateQuestionRequest>({
  text: '',
  conversation_id: props.conversationId,
  stream: true,
  files: []
})

const loading = ref(false)

const submit = () => {
  loading.value = true
  createQuestion(request.value)
    .then((question: IQuestion) => {
      emit('sent', question)
    })
    .finally(() => {
      request.value.text = ''
      request.value.files = []
      loading.value = false
    })
}

const uploadingCount = ref(0)
const onUploadChange = (a: any) => {
  if (['uploading', 'ready'].includes(a.status)) {
    uploadingCount.value++
  } else if (uploadingCount.value > 0) {
    uploadingCount.value--
  }

  loading.value = uploadingCount.value > 0
}

const removeFile = (f: IUploadData) => {
  const idx = request.value.files?.findIndex((i) => i.file_path === f.file_path)
  if (idx && idx >= 0) {
    request.value.files?.splice(idx, 1)
  }
}
</script>

<style scoped lang="scss">
.input-form {
  flex-wrap: wrap;
  justify-content: space-between;
  column-gap: 12px;

  &-file {
  }

  @media (min-width: 980px) {
    flex-wrap: nowrap;
    row-gap: 12px;
    &-text {
      order: 1;
    }

    &-submit {
      order: 2;
    }
  }
}
</style>

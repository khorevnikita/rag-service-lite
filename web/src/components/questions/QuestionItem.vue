<template>
  <div class="flex flex-column row-gap-1">
    <div class="msg">
      <div class="flex justify-between">
        <i>
          {{ moment(question.created_at).format('DD.MM.YYYY HH:mm') }}
        </i>
        <el-tag round>
          {{ question.mode }}
        </el-tag>
      </div>
      <div class="break-spaces">
        {{ question.text }}
      </div>
      <div class="mt-2" v-if="question.question_files && question.question_files.length > 0">
        <p>{{ t('attached_files') }}:</p>
        <ol style="padding-left: 0" v-for="f in question.question_files" :key="f.id">
          <el-button link role="button" @click="download(f.url)" v-if="f.is_private">
            {{ f.name }}
          </el-button>
          <el-button link target="_blank" :href="f.url" v-else>{{ f.name }}</el-button>
        </ol>
      </div>
    </div>
    <div
      class="msg ml-auto answer"
      v-bind:class="{
        liked: question.reaction === 'like',
        disliked: question.reaction === 'dislike'
      }"
    >
      <div v-if="question.answered_at" class="flex justify-between mb-1 flex-wrap">
        <el-tag round type="info" class="mr-1">
          {{ question.model ? question.model.base_model_name : '-' }}
        </el-tag>

        <div class="flex align-center">
          <el-button
            @click="dislike(question)"
            :type="question.reaction === 'dislike' ? 'danger' : 'info'"
            link
          >
            <SvgIcon name="dislike" width="24px" height="18px" />
          </el-button>
          <el-button
            class="ml-1"
            @click="like(question)"
            :type="question.reaction === 'like' ? 'success' : 'info'"
            link
          >
            <SvgIcon name="like" width="24px" height="18px" />
          </el-button>
          <i class="ml-2">{{ moment(question.answered_at).format('DD.MM.YYYY HH:mm') }}</i>
        </div>
      </div>
      <img alt="preloader" style="width: 30px" v-if="!question.answer" :src="SearchPreloader" />
      <vue-markdown v-else :source="question.answer || '-'" />

      <div v-if="question.paragraphs && question.paragraphs.length > 0" class="mt-2">
        <p>
          <b>{{ t('relevant_documents') }}:</b>
        </p>
        <ol style="word-break: break-word">
          <li v-for="paragraph in question.paragraphs" :key="paragraph.id">
            <router-link
              v-if="paragraph.document"
              :to="`/documents/${paragraph.document_id}#${paragraph.id}`"
              >{{ paragraph.document.name }} (#{{ paragraph.id }})
            </router-link>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import { useQuestionStore } from '@/stores/question'
import type { IQuestion } from '@/stores/question'
import moment from 'moment'
import SvgIcon from '@/components/SvgIcon.vue'
import SearchPreloader from '@/assets/searching-preloader.gif'
import VueMarkdown from 'vue-markdown-render'
import { download } from '@/plugins/storage'
import { useI18n } from 'vue-i18n'

defineProps({
  question: {
    type: Object as () => IQuestion,
    required: true
  }
})

const store = useQuestionStore()
const { like, dislike } = store
const { t } = useI18n()
</script>

<style scoped lang="scss">
.msg {
  max-width: 90%;
  padding: 8px;
  border-radius: 8px;
  background: var(--el-color-info-light-9);
  overflow-x: hidden;

  &.answer {
    background: var(--el-color-primary-light-9);
  }

  &.liked {
    background: var(--el-color-success-light-9);
  }

  &.disliked {
    background: var(--el-color-danger-light-9);
  }
}
</style>

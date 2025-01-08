<template>
  <div class="questions">
    <div class="filters">
      <el-button link size="small" v-if="collapse" @click="collapse = false">
        <el-icon>
          <ArrowDown />
        </el-icon>
        &nbsp; {{ t('filter') }}
      </el-button>
      <el-button link size="small" v-if="!collapse" @click="collapse = true">
        <el-icon>
          <ArrowUp />
        </el-icon>
        &nbsp; {{ t('hide') }}
      </el-button>
      <QuestionFilter class="mt-1" @search="search" v-model="request" v-if="!collapse" />
    </div>
    <div class="questions-list">
      <QuestionsList />
    </div>
    <el-card shadow="never" class="form mb-2">
      <CreateQuestionForm @sent="scrollToBottom()" :conversation-id="conversationId" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import QuestionsList from '@/components/questions/QuestionsList.vue'
import CreateQuestionForm from '@/components/questions/CreateQuestionForm.vue'
import { useQuestionStore } from '@/stores/question'
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'
import emitter from '@/plugins/emitter'

const collapse = ref(true)

const store = useQuestionStore()

import type { IQuestionRequest } from '@/stores/question'
import { nextTick, ref } from 'vue'
import QuestionFilter from '@/components/questions/QuestionFilter.vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { getQuestions } = store
const { pagesCount } = storeToRefs(store)
const skip = ref(0)
const limit = ref(10)
const page = ref(1)
const { t } = useI18n()
const route = useRoute()
const conversationId = route.params.id ? Number(route.params.id) : undefined

const request = ref<IQuestionRequest>({
  date_from: null,
  date_to: null,
  model_id: null,
  reaction: null,
  conversation_id: conversationId
})

getQuestions(request.value, skip.value, limit.value).then(() => {
  scrollToBottom()
  listenToScroll()
})

const search = () => {
  skip.value = 0
  getQuestions(request.value, skip.value, limit.value).then(() => {
    nextTick(() => {
      scrollToBottom()
    })
  })
}

const scrollToBottom = () => {
  const chatContainer = document.querySelector('.questions-list')
  if (!chatContainer) return
  chatContainer.scrollTop = chatContainer.scrollHeight
}

const listenToScroll = () => {
  const chatContainer = document.querySelector('.questions-list')
  if (!chatContainer) return
  chatContainer.addEventListener('scroll', () => {
    if (chatContainer.scrollTop < 100) {
      // 100 - это пороговое значение, можно настроить
      onPageChanged()
    }
  })
}

const loading = ref(false)
const onPageChanged = () => {
  if (page.value >= pagesCount.value) return
  if (loading.value) return
  loading.value = true
  page.value++
  skip.value = (page.value - 1) * limit.value
  getQuestions(request.value, skip.value, limit.value, true).then(() => {
    loading.value = false
  })
}

emitter.on('answer-stream', () => {
  scrollToBottom()
})
</script>

<style scoped lang="scss">
.questions {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 144px);
  row-gap: 8px;

  .filters,
  .form {
    flex-shrink: 0;
  }

  .questions-list {
    flex-grow: 1;
    overflow: auto;
  }

  @media (min-width: 980px) {
    height: calc(100vh - 60px);
  }
}
</style>

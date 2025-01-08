<template>
  <div>
    <div class="mb-3">{{ t('found', { count: totalCount }) }}</div>
    <div class="flex flex-column row-gap-2 mb-4">
      <ConversationItem
        v-for="conversation in conversations"
        :key="conversation.id"
        :conversation="conversation"
      />
    </div>
    <el-pagination
      @current-change="onPageChanged"
      layout="prev, pager, next"
      :page-count="pagesCount"
    />
  </div>
</template>

<script setup lang="ts">
import { useConversationStore } from '@/stores/conversation'
import { storeToRefs } from 'pinia'
import ConversationItem from '@/components/conversations/ConversationItem.vue'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const store = useConversationStore()
const { getConversations } = store
const { conversations, totalCount, pagesCount } = storeToRefs(store)
const { t } = useI18n()

const skip = ref(0)
const limit = ref(10)

getConversations(skip.value, limit.value)

const onPageChanged = (p: number) => {
  skip.value = (p - 1) * limit.value
  getConversations(skip.value, limit.value)
}
</script>

<style scoped lang="scss"></style>

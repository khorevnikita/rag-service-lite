<template>
  <router-link class="conversation-link" :to="`/conversations/${conversation.id}`">
    <el-card>
      <h4>{{ conversation.name }}</h4>
      <p>{{ moment(conversation.updated_at).format('DD.MM.YYYY HH:mm') }}</p>
    </el-card>
  </router-link>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { IConversation } from '@/stores/conversation'
import moment from 'moment'

defineProps({
  conversation: {
    type: Object as () => IConversation,
    required: true
  }
})
</script>

<style scoped lang="scss">
.conversation-link {
  text-decoration: none;
}
</style>

<template>
  <div class="mb-main-xs">
    <div class="flex justify-between align-center mb-4">
      <h4 class="text-h1">{{ t('dialogs') }}</h4>
      <el-button type="primary" @click="onNewDialog()">{{ t('new_dialog') }}</el-button>
    </div>
    <p class="text-h1 mb-3">
      <b>{{ t('latest_dialogs') }}</b>
    </p>
    <ConversationsList />
  </div>
</template>

<script setup lang="ts">
import ConversationsList from '@/components/conversations/ConversationsList.vue'
import emitter from '@/plugins/emitter'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const onNewDialog = () => {
  emitter.emit('new-conversation')
}
</script>

<style scoped lang="scss"></style>

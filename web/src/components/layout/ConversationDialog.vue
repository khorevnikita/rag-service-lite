<template>
  <div>
    <CreateQuestionForm />
  </div>
</template>

<script setup lang="ts">
import CreateQuestionForm from '@/components/questions/CreateQuestionForm.vue'
import { defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import emitter from '@/plugins/emitter'

const e = defineEmits(['close'])

const router = useRouter()
emitter.on('answer-stream', (d: any) => {
  e('close')
  if (d) {
    router.push(`/conversations/${d.conversationId}`)
  }
})
</script>

<style scoped lang="scss"></style>

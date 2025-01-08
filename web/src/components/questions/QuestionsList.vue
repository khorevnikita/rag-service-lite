<template>
  <div class="flex flex-column-reverse row-gap-3">
    <QuestionItem v-for="question in questions" :key="question.id" :question="question" />
  </div>
</template>

<script setup lang="ts">
import QuestionItem from '@/components/questions/QuestionItem.vue'
import { useQuestionStore } from '@/stores/question'
import { storeToRefs } from 'pinia'
const store = useQuestionStore()
const { questions } = storeToRefs(store)
</script>

<style scoped lang="scss">
.questions-list {
  overflow-y: auto;
}
</style>

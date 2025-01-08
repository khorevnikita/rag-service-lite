<template>
  <div>
    {{ content }}
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue'
import type { IParagraph } from '@/stores/document'
import { useDocumentStore } from '@/stores/document'

const props = defineProps({
  paragraph: {
    type: Object as () => IParagraph,
    required: true
  }
})

const store = useDocumentStore()
const content = ref('')
const { getParagraphContent } = store

getParagraphContent(props.paragraph).then((c) => (content.value = c))
</script>

<style scoped lang="scss"></style>

<template>
  <el-select
    v-model="value"
    multiple
    filterable
    default-first-option
    :reserve-keyword="false"
    remote
    :remote-method="getKeywords"
    :loading="loading"
    v-bind="$attrs"
    @change="onChange"
  >
    <el-option v-for="item in keywords" :key="item.text" :label="item.text" :value="item.text" />
  </el-select>
</template>

<script setup lang="ts">
import { useKeywordStore } from '@/stores/keyword'
import { storeToRefs } from 'pinia'
import { defineEmits, defineProps, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array as () => string[],
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const keywordStore = useKeywordStore()
const { getKeywords } = keywordStore
const { keywords } = storeToRefs(keywordStore)
const loading = ref(false)
const value = ref<string[]>(props.modelValue)

const onChange = (v: string[]) => {
  emit('update:modelValue', v)
}
</script>

<style scoped lang="scss"></style>

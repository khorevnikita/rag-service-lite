<template>
  <div>
    <el-form>
      <div class="questions-filter">
        <el-date-picker v-model="request.date_from" :placeholder="t('from_date')" />
        <el-date-picker v-model="request.date_to" :placeholder="t('to_date')" />
        <el-select v-model="request.reaction" :placeholder="t('reaction')">
          <el-option :label="t('all')" value="" />
          <el-option :label="t('like')" value="like" />
          <el-option :label="t('dislike')" value="dislike" />
        </el-select>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { defineEmits, defineProps, watch, ref } from 'vue'
import type { IQuestionRequest } from '@/stores/question'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: {
    type: Object as () => IQuestionRequest,
    required: true
  }
})
const emit = defineEmits(['update:modelValue', 'search'])
const { t } = useI18n()
const request = ref<IQuestionRequest>(props.modelValue)

watch(
  request,
  () => {
    emit('update:modelValue', request.value)
    emit('search')
  },
  { deep: true }
)
</script>

<style scoped lang="scss">
.questions-filter {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  row-gap: 8px;
  column-gap: 8px;
}
</style>

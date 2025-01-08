<template>
  <el-upload
    v-bind="$attrs"
    :drag="drag"
    :action="uploadPath"
    :on-success="onUpload"
    :multiple="true"
  >
    <div v-if="drag" class="el-upload__text">Перенесите файл или <em>нажмите для загрузки</em></div>
    <template #tip>
      <div v-if="hint" class="el-upload__tip">{{ hint }}</div>
    </template>
    <slot name="default">
      <el-icon class="el-icon--upload">
        <upload-filled />
      </el-icon>
    </slot>
  </el-upload>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { computed, defineEmits, defineProps, ref, watch } from 'vue'
import type { IUploadData } from '@/plugins/storage'

const props = defineProps({
  modelValue: {
    type: Array as () => IUploadData[],
    default: () => []
  },
  hint: {
    type: String
  },
  drag: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const uploadPath = computed(() => {
  return `${import.meta.env.VITE_APP_ENDPOINT}/api/storage/upload`
})

const uploads = ref<IUploadData[]>(props.modelValue)

const onUpload = (data: IUploadData) => {
  console.log('data', data)
  uploads.value.push(data)
  emit('update:modelValue', uploads.value)
}

watch(
  props,
  () => {
    uploads.value = props.modelValue
  },
  { deep: true }
)
</script>

<style scoped lang="scss"></style>

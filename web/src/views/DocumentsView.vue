<template>
  <div class="mb-main-xs">
    <div class="flex justify-between align-center mb-4">
      <h4 class="text-h1">{{ t('documents') }}</h4>
      <el-button type="primary" @click="createDialog = true">{{ t('create_document') }}</el-button>
    </div>

    <DocumentList />

    <el-dialog width="80%" v-model="createDialog">
      <CreateDocument v-if="createDialog" @created="createDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import DocumentList from '@/components/documents/DocumentList.vue'
import { ref } from 'vue'
import CreateDocument from '@/components/documents/CreateDocument.vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const createDialog = ref(false)
</script>

<style scoped lang="scss"></style>

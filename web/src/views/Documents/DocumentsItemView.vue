<template>
  <div>
    <PreLoader v-if="loading" />
    <div v-else-if="documentItem">
      <el-breadcrumb class="mb-2" separator="/">
        <el-breadcrumb-item :to="{ path: '/documents' }">{{ t('documents') }}</el-breadcrumb-item>
        <el-breadcrumb-item class="break-word">
          {{ documentItem.name || `#${documentItem.id}` }}
        </el-breadcrumb-item>
      </el-breadcrumb>
      <div class="mb-3">
        <h2 class="mb-1 break-word">
          {{ documentItem.name }}
          <el-button link @click="getData()">
            <el-icon>
              <Refresh />
            </el-icon>
          </el-button>
        </h2>

        <div class="mb-3" v-if="documentItem.keywords">
          <el-tag
            class="mr-2"
            size="small"
            effect="dark"
            round
            v-for="keyword in documentItem.keywords"
            :key="keyword"
          >
            {{ keyword }}
          </el-tag>
        </div>
        <vue-markdown
          class="mb-2 break-word text-small"
          v-if="documentItem.meta"
          :source="documentItem.meta"
        />
        <div class="mb-2">
          <p class="text-bold mb-1">{{ t('download_links') }}</p>
          <DocumentLinks :document="documentItem" />
        </div>
        <div class="mb-2">
          <p class="text-bold mb-1">{{ t('status') }}</p>
          <DocumentStatus :document="documentItem" />
        </div>
      </div>
      <div v-if="documentItem.paragraphs">
        <h4 class="mb-2">{{ t('paragraphs') }}</h4>
        <div class="flex flex-column row-gap-1">
          <ParagraphItem
            v-for="(paragraph, i) in documentItem.paragraphs"
            :paragraph="paragraph"
            :key="i"
            :id="paragraph.id"
            :focused="focusId === paragraph.id"
          />
        </div>
      </div>
    </div>

    <el-backtop :right="40" :bottom="40" />
  </div>
</template>

<script setup lang="ts">
import { useDocumentStore } from '@/stores/document'
import { useRoute } from 'vue-router'
import { computed, nextTick, ref } from 'vue'
import { storeToRefs } from 'pinia'
import PreLoader from '@/components/layout/PreLoader.vue'
import DocumentStatus from '@/components/documents/elemets/DocumentStatus.vue'
import ParagraphItem from '@/components/documents/DocumentItem/ParagraphItem.vue'
import { Refresh } from '@element-plus/icons-vue'
import DocumentLinks from '@/components/documents/elemets/DocumentLinks.vue'
import VueMarkdown from 'vue-markdown-render'
import { useI18n } from 'vue-i18n'

const loading = ref(true)

const store = useDocumentStore()
const { getDocumentItem } = store
const { documentItem } = storeToRefs(store)
const { t } = useI18n()
const route = useRoute()

const focusId = computed(() => {
  return Number(route.hash.replace('#', ''))
})

const getData = () => {
  getDocumentItem(Number(route.params.id)).then(() => {
    loading.value = false
    nextTick(() => {
      scrollToFocused()
    })
  })
}
/*
const onMakeQuestions = () => {
  if (!documentItem.value) return
  prepareTuning(documentItem.value).then(() => {
    alert('Запущен процесс подготовки к обучению. Это может занять время.')
  })
}
*/
getData()

const scrollToFocused = () => {
  // Находим элемент по ID
  const element = document.getElementById(String(focusId.value))
  if (element) {
    // Скроллим к элементу
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<style scoped lang="scss"></style>

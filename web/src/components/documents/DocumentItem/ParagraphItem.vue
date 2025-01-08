<template>
  <div class="paragraph">
    <div v-bind:class="{ highlighted: focused }">
      <div class="paragraph-meta">
        <div class="flex column-gap-2">
          <b> #{{ paragraph.id }} </b>
          <el-button type="primary" size="small" @click="contentDialog = true">
            {{ t('open_content') }}
          </el-button>
        </div>
        <div class="flex column-gap-2">
          <el-tag type="success">
            {{ paragraph.status }}
          </el-tag>
        </div>
      </div>
    </div>
    <el-divider />
    <el-dialog v-model="contentDialog">
      <ParagraphContent :paragraph="paragraph" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue'
import type { IParagraph } from '@/stores/document'
import ParagraphContent from '@/components/documents/DocumentItem/ParagraphContent.vue'
import { useI18n } from 'vue-i18n'

defineProps({
  paragraph: {
    type: Object as () => IParagraph,
    required: true
  },
  focused: {
    type: Boolean,
    default: false
  }
})
const { t } = useI18n()
const contentDialog = ref(false)
</script>

<style scoped lang="scss">
.paragraph {
  display: flex;
  flex-direction: column;
  row-gap: 8px;

  &-meta {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    row-gap: 8px;
  }

  &-content {
    display: flex;
    column-gap: 12px;
    flex-flow: column;
    row-gap: 16px;

    @media (min-width: 980px) {
      flex-flow: row;
    }

    &-tunes {
      display: flex;
      flex-direction: column;
      row-gap: 12px;

      @media (min-width: 980px) {
        width: 50%;
      }
    }
  }

  @keyframes highlight {
    0% {
      background-color: var(--el-color-warning-light-5);
    }
    50% {
      background-color: var(--el-color-warning-light-7);
    }
    100% {
      background-color: var(--el-color-warning-light-8);
    }
  }

  .highlighted {
    animation: highlight 1s ease-out;
    background-color: var(--el-color-warning-light-8);
    margin: -8px -16px;
    padding: 8px 16px;
    border-radius: 8px;
  }
}
</style>

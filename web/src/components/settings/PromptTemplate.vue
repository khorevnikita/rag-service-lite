<template>
  <div>
    <el-input
      class="mb-2"
      :placeholder="t('settings_prompt_template')"
      type="textarea"
      v-model="context"
      autosize
    />
    <p
      class="text-xsmall light-gray mb-1"
      v-html="t('settings_prompt_template_hint', { template: '{{prompt}}' })"
    ></p>
    <el-button size="small" type="primary" v-if="changed" @click="save()">{{
      t('save')
    }}</el-button>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { SettingType } from '@/stores/settings'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  settingKey: {
    type: String as () => SettingType,
    required: true
  },
  settingValue: {
    type: String,
    required: true
  }
})

const context = ref(props.settingValue)
const { t } = useI18n()
const store = useSettingsStore()
const { setSetting } = store

const changed = computed(() => {
  return props.settingValue !== context.value
})

const save = () => {
  setSetting(props.settingKey, context.value)
}
</script>

<style scoped></style>

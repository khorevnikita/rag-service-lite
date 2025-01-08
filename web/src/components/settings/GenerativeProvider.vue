<template>
  <div>
    <el-select class="mb-2" :placeholder="t('settings_llm_provider')" v-model="provider">
      <el-option key="openai" label="OpenAI" value="openai" />
    </el-select>
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

const store = useSettingsStore()
const { setSetting } = store
const { t } = useI18n()
const provider = ref(props.settingValue)

const changed = computed(() => {
  return props.settingValue !== provider.value
})

const save = () => {
  setSetting(props.settingKey, provider.value)
}
</script>

<style scoped></style>

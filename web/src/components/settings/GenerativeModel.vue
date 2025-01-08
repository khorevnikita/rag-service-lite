<template>
  <div>
    <el-select class="mb-2" :placeholder="t('settings_llm')" v-model="model">
      <el-option key="gpt-4o-mini" label="GPT-4o mini" value="gpt-4o-mini" />
      <el-option key="gpt-4o" label="GPT-4o" value="gpt-4o" />
    </el-select>
    <el-button size="small" type="primary" v-if="changed" @click="save()"
      >{{ t('save') }}
    </el-button>
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
const model = ref(props.settingValue)

const changed = computed(() => {
  return props.settingValue !== model.value
})

const save = () => {
  setSetting(props.settingKey, model.value)
}
</script>

<style scoped></style>

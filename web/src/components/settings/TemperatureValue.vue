<template>
  <div>
    <el-input class="mb-2" :placeholder="t('settings_temperature')" v-model="temperature" />
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
    default: '0.1'
  }
})

const store = useSettingsStore()
const { setSetting } = store
const { t } = useI18n()
const temperature = ref(props.settingValue)

const changed = computed(() => {
  return props.settingValue !== temperature.value
})

const save = () => {
  setSetting(props.settingKey, temperature.value)
}
</script>

<style scoped></style>

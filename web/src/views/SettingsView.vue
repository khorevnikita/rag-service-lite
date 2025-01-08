<template>
  <div class="mb-main-xs">
    <el-card class="mb-4" v-for="settingKey in settingsKeys" :key="settingKey">
      <p class="text-small mb-2">{{ SETTINGS_LIST[settingKey] }}</p>
      <component
        :is="getSettingComponent(settingKey)"
        :setting-key="settingKey"
        :setting-value="getSettingValue(settingKey)"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import type { IVisibleType } from '@/stores/settings'

const store = useSettingsStore()
const { getSettings, SETTINGS_LIST, getSettingComponent, getSettingValue } = store

getSettings()

const settingsKeys = Object.keys(SETTINGS_LIST) as IVisibleType[]
</script>

<style scoped lang="scss"></style>

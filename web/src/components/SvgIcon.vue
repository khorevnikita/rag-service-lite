<template>
  <span class="slot-container">
    <span class="slot" v-bind:style="{ margin: margin }">
      <slot name="content" />
    </span>
    <span
      v-bind:style="{ width: width, height: height }"
      style="display: inline-flex"
      v-html="icon"
    ></span>
  </span>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue'

const props = defineProps({
  name: String,
  margin: String,
  width: String,
  height: String
})

const icons = Object.fromEntries(
  Object.entries(import.meta.glob('@/assets/icons/**/*.svg', { as: 'raw' })).map(([key, value]) => {
    const filename = key.split('/').pop()?.split('.').shift()
    return [filename, value]
  })
)

const icon = ref('')

if (props.name) {
  const iconName = String(props.name)
  const loadIcon = async () => {
    if (icons[iconName]) {
      icon.value = await icons[iconName]()
    }
  }
  loadIcon()
}
</script>

<style lang="scss">
.slot-container {
  position: relative;
  display: inline-flex;

  .slot {
    position: absolute;
    transform: translate(-50%, -50%);
    left: 50%;
    top: 50%;
    font-style: normal;
  }
}
</style>

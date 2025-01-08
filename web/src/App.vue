<template>
  <el-container>
    <el-header>
      <HeaderComponent />
    </el-header>
    <el-container>
      <el-aside width="200px" v-if="isAuthenticated">
        <SideComponent />
      </el-aside>
      <el-main>
        <RouterView :key="route.path" />
      </el-main>
    </el-container>
    <FooterComponent v-if="isAuthenticated && notInDialog" />
    <MobileMenu v-if="mobileMenu" />
    <el-dialog v-model="newQuestionDialog" :title="t('new_dialog')">
      <ConversationDialog @close="newQuestionDialog = false" />
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import HeaderComponent from '@/components/layout/HeaderComponent.vue'
import SideComponent from '@/components/layout/SideComponent.vue'
import FooterComponent from '@/components/layout/FooterComponent.vue'
import { useAuthStore } from '@/stores/auth'
import { computed, onBeforeMount, ref } from 'vue'
import MobileMenu from '@/components/layout/MobileMenu.vue'
import emitter from '@/plugins/emitter'
import ConversationDialog from '@/components/layout/ConversationDialog.vue'
import { useI18n } from 'vue-i18n'
import Session from 'supertokens-web-js/recipe/session'

const { t } = useI18n()
const authStore = useAuthStore()
const isAuthenticated = ref(false)
onBeforeMount(async () => {
  isAuthenticated.value = await Session.doesSessionExist()
  if (isAuthenticated.value) {
    await authStore.getMe()
  }
})
emitter.on('logout', () => {
  isAuthenticated.value = false
})

const mobileMenu = ref(false)

const route = useRoute()
const notInDialog = computed(() => {
  return route.name !== 'questions'
})

emitter.on('showMenu', (v: any) => {
  mobileMenu.value = Boolean(v)
  if (v) {
    document.body.classList.add('overflow-hidden')
  } else {
    document.body.classList.remove('overflow-hidden')
  }
})

const newQuestionDialog = ref(false)
emitter.on('new-conversation', () => {
  newQuestionDialog.value = true
})
</script>

<style scoped lang="scss">
.el-header {
  display: flex;
  align-items: center;
}

.el-main {
  height: calc(100vh - 60px);
}

.el-aside {
  display: none;

  @media (min-width: 980px) {
    display: block;
    height: calc(100vh - 60px);
    position: sticky;
    top: 12px;
  }
}
</style>

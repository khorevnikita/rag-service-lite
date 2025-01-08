<template>
  <div>
    <h1>{{ t('access_restricted') }}</h1>
    <p class="mb-3">{{ t('access_contact', { email: 'khonikdev@gmail.com' }) }}</p>
    <el-button link @click="onLogout">
      <el-icon>
        <SwitchButton />
      </el-icon>
      &nbsp; {{ t('logout') }}
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { SwitchButton } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore() // Получите экземпляр вашего AuthStore
const { logout } = authStore
const store = useAuthStore()
const { API_TOKEN_VALUE } = storeToRefs(store)
const { t } = useI18n()

if (API_TOKEN_VALUE.value) {
  const router = useRouter()
  router.replace('/')
}

const onLogout = () => {
  if (!confirm('Вы уверены, что хотите выйти из системы?')) return
  logout()
}
</script>

<style scoped lang="scss"></style>

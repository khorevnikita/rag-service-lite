<template>
  <div class="header-items">
    <router-link to="/" class="el-link">
      <el-image :src="Logo" />
    </router-link>
    <div class="flex column-gap-2 items-center">
      <el-dropdown placement="bottom-end">
        <el-button link>
          <SvgIcon :key="locale" :name="locale" width="18px" height="18px" />
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="enableLocale('ru')">
              <SvgIcon name="ru" width="18px" height="18px" />
            </el-dropdown-item>
            <el-dropdown-item @click="enableLocale('en')">
              <SvgIcon name="en" width="18px" height="18px" />
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <el-button class="hidden-sm-and-down" link v-if="isAuthenticated" @click="onLogout">
        {{ t('logout') }}
      </el-button>
      <el-button class="hidden-md-and-up" link v-if="isAuthenticated" @click="onShow">
        <el-icon>
          <Grid />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Logo from '@/assets/logo.svg'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { Grid } from '@element-plus/icons-vue'
import emitter from '@/plugins/emitter'
import { useI18n } from 'vue-i18n'
import SvgIcon from '@/components/SvgIcon.vue'

const authStore = useAuthStore() // Получите экземпляр вашего AuthStore
const { logout } = authStore
const { API_TOKEN_VALUE } = storeToRefs(authStore)
const isAuthenticated = computed(() => !!API_TOKEN_VALUE.value) // Проверьте наличие API токена
const { locale, t } = useI18n()
const onLogout = () => {
  if (!confirm('Вы уверены, что хотите выйти из системы?')) return
  logout()
}

const onShow = () => {
  emitter.emit('showMenu', true)
}

const enableLocale = (l: 'ru' | 'en') => {
  locale.value = l
  localStorage.setItem('locale', l)
}
</script>

<style scoped lang="scss">
.header-items {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  .el-image {
    height: 45px;
  }
}
</style>

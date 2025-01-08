<template>
  <div class="mobile-menu">
    <div class="mobile-menu-header">
      <router-link to="/" class="el-link">
        <el-image :src="Logo" />
      </router-link>
      <el-button link @click="onClose">
        <el-icon>
          <Close />
        </el-icon>
      </el-button>
    </div>
    <div class="mobile-menu-body">
      <router-link to="/" class="el-link" @click="onClose">
        <el-icon>
          <Grid />
        </el-icon>
        <span>{{ t('dashboard') }}</span>
      </router-link>
      <router-link to="/documents" class="el-link" @click="onClose">
        <el-icon>
          <Document />
        </el-icon>
        <span>{{ t('documents') }}</span>
      </router-link>
      <router-link to="/conversations" class="el-link" @click="onClose">
        <el-icon>
          <ChatLineRound />
        </el-icon>
        <span>{{ t('dialogs') }}</span>
      </router-link>
      <router-link to="/usage" class="el-link" @click="onClose">
        <el-icon>
          <Coin />
        </el-icon>
        <span>{{ t('usage') }}</span>
      </router-link>
      <router-link to="/settings" class="el-link" @click="onClose">
        <el-icon>
          <Setting />
        </el-icon>
        <span>{{ t('settings') }}</span>
      </router-link>
      <el-button link v-if="isAuthenticated" @click="onLogout">
        <el-icon>
          <SwitchButton />
        </el-icon>
        <span> {{ t('logout') }}</span>
      </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Logo from '@/assets/logo.svg'
import {
  Setting,
  SwitchButton,
  Close,
  ChatLineRound,
  Coin,
  Grid,
  Document
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import emitter from '@/plugins/emitter'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const onClose = () => {
  emitter.emit('showMenu', false)
}

const authStore = useAuthStore() // Получите экземпляр вашего AuthStore
const { logout } = authStore
const { API_TOKEN_VALUE } = storeToRefs(authStore)
const isAuthenticated = computed(() => !!API_TOKEN_VALUE.value) // Проверьте наличие API токена

const onLogout = () => {
  if (!confirm('Вы уверены, что хотите выйти из системы?')) return
  logout()
  onClose()
}
</script>

<style scoped lang="scss">
.mobile-menu {
  position: fixed;
  z-index: 2;
  width: 100vw;
  height: 100vh;
  background: white;
  padding: 8px 20px;

  &-header {
    display: flex;
    justify-content: space-between;

    .el-image {
      width: 45px;
    }
  }

  &-body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    row-gap: 12px;
    padding-top: 18px;

    .el-icon {
      margin-right: 8px;
    }
  }
}
</style>

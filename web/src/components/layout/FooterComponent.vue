<template>
  <div class="footer">
    <router-link to="/" class="el-link">
      <el-icon>
        <Grid />
      </el-icon>
      <span class="text-xsmall">{{ t('dashboard') }}</span>
    </router-link>
    <router-link to="/documents" class="el-link">
      <el-icon>
        <Document />
      </el-icon>
      <span class="text-xsmall">{{ t('documents') }}</span>
    </router-link>

    <el-button type="primary" link @click="onNewDialog">
      <div class="flex flex-column align-center">
        <el-icon>
          <plus />
        </el-icon>
        <div class="text-xsmall">{{ t('new_question') }}</div>
      </div>
    </el-button>

    <router-link to="/conversations" class="el-link">
      <el-icon>
        <ChatLineRound />
      </el-icon>
      <span class="text-xsmall">{{ t('dialogs') }}</span>
    </router-link>
    <router-link to="/usage" class="el-link">
      <el-icon>
        <Coin />
      </el-icon>
      <span class="text-xsmall">{{ t('usage') }}</span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { Grid, Document, Plus, Coin, ChatLineRound } from '@element-plus/icons-vue'
import emitter from '@/plugins/emitter'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const onNewDialog = () => {
  emitter.emit('new-conversation')
}
</script>

<style scoped lang="scss">
.footer {
  position: fixed;
  bottom: 0;
  z-index: 2;
  background: white;
  border-top: 1px solid var(--el-border-color-light);
  padding: 16px 24px 20px;
  /*display: flex;*/
  justify-content: space-between;
  width: 100%;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  column-gap: 4px;

  .el-link {
    display: flex;
    flex-direction: column;

    &.router-link-active {
      color: var(--el-color-primary);
    }
  }

  @media (min-width: 980px) {
    display: none;
  }
}
</style>

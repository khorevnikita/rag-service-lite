<template>
  <div class="side-menu">
    <el-button class="mt-1 mb-1" type="primary" @click="onNewDialog()">
      {{ t('new_dialog') }}
    </el-button>
    <div class="links">
      <router-link
        :to="`/conversations/${conversation.id}`"
        v-for="conversation in latestConversations"
        :key="conversation.id"
        class="el-link"
      >
        {{ conversation.name }}
      </router-link>
    </div>
    <div class="links">
      <el-divider />
      <router-link to="/" class="el-link">
        <el-icon>
          <Grid />
        </el-icon>
        {{ t('dashboard') }}
      </router-link>
      <router-link to="/conversations" class="el-link">
        <el-icon>
          <ChatLineRound />
        </el-icon>
        {{ t('dialogs') }}
      </router-link>
      <router-link to="/documents" class="el-link">
        <el-icon>
          <Document />
        </el-icon>
        {{ t('documents') }}
      </router-link>
      <router-link to="/usage" class="el-link">
        <el-icon>
          <Coin />
        </el-icon>
        {{ t('usage') }}
      </router-link>
      <router-link to="/settings" class="el-link">
        <el-icon>
          <Setting />
        </el-icon>
        {{ t('settings') }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Grid, Document, Coin, ChatLineRound, Setting } from '@element-plus/icons-vue'
import { useConversationStore } from '@/stores/conversation'
import { storeToRefs } from 'pinia'
import emitter from '@/plugins/emitter'
import { useI18n } from 'vue-i18n'

const store = useConversationStore()
const { getLatestConversations } = store
const { latestConversations } = storeToRefs(store)
const { t } = useI18n()

const onNewDialog = () => {
  emitter.emit('new-conversation')
}

getLatestConversations()
</script>

<style scoped lang="scss">
.el-divider {
  margin: 8px 0;
}

.side-menu {
  display: grid;
  grid-template-rows: 40px 1fr 225px;
  height: 100%;
  padding: 0 8px;

  .links {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 16px;
    row-gap: 12px;
    overflow-y: auto;
    overflow-x: hidden;

    .el-link {
      .el-icon {
        margin-right: 4px;
      }

      &.router-link-active {
        color: var(--el-color-primary);
      }
    }
  }
}
</style>

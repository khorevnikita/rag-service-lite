<template>
  <div>
    <el-row :gutter="16" v-if="dashboardData">
      <el-col>
        <el-row :gutter="16">
          <el-col class="mb-2" :sm="8">
            <QuestionsCard
              :total-dialogs-count="dashboardData.total_conversations"
              :total-count="dashboardData.total_questions"
              :likes-count="dashboardData.likes_count"
              :dislikes-count="dashboardData.dislikes_count"
            />
          </el-col>
          <el-col class="mb-2" :sm="8">
            <DocumentsCard
              :total-documents="dashboardData.total_documents"
              :status-distribution="dashboardData.document_status_distribution"
            />
          </el-col>
          <el-col class="mb-2" :sm="8">
            <UsageCard
              :spent-current-month="dashboardData.spent_current_month"
              :spent-previous-month="dashboardData.spent_previous_month"
              :spent-total="dashboardData.spent_total"
            />
          </el-col>
        </el-row>
      </el-col>
      <el-col :md="8" class="el-col-md-push-16">
        <el-row :gutter="16">
          <!--<el-col class="mb-2" :sm="12" :md="24">
            <QuestionDistribution />
          </el-col>-->
          <el-col class="mb-2" :sm="12" :md="24">
            <KeywordDistribution />
          </el-col>
        </el-row>
      </el-col>
      <el-col :md="16" class="el-col-md-pull-8">
        <el-row :gutter="16">
          <el-col class="mb-2" v-if="dashboardData">
            <ConversationsGraph />
          </el-col>
          <el-col class="mb-2" v-if="dashboardData">
            <QuestionsGraph />
          </el-col>
          <el-col class="mb-2" v-if="dashboardData">
            <UsageGraph />
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard'
import { storeToRefs } from 'pinia'
import QuestionsCard from '@/components/dashboard/QuestionsCard.vue'
import DocumentsCard from '@/components/dashboard/DocumentsCard.vue'
import UsageCard from '@/components/dashboard/UsageCard.vue'
import ConversationsGraph from '@/components/dashboard/ConversationsGraph.vue'
import QuestionsGraph from '@/components/dashboard/QuestionsGraph.vue'
import UsageGraph from '@/components/dashboard/UsageGraph.vue'
import KeywordDistribution from '@/components/dashboard/KeywordDistribution.vue'

const store = useDashboardStore()
const { getDashboardData } = store
const { dashboardData } = storeToRefs(store)

getDashboardData()
</script>

<style scoped lang="scss"></style>

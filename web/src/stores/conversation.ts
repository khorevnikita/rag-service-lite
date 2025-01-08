import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import type { IQuestion } from '@/stores/question'

export interface IConversation {
  id: number
  account_id: number
  name: string
  meta: any
  created_at: string
  updated_at: string
  questions?: IQuestion[]
}

export const useConversationStore = defineStore('conversation', () => {
  const LATEST_CONVERSATIONS_COUNT = 15
  const latestConversations = ref<IConversation[]>([])
  const conversations = ref<IConversation[]>([])
  const totalCount = ref(0)
  const pagesCount = ref(0)

  const getLatestConversations = async () => {
    const response = await axios.get(`conversations?skip=${0}&limit=${LATEST_CONVERSATIONS_COUNT}`)
    latestConversations.value = response.data.conversations
    return latestConversations.value
  }

  const getConversations = async (skip = 0, limit = 10) => {
    const response = await axios.get(`conversations?skip=${skip}&limit=${limit}`)
    conversations.value = response.data.conversations
    totalCount.value = response.data.total_count
    pagesCount.value = response.data.pages_count
    return conversations.value
  }

  return {
    conversations,
    pagesCount,
    totalCount,
    getConversations,
    latestConversations,
    getLatestConversations
  }
})

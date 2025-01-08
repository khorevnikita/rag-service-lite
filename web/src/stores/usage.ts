import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { objToQuery } from '@/plugins/helper'

export interface IUsageLog {
  id: number
  source_key: string
  source_id: number
  operation: string
  input_usage: number
  output_usage: number
  embedding_usage: number
  price: number
  created_at: string
  updated_at: string
}

export interface IUsageRequest {
  date_from: string | null
  date_to: string | null
  operation: string | null
  document_id: number | null
}

export const useUsageStore = defineStore('usage', () => {
  const logs = ref<IUsageLog[]>([])
  const totalCount = ref(0)
  const pagesCount = ref(0)

  const getUsageLogs = async (
    request: IUsageRequest,
    skip = 0,
    limit = 30
  ): Promise<IUsageLog[]> => {
    const q = objToQuery(request)
    const response = await axios.get(`usage?skip=${skip}&limit=${limit}&${q}`)
    logs.value = response.data.usage_logs
    totalCount.value = response.data.total_count
    pagesCount.value = response.data.pages_count
    return logs.value
  }

  return { logs, pagesCount, totalCount, getUsageLogs }
})

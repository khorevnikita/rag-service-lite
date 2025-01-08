import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export interface IKeyword {
  id: number
  text: string
}

export const useKeywordStore = defineStore('keyword', () => {
  const keywords = ref<IKeyword[]>([])

  const getKeywords = async (search: string = '') => {
    const response = await axios.get(`keywords?search=${search}`)
    keywords.value = response.data.keywords
    return keywords.value
  }

  return { keywords, getKeywords }
})

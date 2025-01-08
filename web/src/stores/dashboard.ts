import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import moment from 'moment'

export interface IUsageData {
  date: string
  sum: number
}

export interface IQuestionData {
  date: string
  count: number
}

export interface IConversationData {
  date: string
  count: number
}

export interface IKeywordData {
  id: number
  text: string
  count: number
}

export interface IQuestionKeywordData {
  keyword: string
  count: number
}

export interface IDashboardData {
  total_conversations: number
  total_questions: number
  likes_count: number
  dislikes_count: number
  total_documents: number
  document_status_distribution: any
  spent_total: number
  spent_current_month: number
  spent_previous_month: number

  conversations_on_day: IConversationData[]
  total_questions_per_day: IQuestionData[]
  like_questions_per_day: IQuestionData[]
  dislike_questions_per_day: IQuestionData[]
  usage_per_day: IUsageData[]
  keyword_distribution: IKeywordData[]
  question_keyword_distribution: IQuestionKeywordData[]
}

export const useDashboardStore = defineStore('dashboard', () => {
  const dashboardData = ref<IDashboardData>()
  const DAYS_OFFSET = 30

  const getDashboardData = async (): Promise<IDashboardData> => {
    const response = await axios.get('dashboard')
    dashboardData.value = <IDashboardData>response.data
    return dashboardData.value
  }

  const generatePeriod = () => {
    const now = moment() // Текущая дата и время
    const pointer = moment().subtract(DAYS_OFFSET, 'days') // Начальная точка периода
    const period = []

    while (pointer.isBefore(now)) {
      period.push({
        key: pointer.format('YYYY-MM-DD'),
        label: pointer.format('DD.MM.YYYY')
      })
      pointer.add(1, 'day') // Правильно увеличиваем pointer на один день
    }

    // Включаем также текущий день в период, если это необходимо
    // Это зависит от вашей задачи, нужно ли включать текущий день в период
    period.push({
      key: now.format('YYYY-MM-DD'),
      label: now.format('DD.MM.YYYY')
    })

    return period
  }

  return { dashboardData, getDashboardData, generatePeriod }
})

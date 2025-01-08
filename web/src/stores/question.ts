import { nextTick, reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { objToQuery } from '@/plugins/helper'
import type { IDocument, IParagraph } from '@/stores/document'
import type { IModel } from '@/stores/model'
import moment from 'moment'
import emitter from '@/plugins/emitter'
import type { IUploadData } from '@/plugins/storage'
import { useRouter } from 'vue-router'

export type QuestionReaction = 'like' | 'dislike'

export type QuestionMode = 'regular' | 'embedding' | 'context'

export interface IQuestion {
  id: number
  conversation_id: number
  text: string
  answer: string
  reaction: null | QuestionReaction
  created_at: string
  updated_at: string
  answered_at: string | null
  reacted_at: string | null
  mode: QuestionMode
  keyword: string

  documents?: IDocument[]
  paragraphs?: IParagraph[]
  model?: IModel
  question_files?: IQuestionFile[]
}

export interface IQuestionRequest {
  date_from: string | null
  date_to: string | null
  model_id: number | null
  reaction: QuestionReaction | null
  conversation_id?: number
}

export interface IQuestionFile {
  id: string
  url: string
  name: string
  size: number
  extension: string
  type: string
  is_private: boolean
}

export interface ICreateQuestionRequest {
  text: string
  conversation_id?: number
  webhook?: string
  stream: boolean
  files?: IUploadData[]
}

export const useQuestionStore = defineStore('question', () => {
  const questions = ref<IQuestion[]>([])
  const totalCount = ref<number>(0)
  const pagesCount = ref<number>(1)
  const router = useRouter()

  const getQuestions = async (
    request: IQuestionRequest,
    skip = 0,
    limit = 10,
    concat = false
  ): Promise<IQuestion[]> => {
    const q = objToQuery(request)
    const response = await axios.get(`questions?skip=${skip}&limit=${limit}&${q}`)
    if (concat) {
      questions.value = [...questions.value, ...response.data.questions]
    } else {
      questions.value = response.data.questions
    }
    totalCount.value = response.data.total_count
    pagesCount.value = response.data.pages_count
    return questions.value
  }

  const createQuestion = async (request: ICreateQuestionRequest): Promise<IQuestion> => {
    const tempMsg = reactive<IQuestion>({
      id: 0,
      conversation_id: request.conversation_id || 0,
      text: request.text,
      answer: '',
      reaction: null,
      created_at: moment().format('YYYY-MM-DD HH:mm:ss'),
      updated_at: moment().format('YYYY-MM-DD HH:mm:ss'),
      answered_at: null,
      reacted_at: null,
      mode: 'context',
      documents: [],
      paragraphs: [],
      model: undefined,
      keyword: ''
    })

    let firstTick = true
    const create = await axios.post(`questions`, request, {
      onDownloadProgress: (e) => {
        const req = e.event.target as XMLHttpRequest
        tempMsg.id = Number(req.getResponseHeader('Question-Id'))
        tempMsg.conversation_id = Number(req.getResponseHeader('Conversation-Id'))
        tempMsg.answer = req.response
        nextTick(() => {
          emitter.emit('answer-stream')
        })

        if (firstTick) {
          router.push(`/conversations/${tempMsg.conversation_id}`).then(() => {
            if (request.stream) {
              questions.value.unshift(tempMsg)
            }
          })
          firstTick = false
        }
      }
    })

    let q_id = tempMsg.id
    if (!request.stream) {
      q_id = create.data.question.id
    }

    await new Promise((r) => setTimeout(r, 100))
    const get = await axios.get(`questions/${q_id}`)
    const question = get.data.question
    if (tempMsg.id) {
      const idx = questions.value.findIndex((q) => q.id === tempMsg.id)
      questions.value.splice(idx, 1, question)
    } else {
      questions.value.unshift(question)
    }

    return question
  }

  const like = async (question: IQuestion) => {
    await axios.post(`questions/${question.id}/like`)
    question.reaction = 'like'
  }
  const dislike = async (question: IQuestion) => {
    await axios.post(`questions/${question.id}/dislike`)
    question.reaction = 'dislike'
  }

  return { questions, totalCount, pagesCount, getQuestions, createQuestion, like, dislike }
})

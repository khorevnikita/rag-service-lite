import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { objToQuery } from '@/plugins/helper'

export type DocumentStatus = 'queued' | 'reading' | 'sliced' | 'read' | 'failed'

export type DocumentTuneStatus = 'no' | 'preparing' | 'prepared' | 'tuned'

export type ParagraphStatus = 'queued' | 'completed' | 'failed'

export interface IDocument {
  id: number
  status: DocumentStatus
  name: string
  url: string
  content_length: number
  content_url: string
  created_at: string
  updated_at: string
  meta: string

  paragraphs_count?: number
  paragraphs?: IParagraph[]
  keywords?: string[]
}

export interface IParagraph {
  id: number
  document_id: number
  status: ParagraphStatus
  content_length: number
  content_url: string
  created_at: string
  updated_at: string
  document?: IDocument
}

export interface ICreateDocumentRequest {
  name: string
  url: string
  keywords?: string[]
}

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<IDocument[]>([])
  const pagesCount = ref(1)
  const totalCount = ref(0)

  const documentItem = ref<IDocument>()

  const getDocuments = async (query = {}, skip = 0, limit = 10): Promise<IDocument[]> => {
    const q = objToQuery(query)
    const response = await axios.get(`documents?skip=${skip}&limit=${limit}&${q}`)
    documents.value = response.data.documents
    pagesCount.value = response.data.pages_count
    totalCount.value = response.data.total_count
    return documents.value
  }

  const getDocumentItem = async (id: number): Promise<IDocument> => {
    const response = await axios.get(`documents/${id}`)
    documentItem.value = <IDocument>response.data.document
    return documentItem.value
  }

  const getParagraphContent = async (paragraph: IParagraph): Promise<string> => {
    const response = await axios.get(
      `documents/${paragraph.document_id}/paragraphs/${paragraph.id}/content`
    )
    return response.data.content
  }

  const createDocument = async (request: ICreateDocumentRequest): Promise<IDocument> => {
    const response = await axios.post(`documents`, request)
    const document = response.data.document
    documents.value.unshift(document)
    return document
  }

  const destroy = async (document: IDocument) => {
    await axios.delete(`documents/${document.id}`)
    const idx = documents.value.findIndex((d) => d.id === document.id)
    if (idx >= 0) {
      documents.value.splice(idx, 1)
    }
  }

  const summarize = async (document: IDocument) => {
    await axios.post(`/documents/${document.id}/summarize`)
  }

  return {
    documents,
    pagesCount,
    totalCount,
    getDocuments,
    documentItem,
    getDocumentItem,
    getParagraphContent,
    createDocument,
    destroy,
    summarize
  }
})

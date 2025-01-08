import { defineStore } from 'pinia'

export interface IModel {
  id: number
  base_model_name: string
  status: string
  created_at: string
  updated_at: string
}

export const useModelStore = defineStore('model', () => {
  return {}
})

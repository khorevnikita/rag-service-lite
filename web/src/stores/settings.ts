import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'

export type IVisibleType =
  | 'openai_api_key'
  | 'default_context'
  | 'account_api_key'
  | 'prompt_template'

export type SettingType = IVisibleType | 'logo' | 'meta_title' | 'favicon'

export interface ISettings {
  id: number
  key: SettingType
  value: string
  created_at: string
  updated_at: string
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<ISettings[]>([])
  const { t } = useI18n()

  const SETTINGS_LIST: {
    openai_api_key: string
    default_context: string
    account_api_key: string
    prompt_template: string
    generative_provider: string
    generative_model: string
    embedding_model: string
    temperature: string
  } = {
    openai_api_key: t('settings_openai_label'),
    account_api_key: t('settings_api_key_label'),
    default_context: t('settings_context_label'),
    prompt_template: t('settings_template_label'),
    generative_provider: t('settings_llm_provider_label'),
    generative_model: t('settings_llm_label'),
    embedding_model: t('settings_embedding_label'),
    temperature: t('settings_temperature')
  }

  const getSettings = async (): Promise<ISettings[]> => {
    const response = await axios.get(`settings`)
    settings.value = response.data.settings
    return settings.value
  }

  const getSettingValue = (key: SettingType) => {
    const setting = settings.value.find((s) => s.key === key)
    return setting?.value
  }

  const getSettingComponent = (key: IVisibleType) => {
    const map = {
      openai_api_key: defineAsyncComponent(() => import('../components/settings/OpenAIKey.vue')),
      account_api_key: defineAsyncComponent(() => import('../components/settings/APIKey.vue')),
      prompt_template: defineAsyncComponent(
        () => import('../components/settings/PromptTemplate.vue')
      ),
      generative_provider: defineAsyncComponent(
        () => import('../components/settings/GenerativeProvider.vue')
      ),
      generative_model: defineAsyncComponent(
        () => import('../components/settings/GenerativeModel.vue')
      ),
      embedding_model: defineAsyncComponent(
        () => import('../components/settings/EmbeddingModel.vue')
      ),
      default_context: defineAsyncComponent(
        () => import('../components/settings/ContextString.vue')
      ),
      temperature: defineAsyncComponent(() => import('../components/settings/TemperatureValue.vue'))
    }
    return map[key]
  }

  const setSetting = async (key: SettingType, value: string) => {
    await axios.post(`settings`, {
      key: key,
      value: value
    })
  }

  return { getSettings, settings, SETTINGS_LIST, getSettingValue, getSettingComponent, setSetting }
})

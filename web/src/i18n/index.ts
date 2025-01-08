import { createI18n } from 'vue-i18n'
import en from '@/i18n/en.json'
import ru from '@/i18n/ru.json'

export default createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'en',
  fallbackLocale: 'en',
  messages: {
    en: en,
    ru: ru
  }
})

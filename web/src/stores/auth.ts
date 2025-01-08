import { nextTick, ref } from 'vue'
import { defineStore } from 'pinia'
import axios, { AuthApiKey } from '@/plugins/axios'
import ApiToken from '@/plugins/apiToken'
import { useRouter } from 'vue-router'
import Session from 'supertokens-web-js/recipe/session'
import emitter from '@/plugins/emitter'

export const useAuthStore = defineStore('auth', () => {
  const API_TOKEN_VALUE = ref<string | undefined>(ApiToken.get('api_token'))
  const router = useRouter()

  const getMe = async () => {
    try {
      const response = await axios.get('auth/me')
      const api_key = String(response.data.settings.value)
      ApiToken.set('api_token', api_key)
      axios.defaults.headers.common[AuthApiKey] = api_key
      await nextTick(() => {
        API_TOKEN_VALUE.value = api_key
      })
    } catch (e) {
      await logout()
    }
  }
  const logout = async () => {
    await Session.signOut()
    API_TOKEN_VALUE.value = ''
    ApiToken.forget('api_token')
    await router.replace('/auth')
    emitter.emit('logout')
  }

  return {
    API_TOKEN_VALUE,
    getMe,
    logout
  }
})

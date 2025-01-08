import axios, { AxiosHeaders } from 'axios'
import ApiToken from '@/plugins/apiToken'

export const AuthApiKey = 'x-api-key'

// Set config defaults when creating the instance
export const headers = new AxiosHeaders({
  'x-api-key': ApiToken.get('api_token')
})
const instance = axios.create({
  baseURL: `${import.meta.env.VITE_APP_ENDPOINT}/api`,
  headers: headers
})
export default instance

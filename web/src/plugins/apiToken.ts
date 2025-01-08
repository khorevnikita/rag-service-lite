import moment from 'moment'

export type TokenType = 'api_token' | 'access_token' | 'refresh_token'

export default class ApiToken {
  static expireKey = 'exp'

  static get(type: TokenType) {
    const token = localStorage.getItem(type)
    return token || ''
  }

  static set(type: TokenType, value: string) {
    localStorage.setItem(type, value)
  }

  static forget(type: TokenType) {
    localStorage.removeItem(type)
  }

  static getExpires() {
    return localStorage.getItem(this.expireKey)
  }

  static isExpired() {
    const ts = Number(this.getExpires())
    return ts < moment().unix()
  }

  static setExpires(minutes: number) {
    const now = moment()
    now.add(minutes, 'minutes')
    const expires_in = now.unix()
    return localStorage.setItem(this.expireKey, String(expires_in))
  }
}

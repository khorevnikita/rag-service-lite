export const objToQuery = (obj: any) => {
  return Object.keys(obj)
    .map(function (key) {
      if (!obj[key]) return ''
      return key + '=' + obj[key]
    })
    .filter((x) => x)
    .join('&')
}
export const roundExpense = (n: number) => {
  return Math.ceil(n * 1000) / 1000
}

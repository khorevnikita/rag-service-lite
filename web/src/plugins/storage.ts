import axios from '@/plugins/axios'

export type FileType = 'image' | 'pdf' | 'other'

export interface IUploadData {
  filename: string
  file_path: string
  size: number
  extension: string
  file_type: FileType
}

export const download = async (path: string) => {
  const response = await axios.post(`storage/download`, {
    path: path
  })
  window.open(response.data.url, '_blank')
}

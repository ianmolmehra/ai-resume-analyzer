import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || 'Something went wrong'
    if (error.response?.status !== 404) {
      toast.error(msg)
    }
    return Promise.reject(error)
  }
)

// Resume APIs
export const resumeAPI = {
  upload: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  list: async (skip = 0, limit = 50) => {
    const res = await api.get(`/resumes/?skip=${skip}&limit=${limit}`)
    return res.data
  },
  get: async (id) => {
    const res = await api.get(`/resumes/${id}`)
    return res.data
  },
  delete: async (id) => {
    const res = await api.delete(`/resumes/${id}`)
    return res.data
  },
}

// Matching APIs
export const matchAPI = {
  analyze: async ({ resumeId, jdText, jdFile, jobTitle, company }) => {
    const formData = new FormData()
    formData.append('resume_id', resumeId)
    if (jdText) formData.append('jd_text', jdText)
    if (jdFile) formData.append('jd_file', jdFile)
    if (jobTitle) formData.append('job_title', jobTitle)
    if (company) formData.append('company', company)
    const res = await api.post('/match/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  downloadReport: (matchReportId) => {
    window.open(`${API_BASE}/match/${matchReportId}/report/pdf`, '_blank')
  },
  getHistory: async (resumeId) => {
    const res = await api.get(`/match/history/${resumeId}`)
    return res.data
  },
}

// Analytics APIs
export const analyticsAPI = {
  dashboard: async () => {
    const res = await api.get('/analytics/dashboard')
    return res.data
  },
  topSkills: async (limit = 20) => {
    const res = await api.get(`/analytics/skills/top?limit=${limit}`)
    return res.data
  },
  ranking: async () => {
    const res = await api.get('/analytics/candidates/ranking')
    return res.data
  },
}

// Admin APIs
export const adminAPI = {
  stats: async () => {
    const res = await api.get('/admin/stats')
    return res.data
  },
  listResumes: async () => {
    const res = await api.get('/admin/resumes')
    return res.data
  },
  matchReports: async () => {
    const res = await api.get('/admin/match-reports')
    return res.data
  },
  deleteResume: async (id) => {
    const res = await api.delete(`/admin/resumes/${id}`)
    return res.data
  },
}

export default api

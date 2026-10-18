import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !/\/auth\/(login|register)/.test(err.config?.url || '')) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const register    = (email, password) => api.post('/auth/register', { email, password })
export const login       = (email, password) => api.post('/auth/login', { email, password })
export const getMe       = ()                => api.get('/auth/me')

export const getBooks    = (params = {})     => api.get('/books', { params, paramsSerializer: { indexes: null } })
export const getBook     = (id)              => api.get(`/books/${id}`)
export const getSimilar  = (id)              => api.get(`/books/${id}/similar`)

export const getTags     = ()                => api.get('/tags')
export const getTagsByCategory = (cat)       => api.get(`/tags/category/${cat}`)

export const runQuiz        = (answers) => api.post('/quiz', { answers })
export const getQuizHistory = ()        => api.get('/quiz/history')

export const getLibrary    = ()              => api.get('/library')
export const addToRead     = (bookId, comment = '') => api.post('/library/read', { book_id: bookId, comment })
export const addToWishlist = (bookId)        => api.post('/library/wishlist', { book_id: bookId })

export const getRecommendations = () => api.get('/recommendations')

export const getComments     = (bookId) => api.get(`/comments/book/${bookId}`)
export const addComment      = (bookId, text) => api.post('/comments', { book_id: bookId, text })
export const editComment     = (commentId, text) => api.put(`/comments/${commentId}`, { text })
export const deleteComment   = (commentId) => api.delete(`/comments/${commentId}`)

export default api

export const errorText = (err, fallback) => {
  if (!err.response) return 'Не удаётся связаться с сервером'
  const d = err.response.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map(x => x.msg).join('. ')
  return fallback
}

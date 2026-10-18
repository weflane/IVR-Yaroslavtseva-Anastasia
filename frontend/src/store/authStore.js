import { create } from 'zustand'
import { getMe } from '../api/client'

const useAuthStore = create((set) => ({
  user: null,
  loading: true,

  fetchUser: async () => {
    const token = localStorage.getItem('token')
    if (!token) { set({ loading: false }); return }
    try {
      const { data } = await getMe()
      set({ user: data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  setUser: (user) => set({ user }),

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null })
    window.location.href = '/login'
  },
}))

export default useAuthStore
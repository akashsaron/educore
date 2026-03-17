import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi, clearAuth, setAuth, type AuthUser } from '@/utils/api'

interface AuthState {
  user:      AuthUser | null
  isLoggedIn: boolean
  isLoading: boolean
  login:     (username: string, password: string) => Promise<void>
  logout:    () => Promise<void>
  fetchMe:   () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user:       null,
      isLoggedIn: false,
      isLoading:  false,

      login: async (username, password) => {
        set({ isLoading: true })
        try {
          const data = await authApi.login(username, password)
          setAuth(data.access, data.refresh)
          set({ user: data.user, isLoggedIn: true })
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        const refresh = localStorage.getItem('educore_refresh') ?? ''
        try { await authApi.logout(refresh) } catch {}
        clearAuth()
        set({ user: null, isLoggedIn: false })
      },

      fetchMe: async () => {
        try {
          const user = await authApi.me()
          set({ user, isLoggedIn: true })
        } catch {
          clearAuth()
          set({ user: null, isLoggedIn: false })
        }
      },
    }),
    {
      name: 'educore-auth',
      partialize: state => ({ user: state.user, isLoggedIn: state.isLoggedIn }),
    }
  )
)

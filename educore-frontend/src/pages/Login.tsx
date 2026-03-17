import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading }    = useAuthStore()
  const navigate                = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(username, password)
      navigate('/')
      toast.success('Welcome back!')
    } catch {
      toast.error('Invalid username or password')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-primary-light flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-accent rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4 shadow-lg">🎓</div>
          <h1 className="font-display text-white text-2xl">EduCore</h1>
          <p className="text-white/50 text-sm mt-1">School Management System</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-modal p-7">
          <h2 className="text-lg font-semibold text-primary mb-5">Sign in to continue</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Username</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)}
                className="input" placeholder="admin" autoFocus required />
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="input" placeholder="••••••••" required />
            </div>
            <button type="submit" disabled={isLoading}
              className="btn btn-primary w-full justify-center py-2.5 text-sm">
              {isLoading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>
          <p className="text-xs text-center text-muted mt-5">
            Default: <span className="font-mono bg-surface px-1.5 py-0.5 rounded">admin</span> / <span className="font-mono bg-surface px-1.5 py-0.5 rounded">Admin@1234</span>
          </p>
        </div>

        <p className="text-center text-white/30 text-xs mt-6">
          EduCore ERP · Django + PostgreSQL · Render.com
        </p>
      </div>
    </div>
  )
}

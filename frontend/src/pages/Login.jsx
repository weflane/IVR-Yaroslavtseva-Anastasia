import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login, errorText } from '../api/client'
import useAuthStore from '../store/authStore'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const fetchUser = useAuthStore((s) => s.fetchUser)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await login(email, password)
      localStorage.setItem('token', data.access_token)
      await fetchUser()
      navigate('/')
    } catch (err) {
      setError(errorText(err, 'Ошибка входа'))
    }
  }

  return (
    <div className="form-card">
      <h1>Вход</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Пароль</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        {error && <div className="form-error">{error}</div>}
        <button type="submit" className="btn btn-primary" style={{width: '100%', marginTop: 8}}>
          Войти
        </button>
      </form>
      <p style={{textAlign: 'center', marginTop: 16, fontSize: 14, color: 'var(--text-soft)'}}>
        Нет аккаунта? <Link to="/register" style={{color: 'var(--pink)'}}>Зарегистрироваться</Link>
      </p>
    </div>
  )
}
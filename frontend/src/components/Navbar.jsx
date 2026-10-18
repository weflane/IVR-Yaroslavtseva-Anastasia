import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">BookMatch</Link>
      <div className="navbar-links">
        <Link to="/catalog">Каталог</Link>
        {user ? (
          <>
            <Link to="/quiz">Подобрать книгу</Link>
            <Link to="/recommendations">Рекомендации</Link>
            <Link to="/profile">Профиль</Link>
            <button className="btn-logout" onClick={logout}>Выйти</button>
          </>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register" className="btn btn-primary">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  )
}
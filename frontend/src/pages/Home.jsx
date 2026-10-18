import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

function Sparkle({ className }) {
  return (
    <svg className={`deco ${className}`} viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 0C12 7 17 12 24 12C17 12 12 17 12 24C12 17 7 12 0 12C7 12 12 7 12 0Z" fill="#F4A6C3" />
    </svg>
  )
}

export default function Home() {
  const { user } = useAuthStore()
  return (
    <div className="hero">
      <Sparkle className="deco-1" />
      <Sparkle className="deco-4" />
      <span className="deco deco-dot deco-2" />
      <span className="deco deco-dot deco-3" />
      <span className="deco deco-dot deco-5" />

      <h1>Найди книгу под настроение</h1>
      <p>BookMatch подбирает книги под твоё настроение, темп и желания за 3 минуты.</p>
      <div className="hero-actions">
        {user ? (
          <Link to="/quiz" className="btn btn-primary">Подобрать книгу</Link>
        ) : (
          <>
            <Link to="/register" className="btn btn-primary">Начать</Link>
            <Link to="/catalog" className="btn btn-outline">Смотреть каталог</Link>
          </>
        )}
      </div>
    </div>
  )
}

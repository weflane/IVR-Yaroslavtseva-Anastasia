import { useLocation, Link } from 'react-router-dom'
import BookGrid from '../components/BookGrid'

export default function QuizResult() {
  const { state } = useLocation()
  const session = state?.session

  if (!session) {
    return (
      <div className="empty">
        <p>Результаты не найдены.</p>
        <Link to="/quiz" className="btn btn-primary" style={{marginTop: 16, display: 'inline-block'}}>
          Пройти квиз
        </Link>
      </div>
    )
  }

  return (
    <div>
      <h1 className="page-title">Твоя подборка</h1>
      <p className="page-subtitle">
        Мы нашли {session.result_books.length} книг специально для твоего настроения
      </p>
      <BookGrid books={session.result_books} />
      <div style={{textAlign: 'center', marginTop: 36}}>
        <Link to="/quiz" className="btn btn-outline">Пройти заново</Link>
      </div>
    </div>
  )
}
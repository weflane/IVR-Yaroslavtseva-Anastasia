import { useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import BookGrid from '../components/BookGrid'
import ExportDialog from '../components/ExportDialog'

export default function QuizResult() {
  const { state } = useLocation()
  const session = state?.session
  const [showExport, setShowExport] = useState(false)

  if (!session) {
    return (
      <div className="empty">
        <p>Результаты не найдены.</p>
        <Link to="/quiz" className="btn btn-primary" style={{marginTop: 16, display: 'inline-block'}}>
          Пройти тест
        </Link>
      </div>
    )
  }

  const n = session.result_books.length

  return (
    <div>
      <h1 className="page-title">Ваша подборка</h1>
      <p className="page-subtitle">
        {n ? `Мы нашли ${n} ${n === 1 ? 'книгу' : n < 5 ? 'книги' : 'книг'} специально для вашего настроения`
           : 'Подходящих книг пока нет. Возможно, вы уже прочитали всё из каталога'}
      </p>
      <BookGrid books={session.result_books} showDescription />
      <div className="actions-row" style={{justifyContent: 'center', marginTop: 36}}>
        {n > 0 && (
          <button className="btn btn-secondary" onClick={() => setShowExport(true)}>
            Экспорт
          </button>
        )}
        <Link to="/quiz" className="btn btn-outline">Пройти заново</Link>
      </div>
      <p className="page-subtitle" style={{textAlign: 'center', marginTop: 16}}>
        Карточку любой книги в формате .png можно сохранить на её странице.
      </p>
      {showExport && <ExportDialog session={session} onClose={() => setShowExport(false)} />}
    </div>
  )
}

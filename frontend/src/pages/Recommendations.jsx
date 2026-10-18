import { useEffect, useState } from 'react'
import { getRecommendations } from '../api/client'
import BookGrid from '../components/BookGrid'

export default function Recommendations() {
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadRecommendations = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getRecommendations()
      setBooks(res.data)
    } catch (err) {
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Не удалось получить рекомендации')
      } else {
        setError('Ошибка при загрузке рекомендаций')
      }
      console.error('Failed to load recommendations:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRecommendations()
  }, [])

  return (
    <div>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: 32
      }}>
        <div>
          <h1 className="page-title">Рекомендации для тебя</h1>
          <p className="page-subtitle">На основе твоего читательского вкуса</p>
        </div>
        <button
          onClick={loadRecommendations}
          disabled={loading}
          style={{
            padding: '10px 20px', background: 'var(--pink)', color: '#fff',
            border: 'none', borderRadius: 20, cursor: 'pointer', fontSize: 14,
            fontWeight: 500, opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? 'Обновляем...' : 'Обновить'}
        </button>
      </div>

      {error && (
        <div style={{
          background: '#ffe0e0', color: '#d32f2f', padding: '16px 20px',
          borderRadius: 10, marginBottom: 20, textAlign: 'center'
        }}>
          {error}
        </div>
      )}

      {loading && !books.length ? (
        <div className="loading">Подбираем лучшие книги...</div>
      ) : books.length > 0 ? (
        <BookGrid books={books} />
      ) : (
        <div className="empty">
          <p>Похоже, ты не добавил ни одну книгу в "Прочитанное"</p>
          <p style={{ marginTop: 8, fontSize: 14, color: 'var(--text-faint)' }}>
            Добавь несколько прочитанных книг, чтобы получить персональные рекомендации
          </p>
        </div>
      )}
    </div>
  )
}

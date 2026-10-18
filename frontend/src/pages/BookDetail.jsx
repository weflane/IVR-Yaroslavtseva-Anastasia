import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getBook, getSimilar, addToRead, addToWishlist } from '../api/client'
import BookGrid from '../components/BookGrid'
import useAuthStore from '../store/authStore'
import Comments from '../components/Comments'

export default function BookDetail() {
  const { id } = useParams()
  const { user } = useAuthStore()
  const [book, setBook] = useState(null)
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    setLoading(true)
    Promise.all([getBook(id), getSimilar(id)])
      .then(([bookRes, simRes]) => {
        setBook(bookRes.data)
        setSimilar(simRes.data)
      })
      .finally(() => setLoading(false))
  }, [id])

  const notify = (text) => {
    setMessage(text)
    setTimeout(() => setMessage(''), 2500)
  }

  if (loading) return <div className="loading">Загружаем книгу...</div>
  if (!book)   return <div className="empty">Книга не найдена</div>

  return (
    <div style={{maxWidth: 800, margin: '0 auto'}}>
      {message && (
        <div style={{
          background: 'var(--pink-soft)', color: 'var(--pink)', padding: '12px 20px',
          borderRadius: 10, marginBottom: 20, textAlign: 'center'
        }}>
          {message}
        </div>
      )}
      <div style={{display: 'flex', gap: 32, flexWrap: 'wrap'}}>
        {book.cover_url && (
          <img
            src={book.cover_url}
            alt={book.title}
            style={{width: 200, borderRadius: 10, objectFit: 'cover', flexShrink: 0}}
          />
        )}
        <div style={{flex: 1, minWidth: 240}}>
          <h1 style={{fontSize: 28, fontWeight: 700, marginBottom: 6}}>{book.title}</h1>
          <p style={{color: 'var(--text-soft)', marginBottom: 16}}>{book.author}</p>
          <div className="book-card-tags" style={{marginBottom: 16}}>
            {book.tags?.map(tag => (
              <span key={tag.id} className="tag-pill">{tag.name}</span>
            ))}
          </div>
          {book.page_count && (
            <p style={{fontSize: 14, color: 'var(--text-faint)', marginBottom: 8}}>
              {book.page_count} стр. · темп: {book.pace}
            </p>
          )}
          <p style={{lineHeight: 1.7, color: 'var(--text)', marginBottom: 24}}>
            {book.description}
          </p>
          {user && (
            <div style={{display: 'flex', gap: 10, flexWrap: 'wrap'}}>
              <button className="btn btn-primary"
                onClick={() => addToRead(book.id).then(() => notify('Добавлено в прочитанное ✓')).catch(e => notify(e.response?.data?.detail || 'Не получилось, попробуй ещё раз'))}>
                Прочитал
              </button>
              <button className="btn btn-secondary"
                onClick={() => addToWishlist(book.id).then(() => notify('Добавлено в вишлист ✓')).catch(e => notify(e.response?.data?.detail || 'Не получилось, попробуй ещё раз'))}>
                Хочу прочитать
              </button>
            </div>
          )}
        </div>
      </div>
      {similar.length > 0 && (
        <div style={{marginTop: 48}}>
          <h2 style={{fontSize: 22, fontWeight: 600, marginBottom: 4}}>Похожие книги</h2>
          <BookGrid books={similar} />
        </div>
      )}
      {user && <Comments bookId={id} />}
    </div>
  )
}
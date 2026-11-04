import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  getBook, getSimilar, addToRead, addToWishlist,
  removeFromRead, removeFromWishlist, getLibraryIds, errorText,
} from '../api/client'
import BookGrid from '../components/BookGrid'
import EmotionMap from '../components/EmotionMap'
import Comments from '../components/Comments'
import useAuthStore from '../store/authStore'
import { paceLabel } from '../utils/format'
import { exportBookPng, exportBookText } from '../utils/export'

export default function BookDetail() {
  const { id } = useParams()
  return <BookDetailPage key={id} id={id} />
}

function BookDetailPage({ id }) {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [book, setBook] = useState(null)
  const [similar, setSimilar] = useState(null)
  const [similarLoading, setSimilarLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [isRead, setIsRead] = useState(false)
  const [isWish, setIsWish] = useState(false)
  const [busy, setBusy] = useState(false)
  const similarRef = useRef(null)

  useEffect(() => {
    getBook(id)
      .then(res => setBook(res.data))
      .catch(() => setBook(null))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!user) return
    getLibraryIds()
      .then(({ data }) => {
        setIsRead(data.read_ids.includes(id))
        setIsWish(data.wishlist_ids.includes(id))
      })
      .catch(() => {})
  }, [id, user])

  const notify = (text) => {
    setMessage(text)
    setTimeout(() => setMessage(''), 2500)
  }

  const run = async (fn, okText) => {
    setBusy(true)
    try {
      await fn()
      if (okText) notify(okText)
    } catch (e) {
      notify(errorText(e, 'Не получилось, попробуйте ещё раз'))
    } finally {
      setBusy(false)
    }
  }

  const toggleRead = () => run(async () => {
    if (isRead) { await removeFromRead(id); setIsRead(false); notify('Убрано из прочитанного') }
    else { await addToRead(id); setIsRead(true); setIsWish(false); notify('Добавлено в прочитанное') }
  })

  const toggleWish = () => run(async () => {
    if (isWish) { await removeFromWishlist(id); setIsWish(false); notify('Убрано из списка «Хочу прочитать»') }
    else { await addToWishlist(id); setIsWish(true); notify('Добавлено в «Хочу прочитать»') }
  })

  const findSimilar = async () => {
    setSimilarLoading(true)
    try {
      const { data } = await getSimilar(id)
      setSimilar(data)
      setTimeout(() => similarRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    } catch (e) {
      notify(errorText(e, 'Не удалось найти похожие книги'))
    } finally {
      setSimilarLoading(false)
    }
  }

  if (loading) return <div className="loading">Книга загружается...</div>
  if (!book)   return <div className="empty">Книга не найдена</div>

  return (
    <div style={{maxWidth: 800, margin: '0 auto'}}>
      <button className="btn-mini" style={{marginBottom: 16}}
        onClick={() => (window.history.length > 1 ? navigate(-1) : navigate('/catalog'))}>
        ← Назад
      </button>
      {message && (
        <div role="status" style={{
          background: 'var(--pink-soft)', color: 'var(--pink)', padding: '12px 20px',
          borderRadius: 10, marginBottom: 20, textAlign: 'center'
        }}>
          {message}
        </div>
      )}
      <div style={{display: 'flex', gap: 32, flexWrap: 'wrap'}}>
        <div style={{flexShrink: 0}}>
          {book.cover_url && (
            <img
              src={book.cover_url}
              alt={book.title}
              style={{width: 200, borderRadius: 10, objectFit: 'cover', display: 'block'}}
            />
          )}
        </div>
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
              {book.page_count} стр. · темп: {paceLabel(book.pace)}
            </p>
          )}
          <p style={{lineHeight: 1.7, color: 'var(--text)', marginBottom: 24}}>
            {book.description}
          </p>

          <div className="actions-row">
            {user && (
              <>
                <button className={`btn ${isRead ? 'btn-outline' : 'btn-primary'}`} disabled={busy} onClick={toggleRead}>
                  {isRead ? 'Прочитано (убрать)' : 'Прочитал'}
                </button>
                {!isRead && (
                  <button className="btn btn-secondary" disabled={busy} onClick={toggleWish}>
                    {isWish ? 'В списке (убрать)' : 'Хочу прочитать'}
                  </button>
                )}
              </>
            )}
            <button className="btn btn-secondary" disabled={similarLoading} onClick={findSimilar}>
              {similarLoading ? 'Поиск...' : 'Найти похожую книгу'}
            </button>
          </div>
          <div className="actions-row" style={{marginTop: 10}}>
            <button className="btn-mini" onClick={() =>
              exportBookPng(book).catch(() => notify('Не удалось создать карточку'))}>
              Сохранить карточку (.png)
            </button>
            <button className="btn-mini" onClick={() => exportBookText(book)}>Сохранить (.txt)</button>
          </div>
        </div>
      </div>

      <h2 className="section-title">Эмоциональная карта</h2>
      <EmotionMap data={book.emotion_map} />

      <div ref={similarRef}>
        {similar !== null && (
          <div style={{marginTop: 40}}>
            <h2 style={{fontSize: 22, fontWeight: 600, marginBottom: 4}}>Похожие книги</h2>
            {similar.length
              ? <BookGrid books={similar} showDescription />
              : <p className="empty">Похожих книг пока нет</p>}
          </div>
        )}
      </div>

      {user && <Comments bookId={id} />}
    </div>
  )
}

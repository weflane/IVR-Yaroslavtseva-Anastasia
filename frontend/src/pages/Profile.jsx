import { useEffect, useState } from 'react'
import {
  getQuizHistory, getLibrary, getMyComments, removeFromRead, removeFromWishlist, errorText,
} from '../api/client'
import useAuthStore from '../store/authStore'
import BookGrid from '../components/BookGrid'
import BookCard from '../components/BookCard'
import { exportLibrary, exportQuiz } from '../utils/export'

const ANSWER_LABELS = {
  mood: { sad: 'грустное', uplifting: 'радостное', philosophical: 'задумчивое', tense: 'напряжённое' },
  genre: { mystery: 'детектив', 'sci-fi': 'фантастика', romance: 'роман', classic: 'классика' },
  pace: { slow: 'неспешный', medium: 'средний', fast: 'быстрый' },
  length: { short: 'короткая', medium: 'средняя', long: 'большая' },
}

const answersText = (a = {}) =>
  ['mood', 'genre', 'pace', 'length']
    .filter((k) => a[k])
    .map((k) => ANSWER_LABELS[k]?.[a[k]] || a[k])
    .join(' · ')

export default function Profile() {
  const { user } = useAuthStore()
  const [history, setHistory] = useState([])
  const [library, setLibrary] = useState({ read: [], wishlist: [] })
  const [tab, setTab] = useState('read')
  const [error, setError] = useState('')

  useEffect(() => {
    getQuizHistory().then(res => setHistory(res.data)).catch(() => setError('Не удалось загрузить историю'))
    getLibrary().then(res => setLibrary(res.data)).catch(() => setError('Не удалось загрузить библиотеку'))
  }, [])

  const removeBook = (kind) => async (book) => {
    try {
      await (kind === 'read' ? removeFromRead : removeFromWishlist)(book.id)
      setLibrary((lib) => ({
        ...lib,
        [kind === 'read' ? 'read' : 'wishlist']: lib[kind === 'read' ? 'read' : 'wishlist'].filter(b => b.id !== book.id),
      }))
    } catch (e) {
      setError(errorText(e, 'Не удалось убрать книгу'))
    }
  }

  const exportAll = async () => {
    let comments = []
    try { comments = (await getMyComments()).data } catch { /* без заметок */ }
    exportLibrary(library, comments)
  }

  const tabStyle = (name) => ({
    padding: '8px 20px', borderRadius: 20, border: 'none',
    cursor: 'pointer', fontWeight: 500, fontSize: 14,
    background: tab === name ? 'var(--pink)' : 'var(--pink-soft)',
    color:      tab === name ? '#fff'    : 'var(--pink)',
  })

  return (
    <div>
      <h1 className="page-title">
        Привет, {user?.email?.split('@')[0]}
      </h1>
      {error && <div className="form-error" role="alert">{error}</div>}
      <div style={{display: 'flex', gap: 8, margin: '20px 0', flexWrap: 'wrap', alignItems: 'center'}}>
        <button style={tabStyle('read')}     onClick={() => setTab('read')}>Прочитанное ({library.read.length})</button>
        <button style={tabStyle('wishlist')} onClick={() => setTab('wishlist')}>Хочу прочитать ({library.wishlist.length})</button>
        <button style={tabStyle('history')}  onClick={() => setTab('history')}>История настроений</button>
        <button className="btn-mini" style={{marginLeft: 'auto'}} onClick={exportAll}>Сохранить библиотеку (.txt)</button>
      </div>

      {tab === 'read' && (
        library.read.length
          ? <BookGrid books={library.read} onRemove={removeBook('read')} />
          : <p className="empty">Пока ничего нет.</p>
      )}

      {tab === 'wishlist' && (
        library.wishlist.length
          ? <BookGrid books={library.wishlist} onRemove={removeBook('wishlist')} />
          : <p className="empty">Пока ничего нет</p>
      )}

      {tab === 'history' && (
        <div style={{display: 'flex', flexDirection: 'column', gap: 24}}>
          {history.length ? history.map(session => (
            <div key={session.id} style={{background: '#fff', borderRadius: 16, padding: 20, border: '1.5px solid var(--pink-line)'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', alignItems: 'center'}}>
                <div>
                  <p style={{fontSize: 14, color: 'var(--text)', fontWeight: 600}}>
                    {new Date(session.created_at).toLocaleString('ru-RU', {
                      day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </p>
                  {answersText(session.answers) && (
                    <p style={{fontSize: 13, color: 'var(--text-faint)', marginTop: 2}}>
                      {answersText(session.answers)}
                    </p>
                  )}
                </div>
                <button className="btn-mini" onClick={() => exportQuiz(session)}>Сохранить (.txt)</button>
              </div>
              <div className="book-grid">
                {session.result_books.map(b => <BookCard key={b.id} book={b} />)}
              </div>
            </div>
          )) : <p className="empty">Вы ещё не проходили тест</p>}
        </div>
      )}
    </div>
  )
}

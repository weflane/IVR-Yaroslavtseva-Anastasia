import { useEffect, useState } from 'react'
import { getQuizHistory, getLibrary } from '../api/client'
import useAuthStore from '../store/authStore'
import BookCard from '../components/BookCard'

export default function Profile() {
  const { user } = useAuthStore()
  const [history, setHistory] = useState([])
  const [library, setLibrary] = useState({ read: [], wishlist: [] })
  const [tab, setTab] = useState('read')

  useEffect(() => {
    getQuizHistory().then(res => setHistory(res.data))
    getLibrary().then(res => setLibrary(res.data))
  }, [])

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
      <div style={{display: 'flex', gap: 8, margin: '20px 0'}}>
        <button style={tabStyle('read')}     onClick={() => setTab('read')}>Прочитанное</button>
        <button style={tabStyle('wishlist')} onClick={() => setTab('wishlist')}>Вишлист</button>
        <button style={tabStyle('history')}  onClick={() => setTab('history')}>История квизов</button>
      </div>

      {tab === 'read' && (
        <div className="book-grid">
          {library.read.length
            ? library.read.map(b => <BookCard key={b.id} book={b} />)
            : <p className="empty">Пока ничего нет</p>}
        </div>
      )}

      {tab === 'wishlist' && (
        <div className="book-grid">
          {library.wishlist.length
            ? library.wishlist.map(b => <BookCard key={b.id} book={b} />)
            : <p className="empty">Пока ничего нет</p>}
        </div>
      )}

      {tab === 'history' && (
        <div style={{display: 'flex', flexDirection: 'column', gap: 24}}>
          {history.length ? history.map(session => (
            <div key={session.id} style={{background: '#fff', borderRadius: 16, padding: 20, border: '1.5px solid var(--pink-line)'}}>
              <p style={{fontSize: 13, color: 'var(--text-faint)', marginBottom: 12}}>
                {new Date(session.created_at).toLocaleDateString('ru-RU', {
                  day: 'numeric', month: 'long', year: 'numeric'
                })}
              </p>
              <div className="book-grid">
                {session.result_books.map(b => <BookCard key={b.id} book={b} />)}
              </div>
            </div>
          )) : <p className="empty">Ты ещё не проходил квиз</p>}
        </div>
      )}
    </div>
  )
}

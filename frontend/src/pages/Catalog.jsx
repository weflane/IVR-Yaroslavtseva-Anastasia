import { useEffect, useState } from 'react'
import { getBooks, getTags } from '../api/client'
import BookGrid from '../components/BookGrid'

const PAGE_SIZE = 60

export default function Catalog() {
  const [result, setResult] = useState({ key: null, books: [], hasMore: false, failed: false })
  const [tags, setTags] = useState([])
  const [loadingMore, setLoadingMore] = useState(false)
  const [selectedTags, setSelectedTags] = useState([])
  const [query, setQuery] = useState('')
  const [search, setSearch] = useState('')

  const paramsKey = JSON.stringify([selectedTags, search])
  const loading = result.key !== paramsKey
  const { books, hasMore, failed } = result

  const buildParams = (skip) => {
    const params = { skip, limit: PAGE_SIZE }
    if (selectedTags.length) params.tag_ids = selectedTags
    if (search) params.q = search
    return params
  }

  useEffect(() => {
    getTags().then(res => setTags(res.data)).catch(err => console.error('Failed to load tags:', err))
  }, [])
  useEffect(() => {
    const t = setTimeout(() => setSearch(query.trim()), 300)
    return () => clearTimeout(t)
  }, [query])
  useEffect(() => {
    let cancelled = false
    getBooks(buildParams(0))
      .then((res) => {
        if (!cancelled) setResult({ key: paramsKey, books: res.data, hasMore: res.data.length === PAGE_SIZE, failed: false })
      })
      .catch((err) => {
        console.error('Failed to load books:', err)
        if (!cancelled) setResult({ key: paramsKey, books: [], hasMore: false, failed: true })
      })
    return () => { cancelled = true }
    //.
  }, [paramsKey])

  const loadMore = async () => {
    setLoadingMore(true)
    try {
      const res = await getBooks(buildParams(books.length))
      setResult((prev) => (prev.key === paramsKey
        ? { ...prev, books: [...prev.books, ...res.data], hasMore: res.data.length === PAGE_SIZE }
        : prev))
    } catch (err) {
      console.error('Failed to load books:', err)
    } finally {
      setLoadingMore(false)
    }
  }

  const toggleTag = (tagId) => {
    setSelectedTags(prev =>
      prev.includes(tagId) ? prev.filter(id => id !== tagId) : [...prev, tagId]
    )
  }

  const resetFilters = () => { setSelectedTags([]); setQuery('') }

  const tagsByCategory = {}
  tags.forEach(tag => {
    (tagsByCategory[tag.category] ||= []).push(tag)
  })

  const filtered = selectedTags.length > 0 || search

  return (
    <div>
      <h1 className="page-title">Каталог</h1>
      <p className="page-subtitle">Все книги в нашей библиотеке, просмотр без прохождения теста</p>

      <div className="toolbar">
        <input
          className="search-input"
          type="search"
          placeholder="Поиск по названию или автору"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Поиск по названию или автору"
        />
      </div>

      <div style={{ background: 'var(--pink-faint)', padding: 24, borderRadius: 12, marginBottom: 32 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Фильтр по тегам</h3>

        {Object.entries(tagsByCategory).map(([category, categoryTags]) => (
          <div key={category} style={{ marginBottom: 20 }}>
            <h4 style={{
              fontSize: 13, fontWeight: 500, color: 'var(--pink)',
              textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10
            }}>
              {category}
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {categoryTags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  aria-pressed={selectedTags.includes(tag.id)}
                  style={{
                    padding: '8px 16px', borderRadius: 20, border: '1px solid var(--pink-line)',
                    background: selectedTags.includes(tag.id) ? 'var(--pink)' : '#fff',
                    color: selectedTags.includes(tag.id) ? '#fff' : 'var(--pink)',
                    cursor: 'pointer', fontSize: 13, fontWeight: 500, transition: 'all 0.2s'
                  }}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>
        ))}

        {filtered && (
          <button className="btn-mini" style={{ marginTop: 4 }} onClick={resetFilters}>
            Сбросить фильтры
          </button>
        )}
      </div>

      {selectedTags.length > 0 && (
        <p style={{ color: 'var(--pink)', marginBottom: 20, fontSize: 14, fontWeight: 500 }}>
          Выбранные теги: {tags.filter(t => selectedTags.includes(t.id)).map(t => t.name).join(', ')}
        </p>
      )}

      {!loading && books.length === 0 ? (
        <div className="empty">
          <p>{failed ? 'Не удалось загрузить книги. Обновите страницу через минуту.' : 'По выбранным условиям книг не найдено'}</p>
          {!failed && (
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={resetFilters}>
              Очистить фильтры
            </button>
          )}
        </div>
      ) : (
        <BookGrid books={books} loading={loading} />
      )}

      {hasMore && !loading && (
        <div style={{ textAlign: 'center', marginTop: 28 }}>
          <button className="btn btn-outline" disabled={loadingMore} onClick={loadMore}>
            {loadingMore ? 'Загружаем...' : 'Показать ещё'}
          </button>
        </div>
      )}
    </div>
  )
}

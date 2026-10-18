import { useEffect, useState } from 'react'
import { getBooks, getTags } from '../api/client'
import BookGrid from '../components/BookGrid'

export default function Catalog() {
  const [books, setBooks] = useState([])
  const [tags, setTags] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTags, setSelectedTags] = useState([])

  useEffect(() => {
    loadTags()
    loadBooks()
  }, [])

  useEffect(() => {
    loadBooks()
  }, [selectedTags])

  const loadTags = async () => {
    try {
      const res = await getTags()
      setTags(res.data)
    } catch (err) {
      console.error('Failed to load tags:', err)
    }
  }

  const loadBooks = async () => {
    setLoading(true)
    try {
      const params = selectedTags.length > 0 ? { tag_ids: selectedTags } : {}
      const res = await getBooks(params)
      setBooks(res.data)
    } catch (err) {
      console.error('Failed to load books:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleTag = (tagId) => {
    setSelectedTags(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    )
  }

  const resetFilters = () => {
    setSelectedTags([])
  }
  const tagsByCategory = {}
  tags.forEach(tag => {
    if (!tagsByCategory[tag.category]) {
      tagsByCategory[tag.category] = []
    }
    tagsByCategory[tag.category].push(tag)
  })

  return (
    <div>
      <h1 className="page-title">Каталог</h1>
      <p className="page-subtitle">Все книги в нашей библиотеке</p>
      <div style={{
        background: 'var(--pink-faint)', padding: 24, borderRadius: 12,
        marginBottom: 32
      }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
          Фильтр по тегам
        </h3>

        {Object.entries(tagsByCategory).map(([category, categoryTags]) => (
          <div key={category} style={{ marginBottom: 20 }}>
            <h4 style={{
              fontSize: 13, fontWeight: 500, color: 'var(--pink)',
              textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10
            }}>
              {category}
            </h4>
            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: 8
            }}>
              {categoryTags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  style={{
                    padding: '8px 16px', borderRadius: 20, border: '1px solid var(--pink-line)',
                    background: selectedTags.includes(tag.id) ? 'var(--pink)' : '#fff',
                    color: selectedTags.includes(tag.id) ? '#fff' : 'var(--pink)',
                    cursor: 'pointer', fontSize: 13, fontWeight: 500,
                    transition: 'all 0.2s'
                  }}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>
        ))}

        {selectedTags.length > 0 && (
          <button
            onClick={resetFilters}
            style={{
              marginTop: 16, padding: '8px 16px', background: 'var(--pink-line)',
              color: 'var(--text)', border: 'none', borderRadius: 20,
              cursor: 'pointer', fontSize: 13, fontWeight: 500
            }}
          >
            Сбросить фильтры
          </button>
        )}
      </div>

      {/* Results */}
      {selectedTags.length > 0 && (
        <p style={{
          color: 'var(--pink)', marginBottom: 20, fontSize: 14,
          fontWeight: 500
        }}>
          Выбранные теги: {tags
            .filter(t => selectedTags.includes(t.id))
            .map(t => t.name)
            .join(', ')
          }
        </p>
      )}

      <BookGrid books={books} loading={loading} />

      {!loading && books.length === 0 && (
        <div className="empty">
          <p>По выбранным тегам книг не найдено</p>
          <button
            onClick={resetFilters}
            style={{
              marginTop: 16, padding: '10px 20px', background: 'var(--pink)',
              color: '#fff', border: 'none', borderRadius: 20,
              cursor: 'pointer', fontSize: 14, fontWeight: 500
            }}
          >
            Очистить фильтры
          </button>
        </div>
      )}
    </div>
  )
}

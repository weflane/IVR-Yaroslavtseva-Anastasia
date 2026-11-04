import BookCard from './BookCard'

export default function BookGrid({ books, loading, onRemove, showDescription }) {
  if (loading) return <div className="loading">Книги загружаются...</div>
  if (!books || !books.length) return <div className="empty">Книги не найдены</div>
  return (
    <div className="book-grid">
      {books.map(book => <BookCard key={book.id} book={book} onRemove={onRemove} showDescription={showDescription} />)}
    </div>
  )
}

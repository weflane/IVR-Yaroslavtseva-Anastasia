import BookCard from './BookCard'

export default function BookGrid({ books, loading }) {
  if (loading) return <div className="loading">Загружаем книги...</div>
  if (!books || !books.length) return <div className="empty">Книги не найдены</div>
  return (
    <div className="book-grid">
      {books.map(book => <BookCard key={book.id} book={book} />)}
    </div>
  )
}
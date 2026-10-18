import { Link } from 'react-router-dom'

export default function BookCard({ book }) {
  return (
    <Link to={/books/+book.id} className="book-card">
      <img
        src={book.cover_url || ''}
        alt={book.title}
        onError={(e) => { e.target.style.display = 'none' }}
      />
      <div className="book-card-body">
        <div className="book-card-title">{book.title}</div>
        <div className="book-card-author">{book.author}</div>
        {book.tags && book.tags.length > 0 && (
          <div className="book-card-tags">
            {book.tags.slice(0, 3).map(tag => (
              <span key={tag.id} className="tag-pill">{tag.name}</span>
            ))}
          </div>
        )}
      </div>
    </Link>
  )
}

import { Link } from 'react-router-dom'

export function CoverPlaceholder({ title }) {
  return <div className="cover-placeholder" aria-hidden="true">{(title || '?').trim().slice(0, 1).toUpperCase()}</div>
}

export default function BookCard({ book, onRemove, showDescription }) {
  return (
    <div className="book-cell">
      <Link to={`/books/${book.id}`} className="book-card">
        {book.cover_url ? (
          <img
            src={book.cover_url}
            alt={book.title}
            loading="lazy"
            onError={(e) => { e.target.style.display = 'none' }}
          />
        ) : (
          <CoverPlaceholder title={book.title} />
        )}
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
          {showDescription && book.description && (
            <p className="book-card-desc">{book.description}</p>
          )}
        </div>
      </Link>
      {onRemove && (
        <button className="btn-mini btn-mini-danger" onClick={() => onRemove(book)}>Убрать</button>
      )}
    </div>
  )
}

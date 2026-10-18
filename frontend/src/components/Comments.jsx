import { useEffect, useState } from 'react'
import { getComments, addComment, editComment, deleteComment } from '../api/client'
import useAuthStore from '../store/authStore'

export default function Comments({ bookId }) {
  const { user } = useAuthStore()
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingText, setEditingText] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadComments()
  }, [bookId])

  const loadComments = async () => {
    try {
      const res = await getComments(bookId)
      setComments(res.data)
    } catch (err) {
      console.error('Failed to load comments:', err)
    }
  }

  const handleAddComment = async () => {
    if (!newComment.trim()) return
    if (newComment.length > 500) {
      setMessage('Комментарий не должен превышать 500 символов')
      return
    }

    setLoading(true)
    try {
      await addComment(bookId, newComment)
      setNewComment('')
      await loadComments()
      setMessage('Комментарий добавлен')
      setTimeout(() => setMessage(''), 2500)
    } catch (err) {
      setMessage('Ошибка при добавлении комментария')
    } finally {
      setLoading(false)
    }
  }

  const handleEditComment = async (id) => {
    if (!editingText.trim()) return
    if (editingText.length > 500) {
      setMessage('Комментарий не должен превышать 500 символов')
      return
    }

    try {
      await editComment(id, editingText)
      setEditingId(null)
      setEditingText('')
      await loadComments()
      setMessage('Комментарий обновлён ✓')
      setTimeout(() => setMessage(''), 2500)
    } catch (err) {
      setMessage('Ошибка при редактировании комментария')
    }
  }

  const handleDeleteComment = async (id) => {
    if (!window.confirm('Удалить комментарий?')) return
    try {
      await deleteComment(id)
      await loadComments()
      setMessage('Комментарий удалён')
      setTimeout(() => setMessage(''), 2500)
    } catch (err) {
      setMessage('Ошибка при удалении комментария')
    }
  }

  return (
    <div style={{ marginTop: 40 }}>
      <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>Комментарии</h3>

      {message && (
        <div style={{
          background: 'var(--pink-soft)', color: 'var(--pink)', padding: '10px 16px',
          borderRadius: 8, marginBottom: 16, fontSize: 14
        }}>
          {message}
        </div>
      )}

      {user && (
        <div style={{
          background: 'var(--pink-faint)', padding: 16, borderRadius: 10, marginBottom: 24
        }}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Поделись своим мнением о книге..."
            style={{
              width: '100%', minHeight: 80, padding: 12, border: '1px solid var(--pink-line)',
              borderRadius: 6, fontFamily: 'inherit', fontSize: 14, resize: 'vertical'
            }}
          />
          <div style={{
            fontSize: 12, color: 'var(--text-faint)', marginTop: 6, marginBottom: 12
          }}>
            {newComment.length}/500
          </div>
          <button
            onClick={handleAddComment}
            disabled={loading || !newComment.trim()}
            style={{
              padding: '10px 20px', background: 'var(--pink)', color: '#fff',
              border: 'none', borderRadius: 20, cursor: 'pointer', fontSize: 14,
              fontWeight: 500, opacity: loading || !newComment.trim() ? 0.6 : 1
            }}
          >
            {loading ? 'Добавляем...' : 'Добавить комментарий'}
          </button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {comments.length ? comments.map(comment => (
          <div key={comment.id} style={{
            background: '#fff', padding: 16, borderRadius: 10,
            border: '1px solid var(--pink-line)'
          }}>
            {editingId === comment.id ? (
              <>
                <textarea
                  value={editingText}
                  onChange={(e) => setEditingText(e.target.value)}
                  style={{
                    width: '100%', minHeight: 60, padding: 12, border: '1px solid var(--pink-line)',
                    borderRadius: 6, fontFamily: 'inherit', fontSize: 14, resize: 'vertical'
                  }}
                />
                <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => handleEditComment(comment.id)}
                    style={{
                      padding: '8px 16px', background: 'var(--pink)', color: '#fff',
                      border: 'none', borderRadius: 20, cursor: 'pointer', fontSize: 13
                    }}
                  >
                    Сохранить
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    style={{
                      padding: '8px 16px', background: 'var(--pink-line)', color: 'var(--text)',
                      border: 'none', borderRadius: 20, cursor: 'pointer', fontSize: 13
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </>
            ) : (
              <>
                <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text)', marginBottom: 8 }}>
                  {comment.text}
                </p>
                <div style={{
                  fontSize: 12, color: 'var(--text-faint)', marginBottom: 12,
                  display: 'flex', gap: 16
                }}>
                  <span>{new Date(comment.created_at).toLocaleDateString('ru-RU')}</span>
                  {comment.updated_at !== comment.created_at && (
                    <span>(отредактировано)</span>
                  )}
                </div>
                {user && user.id === comment.user_id && (
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      onClick={() => {
                        setEditingId(comment.id)
                        setEditingText(comment.text)
                      }}
                      style={{
                        padding: '6px 12px', background: 'var(--pink-soft)', border: 'none',
                        borderRadius: 20, cursor: 'pointer', fontSize: 12, color: 'var(--text-soft)'
                      }}
                    >
                      Редактировать
                    </button>
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      style={{
                        padding: '6px 12px', background: '#ffe0e0', border: 'none',
                        borderRadius: 20, cursor: 'pointer', fontSize: 12, color: '#d32f2f'
                      }}
                    >
                      Удалить
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )) : (
          <p style={{ color: 'var(--text-faint)', textAlign: 'center', padding: 20 }}>
            Ещё нет комментариев
          </p>
        )}
      </div>
    </div>
  )
}

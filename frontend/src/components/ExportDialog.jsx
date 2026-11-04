import { useEffect, useState } from 'react'
import { exportQuiz, exportQuizPng } from '../utils/export'

export default function ExportDialog({ session, onClose }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const saveText = () => {
    exportQuiz(session)
    onClose()
  }

  const savePng = async () => {
    setBusy(true)
    setError('')
    try {
      await exportQuizPng(session)
      onClose()
    } catch {
      setError('Не удалось создать картинку')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="export-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="export-title">Экспорт подборки</h2>
        <p>Выберите, в каком виде сохранить подборку:</p>
        <div className="modal-actions">
          <button className="btn btn-secondary" autoFocus onClick={saveText}>
            Текстовый список (.txt)
          </button>
          <button className="btn btn-primary" disabled={busy} onClick={savePng}>
            {busy ? 'Создание картинки...' : 'Визуальная карточка (.png)'}
          </button>
        </div>
        {error && <p className="form-error">{error}</p>}
        <button className="btn-mini" onClick={onClose}>Закрыть</button>
      </div>
    </div>
  )
}

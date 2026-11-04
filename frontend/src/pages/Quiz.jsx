import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runQuiz, getQuizOptions } from '../api/client'

const QUESTIONS = [
  {
    key: 'mood',
    text: 'Какое у вас сейчас настроение?',
    options: [
      { label: 'Грустное', value: 'sad' },
      { label: 'Радостное', value: 'uplifting' },
      { label: 'Задумчивое', value: 'philosophical' },
      { label: 'Напряжённое', value: 'tense' },
    ]
  },
  {
    key: 'genre',
    text: 'Какой жанр вам ближе сейчас?',
    options: [
      { label: 'Детектив', value: 'mystery' },
      { label: 'Фантастика', value: 'sci-fi' },
      { label: 'Роман', value: 'romance' },
      { label: 'Классика', value: 'classic' },
    ]
  },
  {
    key: 'pace',
    text: 'Какой темп чтения вам подходит?',
    options: [
      { label: 'Неспешный', value: 'slow' },
      { label: 'Средний',   value: 'medium' },
      { label: 'Быстрый',  value: 'fast' },
    ]
  },
  {
    key: 'length',
    text: 'Сколько у вас времени?',
    options: [
      { label: 'Мало, короткая книга', value: 'short' },
      { label: 'Среднее',               value: 'medium' },
      { label: 'Много, большой роман', value: 'long' },
    ]
  },
]

export default function Quiz() {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [allowed, setAllowed] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false
    getQuizOptions({})
      .then(({ data }) => { if (!cancelled) setAllowed((prev) => ({ ...prev, mood: data.mood })) })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  const question = QUESTIONS[step]
  const allowedValues = allowed[question.key]
  const filtered = allowedValues && allowedValues.length
    ? question.options.filter((opt) => allowedValues.includes(opt.value))
    : question.options
  const shown = filtered.length ? filtered : question.options
  const narrowed = shown.length < question.options.length

  const handleSelect = async (value) => {
    const newAnswers = { ...answers, [question.key]: value }
    setAnswers(newAnswers)

    if (step < QUESTIONS.length - 1) {
      const nextKey = QUESTIONS[step + 1].key
      setBusy(true)
      try {
        const { data } = await getQuizOptions(newAnswers)
        setAllowed((prev) => ({ ...prev, [nextKey]: data[nextKey] }))
      } catch {
      } finally {
        setBusy(false)
      }
      setStep(step + 1)
    } else {
      setLoading(true)
      try {
        const { data } = await runQuiz(newAnswers)
        navigate('/quiz/result', { state: { session: data } })
      } catch {
        alert('Что-то пошло не так, попробуй ещё раз')
      } finally {
        setLoading(false)
      }
    }
  }

  if (loading) return <div className="loading">Идёт подбор книг...</div>

  return (
    <div className="quiz-card">
      <div className="quiz-progress">Вопрос {step + 1} из {QUESTIONS.length}</div>
      <div style={{height: 4, background: 'var(--pink-soft)', borderRadius: 4, marginBottom: 28}}>
        <div style={{
          height: '100%', borderRadius: 4, background: 'var(--pink)',
          width: `${(step / QUESTIONS.length) * 100}%`,
          transition: 'width 0.3s'
        }} />
      </div>
      <div className="quiz-question">{question.text}</div>
      <div className="quiz-options">
        {shown.map(opt => (
          <button
            key={opt.value}
            disabled={busy}
            className={`quiz-option ${answers[question.key] === opt.value ? 'selected' : ''}`}
            onClick={() => handleSelect(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {narrowed && (
        <p className="quiz-hint">
          Остались только те варианты, для которых есть непрочитанные книги.
        </p>
      )}
      {step > 0 && (
        <div className="quiz-nav">
          <button className="btn btn-secondary" disabled={busy} onClick={() => setStep(step - 1)}>← Назад</button>
        </div>
      )}
    </div>
  )
}

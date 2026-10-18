import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runQuiz } from '../api/client'

const QUESTIONS = [
  {
    key: 'mood',
    text: 'Какое у тебя сейчас настроение?',
    options: [
      { label: 'Грустное', value: 'sad' },
      { label: 'Радостное', value: 'uplifting' },
      { label: 'Задумчивое', value: 'philosophical' },
      { label: 'Напряжённое', value: 'tense' },
    ]
  },
  {
    key: 'genre',
    text: 'Какой жанр тебе ближе сейчас?',
    options: [
      { label: 'Детектив', value: 'mystery' },
      { label: 'Фантастика', value: 'sci-fi' },
      { label: 'Роман', value: 'romance' },
      { label: 'Классика', value: 'classic' },
    ]
  },
  {
    key: 'pace',
    text: 'Какой темп чтения тебе подходит?',
    options: [
      { label: 'Неспешный', value: 'slow' },
      { label: 'Средний',   value: 'medium' },
      { label: 'Быстрый',  value: 'fast' },
    ]
  },
  {
    key: 'length',
    text: 'Сколько у тебя времени?',
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
  const navigate = useNavigate()

  const question = QUESTIONS[step]

  const handleSelect = async (value) => {
    const newAnswers = { ...answers, [question.key]: value }
    setAnswers(newAnswers)

    if (step < QUESTIONS.length - 1) {
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

  if (loading) return <div className="loading">Подбираем книги для тебя...</div>

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
        {question.options.map(opt => (
          <button
            key={opt.value}
            className={`quiz-option ${answers[question.key] === opt.value ? 'selected' : ''}`}
            onClick={() => handleSelect(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {step > 0 && (
        <div className="quiz-nav">
          <button className="btn btn-secondary" onClick={() => setStep(step - 1)}>← Назад</button>
        </div>
      )}
    </div>
  )
}
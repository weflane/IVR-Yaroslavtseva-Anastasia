export const PACE_LABEL = { slow: 'неспешный', medium: 'средний', fast: 'быстрый' }

export const paceLabel = (pace) => PACE_LABEL[pace] || pace || '—'

export default function EmotionMap({ data, size = 300 }) {
  if (!data || data.length < 3) return null
  const c = size / 2
  const r = size / 2 - 52
  const n = data.length
  const angle = (i) => -Math.PI / 2 + (2 * Math.PI * i) / n
  const point = (i, k) => [c + Math.cos(angle(i)) * r * k, c + Math.sin(angle(i)) * r * k]
  const ring = (k) => data.map((_, i) => point(i, k).join(',')).join(' ')
  const shape = data.map((d, i) => point(i, Math.max(d.value, 4) / 100).join(',')).join(' ')

  return (
    <figure className="emotion-map">
      <svg viewBox={`0 0 ${size} ${size}`} role="img"
           aria-label={'Эмоциональная карта: ' + data.map((d) => `${d.label} ${d.value}`).join(', ')}>
        {[0.25, 0.5, 0.75, 1].map((k) => (
          <polygon key={k} points={ring(k)} fill="none" stroke="var(--pink-line)" strokeWidth="1" />
        ))}
        {data.map((_, i) => {
          const [x, y] = point(i, 1)
          return <line key={i} x1={c} y1={c} x2={x} y2={y} stroke="var(--pink-line)" strokeWidth="1" />
        })}
        <polygon points={shape} fill="var(--pink)" fillOpacity="0.28" stroke="var(--pink)" strokeWidth="2" />
        {data.map((d, i) => {
          const [x, y] = point(i, Math.max(d.value, 4) / 100)
          return <circle key={d.key} cx={x} cy={y} r="3.5" fill="var(--pink)" />
        })}
        {data.map((d, i) => {
          const [x, y] = point(i, 1.2)
          const anchor = Math.abs(x - c) < 4 ? 'middle' : x > c ? 'start' : 'end'
          return (
            <text key={d.key} x={x} y={y} textAnchor={anchor} dominantBaseline="middle"
                  fontSize="12" fill="var(--text-soft)">{d.label}</text>
          )
        })}
      </svg>
    </figure>
  )
}

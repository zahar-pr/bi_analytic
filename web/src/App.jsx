import { useEffect, useMemo, useRef, useState } from 'react'
import Chart from 'chart.js/auto'

const ALL = 'Все категории'
const COLORS = ['#7dd3fc', '#a3e635', '#f6d32d', '#ffa53d', '#ff6b57']
const rub = (v) => Math.round(v).toLocaleString('ru-RU') + ' ₽'
const day = (ts) => new Date(ts).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })

Chart.defaults.color = '#a3a39c'
Chart.defaults.borderColor = '#2c2c2c'

function prepare({ segments, sales }) {
  const segOf = (price) => Math.max(0, segments.findIndex((s) => price <= s.price_to))
  const points = sales.map((s) => ({ x: Date.parse(s.date), y: s.price, product: s.product, seg: segOf(s.price) }))
  return { segments, points }
}

function chartConfig({ segments, points }) {
  const xMin = Math.min(...points.map((p) => p.x))
  const xMax = Math.max(...points.map((p) => p.x))
  return {
    data: {
      datasets: [
        {
          type: 'scatter', label: 'Продажи', data: points, pointRadius: 3.5,
          backgroundColor: '#f4f4f0',
          pointBackgroundColor: points.map((p) => COLORS[p.seg]),
        },
        ...segments.map((s, i) => ({
          type: 'line', label: `${s.name}: ${rub(s.price_from)} – ${rub(s.price_to)}`,
          data: [{ x: xMin, y: s.price_from }, { x: xMax, y: s.price_from }],
          borderColor: COLORS[i], backgroundColor: COLORS[i], borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0,
        })),
      ],
    },
    options: {
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: { type: 'linear', title: { display: true, text: 'Дата продажи' }, ticks: { callback: day, stepSize: 86400000 * 7 } },
        y: { title: { display: true, text: 'Цена продажи' }, ticks: { callback: rub } },
      },
      plugins: {
        legend: {
          labels: {
            generateLabels: (c) => Chart.defaults.plugins.legend.labels.generateLabels(c)
              .map((l) => (l.datasetIndex === 0 ? { ...l, fillStyle: '#f4f4f0', strokeStyle: '#f4f4f0' } : l)),
          },
        },
        tooltip: {
          filter: (item) => item.dataset.type === 'scatter',
          callbacks: { label: (c) => `${day(c.raw.x)} · ${c.raw.product}: ${rub(c.raw.y)}` },
        },
      },
    },
  }
}

export default function App() {
  const [categories, setCategories] = useState([])
  const [category, setCategory] = useState(ALL)
  const [data, setData] = useState(null)
  const canvasRef = useRef(null)

  useEffect(() => {
    fetch('/api/categories').then((r) => r.json()).then(setCategories)
  }, [])

  useEffect(() => {
    let cancelled = false
    fetch(`/api/chart?category=${encodeURIComponent(category)}`)
      .then((r) => r.json())
      .then((d) => !cancelled && setData(d))
    return () => { cancelled = true }
  }, [category])

  const view = useMemo(() => data && prepare(data), [data])

  useEffect(() => {
    if (!view) return
    const chart = new Chart(canvasRef.current, chartConfig(view))
    return () => chart.destroy()
  }, [view])

  return (
    <div className="card">
      <h1>Анализ продаж по датам с ценовыми сегментами</h1>
      <label htmlFor="category">Категория товаров</label>
      <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
        {categories.map((c) => <option key={c}>{c}</option>)}
      </select>

      <div className="chart"><canvas ref={canvasRef} /></div>

      <div className="segments">
        {view?.segments.map((s, i) => (
          <div className="seg" key={s.name}>
            <b style={{ background: COLORS[i] }} />{s.name}
            <small>
              {rub(s.price_from)} – {rub(s.price_to)} · продаж: {view.points.filter((p) => p.seg === i).length}
            </small>
          </div>
        ))}
      </div>
    </div>
  )
}

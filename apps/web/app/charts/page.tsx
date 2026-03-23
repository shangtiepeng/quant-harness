import ChartsClient from './ChartsClient'

async function getPerformance() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/analytics/strategy-performance', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

export default async function ChartsPage() {
  const items = await getPerformance()

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 1000, margin: '0 auto' }}>
      <h1>Strategy Charts</h1>
      <p>正式图表版（Recharts）。</p>

      <section style={{ marginTop: 24, border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
        {items.length ? <ChartsClient data={items} /> : <p>暂无可视化数据。</p>}
      </section>
    </main>
  )
}

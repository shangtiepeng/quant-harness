async function getPerformance() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/analytics/strategy-performance', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

function Bar({ value, color = '#1677ff' }: { value: number; color?: string }) {
  const width = Math.max(4, Math.min(100, Math.round(Math.abs(value) * 8)))
  return (
    <div style={{ background: '#eee', borderRadius: 999, height: 12, overflow: 'hidden', width: 220 }}>
      <div style={{ width, height: '100%', background: color }} />
    </div>
  )
}

export default async function ChartsPage() {
  const items = await getPerformance()

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 960, margin: '0 auto' }}>
      <h1>Strategy Charts</h1>
      <p>当前是轻量图表版，后面可以再换成 ECharts / Recharts。</p>

      <section style={{ marginTop: 24, display: 'grid', gap: 16 }}>
        {items.length ? (
          items.map((item: any) => (
            <div key={item.strategy} style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
              <h2>{item.strategy}</h2>
              <div style={{ display: 'grid', gap: 10 }}>
                <div>
                  <div>Avg 1D: {item.avg_return_1d}%</div>
                  <Bar value={item.avg_return_1d} color="#1677ff" />
                </div>
                <div>
                  <div>Avg 3D: {item.avg_return_3d}%</div>
                  <Bar value={item.avg_return_3d} color="#52c41a" />
                </div>
                <div>
                  <div>Avg 5D: {item.avg_return_5d}%</div>
                  <Bar value={item.avg_return_5d} color="#fa8c16" />
                </div>
                <div>
                  <div>Win Rate 1D: {item.win_rate_1d}%</div>
                  <Bar value={item.win_rate_1d / 10} color="#722ed1" />
                </div>
              </div>
            </div>
          ))
        ) : (
          <p>暂无可视化数据。</p>
        )}
      </section>
    </main>
  )
}

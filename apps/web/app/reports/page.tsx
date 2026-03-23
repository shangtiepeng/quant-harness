import Link from 'next/link'

async function getReports() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/history/reports', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

async function getDetail(tradeDate?: string) {
  if (!tradeDate) return null
  try {
    const res = await fetch(`http://127.0.0.1:8010/api/history/reports/${tradeDate}`, { cache: 'no-store' })
    return await res.json()
  } catch {
    return null
  }
}

export default async function ReportsPage({ searchParams }: { searchParams: { date?: string } }) {
  const reports = await getReports()
  const selectedDate = searchParams?.date || reports[0]?.trade_date
  const detail = await getDetail(selectedDate)

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 1100, margin: '0 auto' }}>
      <h1>Archived Daily Reports</h1>
      <p>点击左侧日期可切换预览不同日报。</p>

      <section style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 20, marginTop: 24 }}>
        <div style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
          <h2>Reports</h2>
          {reports.length ? (
            <ul>
              {reports.map((item: any) => {
                const active = item.trade_date === selectedDate
                return (
                  <li key={item.trade_date} style={{ marginBottom: 10 }}>
                    <Link
                      href={`/reports?date=${item.trade_date}`}
                      style={{
                        display: 'inline-block',
                        padding: '6px 10px',
                        borderRadius: 8,
                        textDecoration: 'none',
                        background: active ? '#1677ff' : '#f5f5f5',
                        color: active ? '#fff' : '#333',
                      }}
                    >
                      {item.trade_date}
                    </Link>
                  </li>
                )
              })}
            </ul>
          ) : (
            <p>暂无历史日报。</p>
          )}
        </div>

        <div style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16, whiteSpace: 'pre-wrap' }}>
          <h2>Preview: {selectedDate || 'N/A'}</h2>
          {detail?.md ? detail.md : '暂无可预览内容。'}
        </div>
      </section>
    </main>
  )
}

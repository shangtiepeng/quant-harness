async function getReports() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/history/reports', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

async function getLatestDetail(tradeDate?: string) {
  if (!tradeDate) return null
  try {
    const res = await fetch(`http://127.0.0.1:8010/api/history/reports/${tradeDate}`, { cache: 'no-store' })
    return await res.json()
  } catch {
    return null
  }
}

export default async function ReportsPage() {
  const reports = await getReports()
  const latest = reports[0]
  const detail = await getLatestDetail(latest?.trade_date)

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 1100, margin: '0 auto' }}>
      <h1>Archived Daily Reports</h1>
      <p>历史日报浏览页。当前默认预览最新一份 Markdown 报告。</p>

      <section style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 20, marginTop: 24 }}>
        <div style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16 }}>
          <h2>Reports</h2>
          {reports.length ? (
            <ul>
              {reports.map((item: any) => (
                <li key={item.trade_date} style={{ marginBottom: 10 }}>
                  <a href={`/reports?date=${item.trade_date}`}>{item.trade_date}</a>
                </li>
              ))}
            </ul>
          ) : (
            <p>暂无历史日报。</p>
          )}
        </div>

        <div style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16, whiteSpace: 'pre-wrap' }}>
          <h2>Preview</h2>
          {detail?.md ? detail.md : '暂无可预览内容。'}
        </div>
      </section>
    </main>
  )
}

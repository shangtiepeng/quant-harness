async function getPayload() {
  try {
    const [metaRes, marketRes, signalsRes, reportRes] = await Promise.all([
      fetch('http://127.0.0.1:8010/api/meta', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/market/overview', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/signals', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/report/daily', { cache: 'no-store' }),
    ])

    return {
      meta: await metaRes.json(),
      market: await marketRes.json(),
      signals: await signalsRes.json(),
      report: await reportRes.json(),
    }
  } catch {
    return {
      meta: null,
      market: null,
      signals: [],
      report: null,
    }
  }
}

export default async function Page() {
  const data = await getPayload()

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 1080, margin: '0 auto' }}>
      <h1>Quant Harness Dashboard</h1>
      <p>研究优先的 A 股战法系统 MVP</p>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Data Source</h2>
        {data.meta ? (
          <ul>
            <li>Source: {data.meta.source}</li>
            <li>Trade Date: {data.meta.trade_date}</li>
          </ul>
        ) : (
          <p>API not running yet.</p>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Market Overview</h2>
        {data.market ? (
          <ul>
            <li>Sentiment Stage: {data.market.market_sentiment_stage}</li>
            <li>Limit Up Count: {data.market.limit_up_count}</li>
            <li>Limit Down Count: {data.market.limit_down_count}</li>
            <li>Highest Board: {data.market.highest_board}</li>
            <li>Broken Board Rate: {(data.market.broken_board_rate * 100).toFixed(1)}%</li>
          </ul>
        ) : (
          <p>API not running yet.</p>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Top Signals</h2>
        <div style={{ display: 'grid', gap: 12 }}>
          {data.signals.map((signal: any) => (
            <div key={`${signal.strategy}-${signal.symbol}`} style={{ padding: 12, border: '1px solid #eee', borderRadius: 10 }}>
              <strong>{signal.name} ({signal.symbol})</strong>
              <div>Strategy: {signal.strategy}</div>
              <div>Theme: {signal.theme}</div>
              <div>Score: {signal.score}</div>
              <div>Risk: {signal.risk_level}</div>
              <ul>
                {signal.reasons.map((reason: string) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Daily Report</h2>
        {data.report ? (
          <>
            <p>{data.report.summary_cn}</p>
            <p style={{ color: '#555' }}>{data.report.summary_en}</p>
          </>
        ) : (
          <p>No report available yet.</p>
        )}
      </section>
    </main>
  )
}

async function getPayload() {
  try {
    const [metaRes, marketRes, signalsRes, reportRes, runsRes, validationsRes, perfRes] = await Promise.all([
      fetch('http://127.0.0.1:8010/api/meta', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/market/overview', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/signals', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/report/daily', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/history/runs', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/history/validations', { cache: 'no-store' }),
      fetch('http://127.0.0.1:8010/api/analytics/strategy-performance', { cache: 'no-store' }),
    ])

    return {
      meta: await metaRes.json(),
      market: await marketRes.json(),
      signals: await signalsRes.json(),
      report: await reportRes.json(),
      runs: await runsRes.json(),
      validations: await validationsRes.json(),
      performance: await perfRes.json(),
    }
  } catch {
    return {
      meta: null,
      market: null,
      signals: [],
      report: null,
      runs: [],
      validations: [],
      performance: [],
    }
  }
}

export default async function Page() {
  const data = await getPayload()

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 1080, margin: '0 auto' }}>
      <h1>Quant Harness Dashboard</h1>
      <p>研究优先的 A 股战法系统 MVP</p>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12, background: '#fffbe6' }}>
        <h2>Automation</h2>
        <p>
          已支持自动日常任务：
          <code style={{ marginLeft: 8 }}>/api/jobs/daily-run</code>
        </p>
        <p>
          也可以本地执行：
          <code style={{ marginLeft: 8 }}>python3 scripts/run_daily_job.py</code>
        </p>
        <p>
          若要安装工作日自动任务：
          <code style={{ marginLeft: 8 }}>./scripts/setup_cron.sh</code>
        </p>
        <p>
          前端手动执行页面：
          <a href="/run-job" style={{ marginLeft: 8 }}>打开 Run Daily Job</a>
        </p>
      </section>

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

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Historical Runs</h2>
        {data.runs.length ? (
          <ul>
            {data.runs.map((run: any) => (
              <li key={run.id}>#{run.id} · {run.trade_date} · {run.source} · {run.created_at}</li>
            ))}
          </ul>
        ) : (
          <p>还没有历史运行。先调用一次 POST /api/pipeline/run 保存一轮结果。</p>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Validation Results</h2>
        {data.validations.length ? (
          <div style={{ display: 'grid', gap: 10 }}>
            {data.validations.map((item: any) => (
              <div key={item.id} style={{ padding: 12, border: '1px solid #eee', borderRadius: 10 }}>
                <strong>{item.name} ({item.symbol})</strong>
                <div>Strategy: {item.strategy}</div>
                <div>1D: {item.return_1d}% · 3D: {item.return_3d}% · 5D: {item.return_5d}%</div>
                <div>Outcome: {item.outcome_label}</div>
              </div>
            ))}
          </div>
        ) : (
          <p>还没有验证结果。先保存 run，再对该 run 调用验证接口。</p>
        )}
      </section>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
        <h2>Strategy Performance</h2>
        {data.performance.length ? (
          <div style={{ display: 'grid', gap: 10 }}>
            {data.performance.map((item: any) => (
              <div key={item.strategy} style={{ padding: 12, border: '1px solid #eee', borderRadius: 10 }}>
                <strong>{item.strategy}</strong>
                <div>Count: {item.count}</div>
                <div>Avg 1D: {item.avg_return_1d}%</div>
                <div>Avg 3D: {item.avg_return_3d}%</div>
                <div>Avg 5D: {item.avg_return_5d}%</div>
                <div>Win Rate 1D: {item.win_rate_1d}%</div>
              </div>
            ))}
          </div>
        ) : (
          <p>暂无策略统计数据。</p>
        )}
      </section>
    </main>
  )
}

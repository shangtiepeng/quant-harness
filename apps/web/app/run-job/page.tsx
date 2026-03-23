'use client'

import { useState } from 'react'

export default function RunJobPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  async function runJob() {
    setLoading(true)
    setError('')
    try {
      const res = await fetch('http://127.0.0.1:8010/api/jobs/daily-run', {
        method: 'POST',
      })
      const json = await res.json()
      setResult(json)
    } catch (e) {
      setError('执行失败，请确认 API 已启动。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: 24, fontFamily: 'Arial, sans-serif', maxWidth: 900, margin: '0 auto' }}>
      <h1>Run Daily Job</h1>
      <p>点击按钮执行一次完整盘后任务：采集、归档、验证、生成日报。</p>

      <button
        onClick={runJob}
        disabled={loading}
        style={{
          padding: '12px 20px',
          borderRadius: 10,
          border: 'none',
          background: loading ? '#999' : '#1677ff',
          color: 'white',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Running...' : 'Run Daily Job'}
      </button>

      {error ? <p style={{ color: 'red' }}>{error}</p> : null}

      {result ? (
        <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 12 }}>
          <h2>Result</h2>
          <ul>
            <li>Run ID: {result.run_id}</li>
            <li>Trade Date: {result.trade_date}</li>
            <li>Source: {result.source}</li>
            <li>Signal Count: {result.signal_count}</li>
            <li>Validation Count: {result.validation_count}</li>
            <li>JSON Archive: {result.archive?.json_path}</li>
            <li>Markdown Archive: {result.archive?.md_path}</li>
          </ul>
          <p>{result.report?.summary_cn}</p>
        </section>
      ) : null}
    </main>
  )
}

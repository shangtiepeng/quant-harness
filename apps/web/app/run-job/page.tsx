'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Alert, Button, Card, Descriptions, Layout, Space, Spin, Typography } from 'antd'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography

export default function RunJobPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [statusText, setStatusText] = useState('')

  async function runJob() {
    setLoading(true)
    setError('')
    setResult(null)
    setStatusText('正在执行盘后任务，这可能需要 10~60 秒，请稍等…')

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 90_000)

    try {
      const res = await fetch('http://127.0.0.1:8010/api/jobs/daily-run', {
        method: 'POST',
        signal: controller.signal,
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const json = await res.json()
      setResult(json)
      setStatusText('执行完成。')
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('执行超时：任务仍可能在后台运行，请稍后查看 Reports 页面或重试。')
      } else if (err instanceof Error) {
        setError(`执行失败：${err.message}`)
      } else {
        setError('执行失败，请确认 API 已启动。')
      }
      setStatusText('')
    } finally {
      clearTimeout(timeoutId)
      setLoading(false)
    }
  }

  return (
    <Layout>
      <Header style={{ background: '#001529' }}>
        <Space size="large">
          <Link href="/" style={{ color: '#fff' }}>Dashboard</Link>
          <Link href="/run-job" style={{ color: '#fff' }}>Run Job</Link>
          <Link href="/reports" style={{ color: '#fff' }}>Reports</Link>
          <Link href="/charts" style={{ color: '#fff' }}>Charts</Link>
        </Space>
      </Header>
      <Content style={{ padding: 24 }}>
        <Space orientation="vertical" size={16} style={{ width: '100%' }}>
          <Card>
            <Title level={2}>Run Daily Job</Title>
            <Paragraph>点击按钮执行一次完整盘后任务：采集、归档、验证、生成日报。</Paragraph>
            <Space orientation="vertical" size={12} style={{ width: '100%' }}>
              <Button type="primary" onClick={runJob} loading={loading} disabled={loading}>
                {loading ? 'Running…' : 'Run Daily Job'}
              </Button>
              {statusText ? (
                <Text type={loading ? 'secondary' : undefined}>
                  {statusText}
                </Text>
              ) : null}
              {loading ? <Spin tip="任务执行中…" /> : null}
            </Space>
          </Card>

          {error ? <Alert type="error" title={error} showIcon /> : null}

          {result ? (
            <Card title="Execution Result">
              <Descriptions bordered column={1}>
                <Descriptions.Item label="Run ID">{result.run_id}</Descriptions.Item>
                <Descriptions.Item label="Trade Date">{result.trade_date}</Descriptions.Item>
                <Descriptions.Item label="Source">{result.source}</Descriptions.Item>
                <Descriptions.Item label="Signal Count">{result.signal_count}</Descriptions.Item>
                <Descriptions.Item label="Validation Count">{result.validation_count}</Descriptions.Item>
                <Descriptions.Item label="Paper Opened">{result.paper_execution?.opened_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Paper Closed">{result.paper_execution?.closed_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Paper Rebalanced">{result.paper_execution?.rebalanced_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Execution Policy">{result.paper_execution?.execution_policy ?? 'N/A'}</Descriptions.Item>
                <Descriptions.Item label="Risk Mode">{result.paper_execution?.risk_mode ?? 'N/A'}</Descriptions.Item>
                <Descriptions.Item label="JSON Archive">{result.archive?.json_path}</Descriptions.Item>
                <Descriptions.Item label="Markdown Archive">{result.archive?.md_path}</Descriptions.Item>
              </Descriptions>
              <Alert style={{ marginTop: 16 }} type="info" title={result.report?.summary_cn} showIcon />
            </Card>
          ) : null}
        </Space>
      </Content>
    </Layout>
  )
}

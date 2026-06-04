'use client'

import { useState } from 'react'
import { Alert, Button, Card, Col, Descriptions, Progress, Row, Space, Spin, Typography } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import { apiUrl } from '../config'
import { AppShell, MetricCard, PageIntro } from '../components/AppShell'

const { Paragraph, Text } = Typography

type DailyRunResult = {
  run_id?: string
  trade_date?: string
  source?: string
  signal_count?: number
  validation_count?: number
  paper_execution?: {
    opened_count?: number
    closed_count?: number
    rebalanced_count?: number
    execution_policy?: string
    risk_mode?: string
  }
  archive?: {
    json_path?: string
    md_path?: string
  }
  report?: {
    summary_cn?: string
  }
}

export default function RunJobPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DailyRunResult | null>(null)
  const [error, setError] = useState('')
  const [statusText, setStatusText] = useState('')

  async function runJob() {
    setLoading(true)
    setError('')
    setResult(null)
    setStatusText('正在执行盘后任务，这可能需要 10 到 60 秒。')

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 90_000)

    try {
      const res = await fetch(apiUrl('/api/jobs/daily-run'), {
        method: 'POST',
        signal: controller.signal,
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const json = (await res.json()) as DailyRunResult
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
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="Run Job"
          title="Run Daily Job"
          description="手动执行一次完整盘后任务：采集、归档、验证、模拟执行和生成日报。"
          actions={(
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={runJob}
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Running' : 'Run Daily Job'}
            </Button>
          )}
        >
          <Text type="secondary">API 请求超时设置为 90 秒；超时后任务仍可能在后端继续执行。</Text>
        </PageIntro>

        {error ? <Alert type="error" title={error} showIcon /> : null}

        <Card>
          <Space orientation="vertical" size={12} style={{ width: '100%' }}>
            <Space align="center" size={12}>
              {loading ? <Spin /> : null}
              <Text>{statusText || '等待执行。'}</Text>
            </Space>
            {loading ? <Progress percent={70} status="active" showInfo={false} /> : null}
          </Space>
        </Card>

        {result ? (
          <Space orientation="vertical" size={16} style={{ width: '100%' }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="Trade Date" value={result.trade_date || 'N/A'} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="Signals" value={result.signal_count || 0} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="Validations" value={result.validation_count || 0} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="Risk Mode" value={result.paper_execution?.risk_mode || 'N/A'} />
              </Col>
            </Row>

            <Card title="Execution Result">
              <Descriptions bordered column={{ xs: 1, md: 2 }}>
                <Descriptions.Item label="Run ID">{result.run_id}</Descriptions.Item>
                <Descriptions.Item label="Source">{result.source}</Descriptions.Item>
                <Descriptions.Item label="Paper Opened">{result.paper_execution?.opened_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Paper Closed">{result.paper_execution?.closed_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Paper Rebalanced">{result.paper_execution?.rebalanced_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="Execution Policy">{result.paper_execution?.execution_policy ?? 'N/A'}</Descriptions.Item>
                <Descriptions.Item label="JSON Archive">{result.archive?.json_path}</Descriptions.Item>
                <Descriptions.Item label="Markdown Archive">{result.archive?.md_path}</Descriptions.Item>
              </Descriptions>
              {result.report?.summary_cn ? (
                <Alert style={{ marginTop: 16 }} type="info" title={result.report.summary_cn} showIcon />
              ) : null}
            </Card>
          </Space>
        ) : (
          <Card>
            <Paragraph type="secondary" style={{ marginBottom: 0 }}>
              执行完成后，这里会显示运行 ID、信号数、验证数、模拟持仓变动和归档路径。
            </Paragraph>
          </Card>
        )}
      </Space>
    </AppShell>
  )
}

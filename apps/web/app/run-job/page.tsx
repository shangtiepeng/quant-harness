'use client'

import { useState } from 'react'
import { Alert, Button, Card, Col, Descriptions, Progress, Row, Space, Spin, Typography } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import { apiConnectionError, fetchApi } from '../config'
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

    try {
      const json = await fetchApi<DailyRunResult>('/api/jobs/daily-run', undefined, {
        method: 'POST',
        timeoutMs: 90_000,
      })
      setResult(json)
      setStatusText('执行完成。')
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        setError('执行超时：任务仍可能在后台运行，请稍后查看“研究报告”页面或重试。')
      } else if (err instanceof Error) {
        setError(err.message === 'Failed to fetch' ? apiConnectionError('执行失败').message : `执行失败：${err.message}`)
      } else {
        setError(apiConnectionError('执行失败').message)
      }
      setStatusText('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="任务执行"
          title="执行盘后研究任务"
          description="手动执行一次完整盘后任务：采集、归档、验证、模拟执行和生成日报。"
          actions={(
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={runJob}
              loading={loading}
              disabled={loading}
            >
              {loading ? '执行中' : '开始执行'}
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
                <MetricCard title="交易日" value={result.trade_date || '暂无'} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="信号数" value={result.signal_count || 0} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="验证数" value={result.validation_count || 0} />
              </Col>
              <Col xs={24} sm={12} xl={6}>
                <MetricCard title="风险模式" value={result.paper_execution?.risk_mode || '暂无'} />
              </Col>
            </Row>

            <Card title="执行结果">
              <Descriptions bordered column={{ xs: 1, md: 2 }}>
                <Descriptions.Item label="运行 ID">{result.run_id}</Descriptions.Item>
                <Descriptions.Item label="数据源">{result.source}</Descriptions.Item>
                <Descriptions.Item label="模拟开仓">{result.paper_execution?.opened_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="模拟平仓">{result.paper_execution?.closed_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="模拟调仓">{result.paper_execution?.rebalanced_count ?? 0}</Descriptions.Item>
                <Descriptions.Item label="执行策略">{result.paper_execution?.execution_policy ?? '暂无'}</Descriptions.Item>
                <Descriptions.Item label="JSON 归档">{result.archive?.json_path}</Descriptions.Item>
                <Descriptions.Item label="Markdown 归档">{result.archive?.md_path}</Descriptions.Item>
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

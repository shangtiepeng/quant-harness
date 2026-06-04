'use client'

import { useEffect, useMemo, useState } from 'react'
import { Alert, Card, Col, Empty, Row, Space, Table, Typography } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import ChartsClient from './ChartsClient'
import { apiUrl } from '../config'
import { AppShell, MetricCard, PageIntro } from '../components/AppShell'

const { Paragraph, Text } = Typography

type ApiRecord = Record<string, unknown>

type AnalyticsRow = ApiRecord & {
  key: string
}

type ResonancePayload = {
  sample_size?: number
  by_resonance_level?: ApiRecord[]
  by_mainline?: ApiRecord[]
  by_market_stage?: ApiRecord[]
  by_consensus?: ApiRecord[]
}

function asString(value: unknown, fallback = 'N/A'): string {
  return typeof value === 'string' && value ? value : fallback
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function keyedRows(rows: ApiRecord[] | undefined): AnalyticsRow[] {
  return (rows || []).map((record, index) => ({
    ...record,
    key: asString(record.bucket, `row-${index}`),
  }))
}

export default function ChartsPage() {
  const [items, setItems] = useState<ApiRecord[]>([])
  const [resonance, setResonance] = useState<ResonancePayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let ignore = false

    async function fetchJson<T>(path: string, fallback: T): Promise<T> {
      try {
        const res = await fetch(apiUrl(path))
        if (!res.ok) return fallback
        return (await res.json()) as T
      } catch {
        return fallback
      }
    }

    async function load() {
      setLoading(true)
      setError('')
      try {
        const [perfData, resonanceData] = await Promise.all([
          fetchJson<ApiRecord[]>('/api/analytics/strategy-performance', []),
          fetchJson<ResonancePayload | null>('/api/analytics/resonance-validation', null),
        ])
        if (ignore) return
        setItems(perfData)
        setResonance(resonanceData)
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : '加载失败')
        }
      } finally {
        if (!ignore) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      ignore = true
    }
  }, [])

  const chartItems = useMemo<AnalyticsRow[]>(() => items.map((record, index) => ({
    ...record,
    key: asString(record.strategy, `strategy-${index}`),
  })), [items])
  const best = chartItems[0]
  const resonanceRows = keyedRows(resonance?.by_resonance_level)
  const bestResonance = resonanceRows[0]

  const columns: ColumnsType<AnalyticsRow> = [
    { title: 'Bucket', dataIndex: 'bucket', key: 'bucket', width: 170 },
    { title: 'Count', dataIndex: 'count', key: 'count', width: 90 },
    { title: 'Avg 1D', dataIndex: 'avg_return_1d', key: 'avg_return_1d', width: 110 },
    { title: 'Avg 3D', dataIndex: 'avg_return_3d', key: 'avg_return_3d', width: 110 },
    { title: 'Avg 5D', dataIndex: 'avg_return_5d', key: 'avg_return_5d', width: 110 },
    { title: 'Win Rate 1D', dataIndex: 'win_rate_1d', key: 'win_rate_1d', width: 130 },
  ]

  const tableSections = [
    { title: 'Resonance Level Validation', rows: resonanceRows },
    { title: 'Mainline vs Non-mainline', rows: keyedRows(resonance?.by_mainline) },
    { title: 'By Market Stage', rows: keyedRows(resonance?.by_market_stage) },
    { title: 'By Strategy Consensus', rows: keyedRows(resonance?.by_consensus) },
  ]

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="Analytics"
          title="Strategy & Resonance Analytics"
          description="不仅看策略表现，也看共振等级、主线归属和市场阶段下的验证差异。"
        />

        {error ? <Alert type="error" showIcon title="加载失败" description={error} /> : null}

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <MetricCard
              title="Best Strategy"
              value={asString(best?.strategy)}
              extra={<Text type="secondary">Avg 1D: {asNumber(best?.avg_return_1d)}% / Win Rate: {asNumber(best?.win_rate_1d)}%</Text>}
            />
          </Col>
          <Col xs={24} md={8}>
            <MetricCard
              title="Best Resonance Bucket"
              value={asString(bestResonance?.bucket)}
              extra={<Text type="secondary">Avg 1D: {asNumber(bestResonance?.avg_return_1d)}% / Win Rate: {asNumber(bestResonance?.win_rate_1d)}%</Text>}
            />
          </Col>
          <Col xs={24} md={8}>
            <MetricCard title="Validation Sample Size" value={resonance?.sample_size || 0} />
          </Col>
        </Row>

        <Card title="Strategy Performance Overview" loading={loading}>
          {chartItems.length ? (
            <ChartsClient data={chartItems} />
          ) : (
            <Empty description="暂无可视化数据" />
          )}
        </Card>

        <Row gutter={[16, 16]}>
          {tableSections.map((section) => (
            <Col xs={24} xl={12} key={section.title}>
              <Card title={section.title} loading={loading}>
                {section.rows.length ? (
                  <Table
                    className="app-table"
                    columns={columns}
                    dataSource={section.rows}
                    pagination={false}
                    scroll={{ x: 720 }}
                    size="middle"
                  />
                ) : (
                  <Paragraph type="secondary" style={{ marginBottom: 0 }}>暂无数据。</Paragraph>
                )}
              </Card>
            </Col>
          ))}
        </Row>
      </Space>
    </AppShell>
  )
}

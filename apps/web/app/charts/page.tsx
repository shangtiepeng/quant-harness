'use client'

import { useEffect, useMemo, useState } from 'react'
import { Alert, Card, Col, Empty, Row, Space, Table, Typography } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import ChartsClient from './ChartsClient'
import { apiConnectionError, fetchApi } from '../config'
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

function asString(value: unknown, fallback = '暂无'): string {
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

    async function load() {
      setLoading(true)
      setError('')
      try {
        const [perfData, resonanceData] = await Promise.all([
          fetchApi<ApiRecord[]>('/api/analytics/strategy-performance', []),
          fetchApi<ResonancePayload | null>('/api/analytics/resonance-validation', null),
        ])
        if (ignore) return
        setItems(perfData)
        setResonance(resonanceData)
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : apiConnectionError().message)
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
    { title: '分组', dataIndex: 'bucket', key: 'bucket', width: 170 },
    { title: '样本数', dataIndex: 'count', key: 'count', width: 90 },
    { title: '1日均值', dataIndex: 'avg_return_1d', key: 'avg_return_1d', width: 110 },
    { title: '3日均值', dataIndex: 'avg_return_3d', key: 'avg_return_3d', width: 110 },
    { title: '5日均值', dataIndex: 'avg_return_5d', key: 'avg_return_5d', width: 110 },
    { title: '1日胜率', dataIndex: 'win_rate_1d', key: 'win_rate_1d', width: 130 },
  ]

  const tableSections = [
    { title: '共振等级验证', rows: resonanceRows },
    { title: '主线与非主线对比', rows: keyedRows(resonance?.by_mainline) },
    { title: '市场阶段分组', rows: keyedRows(resonance?.by_market_stage) },
    { title: '策略共识分组', rows: keyedRows(resonance?.by_consensus) },
  ]

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="数据看板"
          title="策略与共振验证"
          description="不仅看策略表现，也看共振等级、主线归属和市场阶段下的验证差异。"
        />

        {error ? <Alert type="error" showIcon title="加载失败" description={error} /> : null}

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <MetricCard
              title="最佳策略"
              value={asString(best?.strategy)}
              extra={<Text type="secondary">1日均值：{asNumber(best?.avg_return_1d)}% / 胜率：{asNumber(best?.win_rate_1d)}%</Text>}
            />
          </Col>
          <Col xs={24} md={8}>
            <MetricCard
              title="最佳共振分组"
              value={asString(bestResonance?.bucket)}
              extra={<Text type="secondary">1日均值：{asNumber(bestResonance?.avg_return_1d)}% / 胜率：{asNumber(bestResonance?.win_rate_1d)}%</Text>}
            />
          </Col>
          <Col xs={24} md={8}>
            <MetricCard title="验证样本数" value={resonance?.sample_size || 0} />
          </Col>
        </Row>

        <Card title="策略表现概览" loading={loading}>
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

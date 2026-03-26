'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, Col, Layout, Row, Space, Statistic, Table, Typography } from 'antd'
import ChartsClient from './ChartsClient'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography

export default function ChartsPage() {
  const [items, setItems] = useState<any[]>([])
  const [resonance, setResonance] = useState<any>(null)

  useEffect(() => {
    async function load() {
      const fetchJson = async (url: string, fallback: any) => {
        try {
          const res = await fetch(url)
          if (!res.ok) return fallback
          return await res.json()
        } catch {
          return fallback
        }
      }

      const [perfData, resonanceData] = await Promise.all([
        fetchJson('http://127.0.0.1:8010/api/analytics/strategy-performance', []),
        fetchJson('http://127.0.0.1:8010/api/analytics/resonance-validation', null),
      ])
      setItems(perfData)
      setResonance(resonanceData)
    }
    load()
  }, [])

  const best = items[0]
  const bestResonance = resonance?.by_resonance_level?.[0]

  const columns = [
    { title: 'Bucket', dataIndex: 'bucket', key: 'bucket' },
    { title: 'Count', dataIndex: 'count', key: 'count' },
    { title: 'Avg 1D', dataIndex: 'avg_return_1d', key: 'avg_return_1d' },
    { title: 'Avg 3D', dataIndex: 'avg_return_3d', key: 'avg_return_3d' },
    { title: 'Avg 5D', dataIndex: 'avg_return_5d', key: 'avg_return_5d' },
    { title: 'Win Rate 1D', dataIndex: 'win_rate_1d', key: 'win_rate_1d' },
  ]

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
            <Title level={2}>Strategy & Resonance Analytics</Title>
            <Paragraph>不仅看策略表现，也看共振等级、主线归属和市场阶段下的验证差异。</Paragraph>
          </Card>

          <Row gutter={16}>
            {best ? (
              <Col span={8}>
                <Card>
                  <Statistic title="Best Strategy" value={best.strategy} />
                  <Text type="secondary">Avg 1D: {best.avg_return_1d}% / Win Rate 1D: {best.win_rate_1d}%</Text>
                </Card>
              </Col>
            ) : null}
            {bestResonance ? (
              <Col span={8}>
                <Card>
                  <Statistic title="Best Resonance Bucket" value={bestResonance.bucket} />
                  <Text type="secondary">Avg 1D: {bestResonance.avg_return_1d}% / Win Rate 1D: {bestResonance.win_rate_1d}%</Text>
                </Card>
              </Col>
            ) : null}
            {resonance ? (
              <Col span={8}>
                <Card>
                  <Statistic title="Validation Sample Size" value={resonance.sample_size || 0} />
                </Card>
              </Col>
            ) : null}
          </Row>

          <Card title="Strategy Performance Overview">
            {items.length ? <ChartsClient data={items} /> : <p>暂无可视化数据。</p>}
          </Card>

          <Card title="Resonance Level Validation">
            <Table columns={columns} dataSource={(resonance?.by_resonance_level || []).map((r: any) => ({ ...r, key: r.bucket }))} pagination={false} />
          </Card>

          <Card title="Mainline vs Non-mainline">
            <Table columns={columns} dataSource={(resonance?.by_mainline || []).map((r: any) => ({ ...r, key: r.bucket }))} pagination={false} />
          </Card>

          <Card title="By Market Stage">
            <Table columns={columns} dataSource={(resonance?.by_market_stage || []).map((r: any) => ({ ...r, key: r.bucket }))} pagination={false} />
          </Card>

          <Card title="By Strategy Consensus">
            <Table columns={columns} dataSource={(resonance?.by_consensus || []).map((r: any) => ({ ...r, key: r.bucket }))} pagination={false} />
          </Card>
        </Space>
      </Content>
    </Layout>
  )
}

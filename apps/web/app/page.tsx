'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, Col, Layout, Row, Space, Statistic, Table, Tag, Typography } from 'antd'

const { Header, Content } = Layout
const { Title, Paragraph } = Typography

export default function Page() {
  const [data, setData] = useState<any>({
    meta: null,
    market: null,
    signals: [],
    report: null,
    runs: [],
    validations: [],
    performance: [],
  })

  useEffect(() => {
    async function load() {
      const [metaRes, marketRes, signalsRes, reportRes, runsRes, validationsRes, perfRes] = await Promise.all([
        fetch('http://127.0.0.1:8010/api/meta'),
        fetch('http://127.0.0.1:8010/api/market/overview'),
        fetch('http://127.0.0.1:8010/api/signals'),
        fetch('http://127.0.0.1:8010/api/report/daily'),
        fetch('http://127.0.0.1:8010/api/history/runs'),
        fetch('http://127.0.0.1:8010/api/history/validations'),
        fetch('http://127.0.0.1:8010/api/analytics/strategy-performance'),
      ])
      setData({
        meta: await metaRes.json(),
        market: await marketRes.json(),
        signals: await signalsRes.json(),
        report: await reportRes.json(),
        runs: await runsRes.json(),
        validations: await validationsRes.json(),
        performance: await perfRes.json(),
      })
    }
    load()
  }, [])

  const signalColumns = [
    { title: '标的', dataIndex: 'display', key: 'display' },
    { title: '策略', dataIndex: 'strategy', key: 'strategy', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: '题材', dataIndex: 'theme', key: 'theme' },
    { title: '分数', dataIndex: 'score', key: 'score' },
    { title: '风险', dataIndex: 'risk_level', key: 'risk_level', render: (v: string) => <Tag color={v === 'high' ? 'red' : 'orange'}>{v}</Tag> },
  ]

  const runColumns = [
    { title: 'Run ID', dataIndex: 'id', key: 'id' },
    { title: '日期', dataIndex: 'trade_date', key: 'trade_date' },
    { title: '数据源', dataIndex: 'source', key: 'source' },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  ]

  const validationColumns = [
    { title: '标的', dataIndex: 'display', key: 'display' },
    { title: '策略', dataIndex: 'strategy', key: 'strategy' },
    { title: '1D%', dataIndex: 'return_1d', key: 'return_1d' },
    { title: '3D%', dataIndex: 'return_3d', key: 'return_3d' },
    { title: '5D%', dataIndex: 'return_5d', key: 'return_5d' },
    { title: '结果', dataIndex: 'outcome_label', key: 'outcome_label' },
  ]

  const perfColumns = [
    { title: '策略', dataIndex: 'strategy', key: 'strategy' },
    { title: '样本数', dataIndex: 'count', key: 'count' },
    { title: 'Avg 1D', dataIndex: 'avg_return_1d', key: 'avg_return_1d' },
    { title: 'Avg 3D', dataIndex: 'avg_return_3d', key: 'avg_return_3d' },
    { title: 'Avg 5D', dataIndex: 'avg_return_5d', key: 'avg_return_5d' },
    { title: 'Win Rate 1D', dataIndex: 'win_rate_1d', key: 'win_rate_1d' },
  ]

  const signals = data.signals.map((r: any, i: number) => ({ ...r, key: `${r.strategy}-${r.symbol}-${i}`, display: `${r.name} (${r.symbol})` }))
  const runs = data.runs.map((r: any) => ({ ...r, key: r.id }))
  const validations = data.validations.map((r: any) => ({ ...r, key: r.id, display: `${r.name} (${r.symbol})` }))
  const performance = data.performance.map((r: any) => ({ ...r, key: r.strategy }))

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
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <Card>
            <Title level={2}>Quant Harness Dashboard</Title>
            <Paragraph>研究优先的 A 股战法系统 MVP</Paragraph>
          </Card>

          <Row gutter={16}>
            <Col span={6}><Card><Statistic title="Data Source" value={data.meta?.source || 'N/A'} /></Card></Col>
            <Col span={6}><Card><Statistic title="Trade Date" value={data.meta?.trade_date || 'N/A'} /></Card></Col>
            <Col span={6}><Card><Statistic title="Sentiment" value={data.market?.market_sentiment_stage || 'N/A'} /></Card></Col>
            <Col span={6}><Card><Statistic title="Highest Board" value={data.market?.highest_board || 0} /></Card></Col>
          </Row>

          <Card title="Daily Report">
            <Paragraph>{data.report?.summary_cn || '暂无摘要'}</Paragraph>
            <Paragraph type="secondary">{data.report?.summary_en || ''}</Paragraph>
          </Card>

          <Card title="Top Signals">
            <Table columns={signalColumns} dataSource={signals} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Historical Runs">
            <Table columns={runColumns} dataSource={runs} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Validation Results">
            <Table columns={validationColumns} dataSource={validations} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Strategy Performance">
            <Table columns={perfColumns} dataSource={performance} pagination={false} />
          </Card>
        </Space>
      </Content>
    </Layout>
  )
}

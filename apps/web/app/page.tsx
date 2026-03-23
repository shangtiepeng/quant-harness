import Link from 'next/link'
import { Card, Col, Layout, Row, Space, Statistic, Table, Tag, Typography } from 'antd'

const { Header, Content } = Layout
const { Title, Paragraph } = Typography

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

  const signalColumns = [
    { title: '标的', dataIndex: 'name', key: 'name', render: (_: any, r: any) => `${r.name} (${r.symbol})` },
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
    { title: '标的', dataIndex: 'name', key: 'name', render: (_: any, r: any) => `${r.name} (${r.symbol})` },
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
            <Table rowKey={(r) => `${r.strategy}-${r.symbol}`} columns={signalColumns} dataSource={data.signals} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Historical Runs">
            <Table rowKey="id" columns={runColumns} dataSource={data.runs} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Validation Results">
            <Table rowKey="id" columns={validationColumns} dataSource={data.validations} pagination={{ pageSize: 5 }} />
          </Card>

          <Card title="Strategy Performance">
            <Table rowKey="strategy" columns={perfColumns} dataSource={data.performance} pagination={false} />
          </Card>
        </Space>
      </Content>
    </Layout>
  )
}

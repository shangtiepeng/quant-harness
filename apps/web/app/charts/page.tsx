import Link from 'next/link'
import { Card, Layout, Space, Statistic, Typography } from 'antd'
import ChartsClient from './ChartsClient'

const { Header, Content } = Layout
const { Title, Paragraph } = Typography

async function getPerformance() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/analytics/strategy-performance', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

export default async function ChartsPage() {
  const items = await getPerformance()
  const best = items[0]

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
            <Title level={2}>Strategy Charts</Title>
            <Paragraph>正式图表版（Recharts + Ant Design 容器）。</Paragraph>
          </Card>

          {best ? (
            <Card>
              <Space size={24}>
                <Statistic title="Best Strategy" value={best.strategy} />
                <Statistic title="Avg 1D" value={best.avg_return_1d} suffix="%" />
                <Statistic title="Win Rate 1D" value={best.win_rate_1d} suffix="%" />
              </Space>
            </Card>
          ) : null}

          <Card title="Performance Overview">
            {items.length ? <ChartsClient data={items} /> : <p>暂无可视化数据。</p>}
          </Card>
        </Space>
      </Content>
    </Layout>
  )
}

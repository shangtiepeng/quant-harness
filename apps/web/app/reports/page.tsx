import Link from 'next/link'
import { Card, Layout, List, Space, Typography } from 'antd'

const { Header, Content, Sider } = Layout
const { Title, Paragraph } = Typography

async function getReports() {
  try {
    const res = await fetch('http://127.0.0.1:8010/api/history/reports', { cache: 'no-store' })
    return await res.json()
  } catch {
    return []
  }
}

async function getDetail(tradeDate?: string) {
  if (!tradeDate) return null
  try {
    const res = await fetch(`http://127.0.0.1:8010/api/history/reports/${tradeDate}`, { cache: 'no-store' })
    return await res.json()
  } catch {
    return null
  }
}

export default async function ReportsPage({ searchParams }: { searchParams: { date?: string } }) {
  const reports = await getReports()
  const selectedDate = searchParams?.date || reports[0]?.trade_date
  const detail = await getDetail(selectedDate)

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
      <Layout>
        <Sider width={320} style={{ background: '#fff', padding: 16, borderRight: '1px solid #f0f0f0' }}>
          <Title level={4}>Reports</Title>
          <List
            bordered
            dataSource={reports}
            renderItem={(item: any) => (
              <List.Item style={{ background: item.trade_date === selectedDate ? '#e6f4ff' : undefined }}>
                <Link href={`/reports?date=${item.trade_date}`}>{item.trade_date}</Link>
              </List.Item>
            )}
          />
        </Sider>
        <Content style={{ padding: 24 }}>
          <Card>
            <Title level={3}>Preview: {selectedDate || 'N/A'}</Title>
            <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{detail?.md || '暂无可预览内容。'}</Paragraph>
          </Card>
        </Content>
      </Layout>
    </Layout>
  )
}

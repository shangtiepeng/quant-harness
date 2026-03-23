'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, Layout, List, Space, Typography } from 'antd'

const { Header, Content, Sider } = Layout
const { Title, Paragraph } = Typography

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([])
  const [selectedDate, setSelectedDate] = useState<string>('')
  const [detail, setDetail] = useState<any>(null)

  useEffect(() => {
    async function load() {
      const res = await fetch('http://127.0.0.1:8010/api/history/reports')
      const data = await res.json()
      setReports(data)
      const first = data[0]?.trade_date || ''
      setSelectedDate(first)
      if (first) {
        const detailRes = await fetch(`http://127.0.0.1:8010/api/history/reports/${first}`)
        setDetail(await detailRes.json())
      }
    }
    load()
  }, [])

  async function selectReport(date: string) {
    setSelectedDate(date)
    const res = await fetch(`http://127.0.0.1:8010/api/history/reports/${date}`)
    setDetail(await res.json())
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
      <Layout>
        <Sider width={320} style={{ background: '#fff', padding: 16, borderRight: '1px solid #f0f0f0' }}>
          <Title level={4}>Reports</Title>
          <List
            bordered
            dataSource={reports}
            renderItem={(item: any) => (
              <List.Item onClick={() => selectReport(item.trade_date)} style={{ cursor: 'pointer', background: item.trade_date === selectedDate ? '#e6f4ff' : undefined }}>
                {item.trade_date}
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

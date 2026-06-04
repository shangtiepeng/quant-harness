'use client'

import { useEffect, useState } from 'react'
import { Alert, Card, Col, Empty, List, Row, Skeleton, Space, Tag, Typography } from 'antd'
import { apiConnectionError, fetchApi } from '../config'
import { AppShell, PageIntro } from '../components/AppShell'

const { Paragraph, Text, Title } = Typography

type ReportItem = {
  trade_date: string
  source?: string
  created_at?: string
}

type ReportDetail = {
  md?: string
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportItem[]>([])
  const [selectedDate, setSelectedDate] = useState('')
  const [detail, setDetail] = useState<ReportDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState('')

  async function fetchJson<T>(path: string, fallback: T): Promise<T> {
    try {
      return await fetchApi<T>(path)
    } catch {
      return fallback
    }
  }

  useEffect(() => {
    let ignore = false

    async function load() {
      setLoading(true)
      setError('')
      try {
        const data = await fetchJson<ReportItem[]>('/api/history/reports', [])
        if (ignore) return
        setReports(data)
        const first = data[0]?.trade_date || ''
        setSelectedDate(first)
        if (first) {
          setDetailLoading(true)
          const detailData = await fetchJson<ReportDetail | null>(`/api/history/reports/${first}`, null)
          if (!ignore) setDetail(detailData)
        }
      } catch (err) {
        if (!ignore) setError(err instanceof Error ? err.message : apiConnectionError().message)
      } finally {
        if (!ignore) {
          setLoading(false)
          setDetailLoading(false)
        }
      }
    }

    load()

    return () => {
      ignore = true
    }
  }, [])

  async function selectReport(date: string) {
    setSelectedDate(date)
    setDetail(null)
    setDetailLoading(true)
    try {
      const detailData = await fetchJson<ReportDetail | null>(`/api/history/reports/${date}`, null)
      setDetail(detailData)
    } finally {
      setDetailLoading(false)
    }
  }

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="研究报告"
          title="历史研究报告"
          description="查看历史日报归档，快速切换日期并预览 Markdown 报告内容。"
        />

        {error ? <Alert type="error" showIcon title="加载失败" description={error} /> : null}

        <Row gutter={[16, 16]} align="stretch">
          <Col xs={24} lg={7}>
            <Card title="报告列表" className="full-height-card">
              {loading ? (
                <Skeleton active paragraph={{ rows: 8 }} />
              ) : reports.length ? (
                <List
                  className="report-list"
                  dataSource={reports}
                  renderItem={(item) => (
                    <List.Item
                      className={item.trade_date === selectedDate ? 'report-list-item report-list-item-active' : 'report-list-item'}
                      onClick={() => selectReport(item.trade_date)}
                    >
                      <Space orientation="vertical" size={4}>
                        <Text strong>{item.trade_date}</Text>
                        <Space wrap>
                          {item.source ? <Tag>{item.source}</Tag> : null}
                          {item.created_at ? <Text type="secondary">{item.created_at}</Text> : null}
                        </Space>
                      </Space>
                    </List.Item>
                  )}
                />
              ) : (
                <Empty description="暂无历史报告" />
              )}
            </Card>
          </Col>
          <Col xs={24} lg={17}>
            <Card className="full-height-card">
              <Space orientation="vertical" size={12} style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">报告预览</Text>
                  <Title level={3} style={{ margin: 0 }}>{selectedDate || '暂无报告'}</Title>
                </div>
                {detailLoading ? (
                  <Skeleton active paragraph={{ rows: 14 }} />
                ) : detail?.md ? (
                  <Paragraph className="markdown-preview">{detail.md}</Paragraph>
                ) : (
                  <Empty description="暂无可预览内容" />
                )}
              </Space>
            </Card>
          </Col>
        </Row>
      </Space>
    </AppShell>
  )
}

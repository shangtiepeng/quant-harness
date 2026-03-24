'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import {
  Card,
  Col,
  Descriptions,
  Divider,
  Layout,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from 'antd'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography

type SignalRow = {
  key: string
  strategy: string
  symbol: string
  name: string
  score: number
  risk_level: string
  reasons: string[]
  entry_note: string
  exit_note: string
  invalidation_note: string
  theme: string
  secondary_theme?: string
  concepts?: string[]
  display: string
}

const strategyLabelMap: Record<string, string> = {
  leader: '龙头',
  hotmoney: '游资',
  sentiment: '情绪',
  composite: '综合',
}

const riskColorMap: Record<string, string> = {
  low: 'green',
  medium: 'orange',
  high: 'red',
}

export default function Page() {
  const [data, setData] = useState<any>({
    meta: null,
    market: null,
    signals: [],
    report: null,
    runs: [],
    validations: [],
    performance: [],
    themeHeat: [],
  })
  const [selectedSignalKey, setSelectedSignalKey] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      const [metaRes, marketRes, signalsRes, reportRes, runsRes, validationsRes, perfRes, themeHeatRes] = await Promise.all([
        fetch('http://127.0.0.1:8010/api/meta'),
        fetch('http://127.0.0.1:8010/api/market/overview'),
        fetch('http://127.0.0.1:8010/api/signals'),
        fetch('http://127.0.0.1:8010/api/report/daily'),
        fetch('http://127.0.0.1:8010/api/history/runs'),
        fetch('http://127.0.0.1:8010/api/history/validations'),
        fetch('http://127.0.0.1:8010/api/analytics/strategy-performance'),
        fetch('http://127.0.0.1:8010/api/themes/heat'),
      ])
      const themeHeatPayload = await themeHeatRes.json()
      const nextData = {
        meta: await metaRes.json(),
        market: await marketRes.json(),
        signals: await signalsRes.json(),
        report: await reportRes.json(),
        runs: await runsRes.json(),
        validations: await validationsRes.json(),
        performance: await perfRes.json(),
        themeHeat: themeHeatPayload.items || [],
      }
      setData(nextData)
    }
    load()
  }, [])

  const signals: SignalRow[] = useMemo(() => {
    return data.signals.map((r: any, i: number) => ({
      ...r,
      key: `${r.strategy}-${r.symbol}-${i}`,
      display: `${r.name} (${r.symbol})`,
    }))
  }, [data.signals])

  useEffect(() => {
    if (!signals.length) {
      setSelectedSignalKey(null)
      return
    }
    if (!selectedSignalKey || !signals.find((item) => item.key === selectedSignalKey)) {
      setSelectedSignalKey(signals[0].key)
    }
  }, [signals, selectedSignalKey])

  const selectedSignal = signals.find((item) => item.key === selectedSignalKey) || null
  const mainlineThemes = data.themeHeat.filter((item: any) => item.is_mainline).map((item: any) => item.theme)
  const selectedThemePeers = selectedSignal
    ? signals.filter(
        (item) => item.key !== selectedSignal.key && item.theme === selectedSignal.theme,
      )
    : []
  const selectedThemeRank = selectedSignal
    ? data.themeHeat.findIndex((item: any) => item.theme === selectedSignal.theme) + 1
    : 0

  const signalColumns = [
    { title: '标的', dataIndex: 'display', key: 'display' },
    {
      title: '策略',
      dataIndex: 'strategy',
      key: 'strategy',
      render: (v: string) => <Tag color="blue">{strategyLabelMap[v] || v}</Tag>,
    },
    {
      title: '主题材',
      dataIndex: 'theme',
      key: 'theme',
      render: (v: string) => <Tag color="gold">{v || '未分类'}</Tag>,
    },
    {
      title: '次题材',
      dataIndex: 'secondary_theme',
      key: 'secondary_theme',
      render: (v: string) => <Tag color="lime">{v || '-'}</Tag>,
    },
    { title: '分数', dataIndex: 'score', key: 'score' },
    {
      title: '风险',
      dataIndex: 'risk_level',
      key: 'risk_level',
      render: (v: string) => <Tag color={riskColorMap[v] || 'default'}>{v}</Tag>,
    },
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

  const themeHeatColumns = [
    {
      title: '题材',
      dataIndex: 'theme',
      key: 'theme',
      render: (v: string, record: any) => (
        <Space wrap>
          <Tag color="volcano">{v}</Tag>
          {record.is_mainline ? <Tag color="red">主线</Tag> : null}
        </Space>
      ),
    },
    { title: '出现数', dataIndex: 'count', key: 'count' },
    { title: '强度分', dataIndex: 'heat_score', key: 'heat_score' },
    {
      title: '代表个股',
      dataIndex: 'leaders',
      key: 'leaders',
      render: (leaders: string[]) => (
        <Space wrap>
          {(leaders || []).map((item) => (
            <Tag key={item}>{item}</Tag>
          ))}
        </Space>
      ),
    },
  ]

  const runs = data.runs.map((r: any) => ({ ...r, key: r.id }))
  const validations = data.validations.map((r: any) => ({ ...r, key: r.id, display: `${r.name} (${r.symbol})` }))
  const performance = data.performance.map((r: any) => ({ ...r, key: r.strategy }))
  const themeHeat = data.themeHeat.map((r: any) => ({ ...r, key: r.theme }))

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
            <Title level={2} style={{ marginBottom: 8 }}>Quant Harness Dashboard</Title>
            <Paragraph style={{ marginBottom: 0 }}>研究优先的 A 股战法系统 MVP</Paragraph>
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

          <Card title="题材热度榜">
            <Table columns={themeHeatColumns} dataSource={themeHeat} pagination={false} />
          </Card>

          <Row gutter={16} align="stretch">
            <Col span={14}>
              <Card title="Top Signals">
                <Table
                  columns={signalColumns}
                  dataSource={signals}
                  pagination={{ pageSize: 6 }}
                  rowClassName={(record: SignalRow) =>
                    record.key === selectedSignalKey ? 'selected-signal-row' : ''
                  }
                  onRow={(record: SignalRow) => ({
                    onClick: () => setSelectedSignalKey(record.key),
                    style: { cursor: 'pointer' },
                  })}
                />
              </Card>
            </Col>
            <Col span={10}>
              <Card title="选中核心说明" style={{ height: '100%' }}>
                {selectedSignal ? (
                  <Space direction="vertical" size={12} style={{ width: '100%' }}>
                    <div>
                      <Title level={4} style={{ marginBottom: 4 }}>{selectedSignal.name}</Title>
                      <Text type="secondary">{selectedSignal.symbol}</Text>
                    </div>

                    <Space wrap>
                      <Tag color="blue">{strategyLabelMap[selectedSignal.strategy] || selectedSignal.strategy}</Tag>
                      <Tag color="gold">主题材：{selectedSignal.theme || '未分类'}</Tag>
                      <Tag color="lime">次题材：{selectedSignal.secondary_theme || '-'}</Tag>
                      <Tag color={riskColorMap[selectedSignal.risk_level] || 'default'}>风险：{selectedSignal.risk_level}</Tag>
                      <Tag color="purple">分数：{selectedSignal.score}</Tag>
                    </Space>

                    <Descriptions column={1} size="small" bordered>
                      <Descriptions.Item label="主题材">
                        {selectedSignal.theme || '未分类'}
                      </Descriptions.Item>
                      <Descriptions.Item label="次题材">
                        {selectedSignal.secondary_theme || '-'}
                      </Descriptions.Item>
                      <Descriptions.Item label="主线判断">
                        {mainlineThemes.includes(selectedSignal.theme) ? '是，属于当前主线题材' : '否，暂不属于主线第一梯队'}
                      </Descriptions.Item>
                      <Descriptions.Item label="题材热度排名">
                        {selectedThemeRank > 0 ? `第 ${selectedThemeRank} 名` : '未进入热度榜'}
                      </Descriptions.Item>
                      <Descriptions.Item label="入场说明">
                        {selectedSignal.entry_note}
                      </Descriptions.Item>
                      <Descriptions.Item label="退出说明">
                        {selectedSignal.exit_note}
                      </Descriptions.Item>
                      <Descriptions.Item label="失效条件">
                        {selectedSignal.invalidation_note}
                      </Descriptions.Item>
                    </Descriptions>

                    <div>
                      <Text strong>概念列表</Text>
                      <Divider style={{ margin: '8px 0 12px' }} />
                      <Space wrap>
                        {(selectedSignal.concepts || []).slice(0, 8).map((concept) => (
                          <Tag key={`${selectedSignal.key}-${concept}`} color="cyan">
                            {concept}
                          </Tag>
                        ))}
                      </Space>
                    </div>

                    <div>
                      <Text strong>同题材代表股对比</Text>
                      <Divider style={{ margin: '8px 0 12px' }} />
                      <Space wrap>
                        {selectedThemePeers.length > 0 ? (
                          selectedThemePeers.slice(0, 6).map((peer) => (
                            <Tag key={peer.key} color="magenta">
                              {peer.name}({peer.symbol}) · {peer.score}
                            </Tag>
                          ))
                        ) : (
                          <Text type="secondary">当前 Top Signals 中暂无更多同题材代表股</Text>
                        )}
                      </Space>
                    </div>

                    <div>
                      <Text strong>核心理由</Text>
                      <Divider style={{ margin: '8px 0 12px' }} />
                      <Space wrap>
                        {selectedSignal.reasons?.map((reason, idx) => (
                          <Tag key={`${selectedSignal.key}-reason-${idx}`} color="geekblue">
                            {reason}
                          </Tag>
                        ))}
                      </Space>
                    </div>
                  </Space>
                ) : (
                  <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                    点击左侧信号行后，这里会显示对应标的的核心说明、题材和交易要点。
                  </Paragraph>
                )}
              </Card>
            </Col>
          </Row>

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

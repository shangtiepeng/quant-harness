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
  resonance_score: number
  resonance_level: 'A' | 'B' | 'C' | 'D'
  resonance_role: string
  resonance_reasons?: string[]
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

const resonanceColorMap: Record<string, string> = {
  A: 'red',
  B: 'volcano',
  C: 'gold',
  D: 'default',
}

const resonanceRoleMap: Record<string, string> = {
  mainline_leader: '主线龙头',
  frontline_core: '前排核心',
  secondary_rotation: '轮动补涨',
  follower: '跟风观察',
  noise: '噪声票',
}

export default function Page() {
  const [data, setData] = useState<any>({
    meta: null,
    market: null,
    signals: [],
    candidates: [],
    portfolioPlan: null,
    paperSummary: null,
    paperPositions: [],
    paperTrades: [],
    report: null,
    runs: [],
    validations: [],
    performance: [],
    themeHeat: [],
  })
  const [selectedSignalKey, setSelectedSignalKey] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      const [metaRes, marketRes, signalsRes, candidatesRes, portfolioPlanRes, paperSummaryRes, paperPositionsRes, paperTradesRes, reportRes, runsRes, validationsRes, perfRes, themeHeatRes] = await Promise.all([
        fetch('http://127.0.0.1:8010/api/meta'),
        fetch('http://127.0.0.1:8010/api/market/overview'),
        fetch('http://127.0.0.1:8010/api/signals'),
        fetch('http://127.0.0.1:8010/api/candidates'),
        fetch('http://127.0.0.1:8010/api/portfolio-plan'),
        fetch('http://127.0.0.1:8010/api/paper/summary'),
        fetch('http://127.0.0.1:8010/api/paper/positions'),
        fetch('http://127.0.0.1:8010/api/paper/trades'),
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
        candidates: await candidatesRes.json(),
        portfolioPlan: await portfolioPlanRes.json(),
        paperSummary: await paperSummaryRes.json(),
        paperPositions: await paperPositionsRes.json(),
        paperTrades: await paperTradesRes.json(),
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

  const candidates = useMemo(() => {
    return data.candidates.map((r: any, i: number) => ({
      ...r,
      key: `candidate-${r.symbol}-${i}`,
    }))
  }, [data.candidates])

  useEffect(() => {
    if (!candidates.length) {
      setSelectedSignalKey(null)
      return
    }
    if (!selectedSignalKey || !candidates.find((item: any) => item.key === selectedSignalKey)) {
      setSelectedSignalKey(candidates[0].key)
    }
  }, [candidates, selectedSignalKey])

  const selectedSignal = candidates.find((item: any) => item.key === selectedSignalKey) || null
  const mainlineThemes = data.themeHeat.filter((item: any) => item.is_mainline).map((item: any) => item.theme)
  const selectedThemePeers = selectedSignal
    ? candidates.filter(
        (item: any) => item.key !== selectedSignal.key && item.theme === selectedSignal.theme,
      )
    : []
  const selectedThemeRank = selectedSignal
    ? data.themeHeat.findIndex((item: any) => item.theme === selectedSignal.theme) + 1
    : 0

  const signalColumns = [
    { title: '候选标的', dataIndex: 'display', key: 'display' },
    {
      title: '策略共识',
      dataIndex: 'strategies',
      key: 'strategies',
      render: (values: string[]) => (
        <Space wrap>
          {(values || []).map((v) => (
            <Tag color="blue" key={v}>{strategyLabelMap[v] || v}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '共振等级',
      dataIndex: 'resonance_level',
      key: 'resonance_level',
      render: (v: string) => <Tag color={resonanceColorMap[v] || 'default'}>{v}</Tag>,
    },
    {
      title: '共振角色',
      dataIndex: 'resonance_role',
      key: 'resonance_role',
      render: (v: string) => <Tag color="purple">{resonanceRoleMap[v] || v}</Tag>,
    },
    {
      title: '主题材',
      dataIndex: 'theme',
      key: 'theme',
      render: (v: string) => <Tag color="gold">{v || '未分类'}</Tag>,
    },
    { title: '共振分', dataIndex: 'resonance_score', key: 'resonance_score' },
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

          <Card title="今日策略组合建议">
            <Row gutter={16}>
              <Col span={6}><Statistic title="Risk Mode" value={data.portfolioPlan?.risk_mode || 'N/A'} /></Col>
              <Col span={6}><Statistic title="Risk Budget" value={data.portfolioPlan?.risk_budget_pct || 0} suffix="%" /></Col>
              <Col span={6}><Statistic title="No Trade" value={data.portfolioPlan?.no_trade ? 'YES' : 'NO'} /></Col>
              <Col span={6}><Statistic title="Plan Count" value={(data.portfolioPlan?.candidate_plan || []).length} /></Col>
            </Row>
            <Divider />
            <Text strong>启用策略</Text>
            <Space wrap style={{ marginTop: 8, marginBottom: 12 }}>
              {(data.portfolioPlan?.strategy_weights || []).map((item: any) => (
                <Tag key={`sw-${item.strategy}`} color="blue">{item.label}: {item.weight_pct}%</Tag>
              ))}
            </Space>
            <Text strong>组合备注</Text>
            <ul style={{ marginTop: 8, paddingLeft: 20 }}>
              {(data.portfolioPlan?.notes || []).map((item: string, idx: number) => (
                <li key={`note-${idx}`}>{item}</li>
              ))}
            </ul>
            <Divider />
            <Table
              pagination={false}
              dataSource={(data.portfolioPlan?.candidate_plan || []).map((item: any) => ({ ...item, key: item.symbol }))}
              columns={[
                { title: '标的', dataIndex: 'display', key: 'display' },
                { title: '目标仓位', dataIndex: 'target_weight_pct', key: 'target_weight_pct', render: (v: number) => `${v}%` },
                { title: '共振等级', dataIndex: 'resonance_level', key: 'resonance_level' },
                { title: '主题材', dataIndex: 'theme', key: 'theme' },
                { title: '策略共识', dataIndex: 'strategies', key: 'strategies', render: (values: string[]) => (values || []).map((v) => strategyLabelMap[v] || v).join(' / ') },
              ]}
            />
          </Card>

          <Card title="Paper Portfolio">
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={4}><Statistic title="Open Positions" value={data.paperSummary?.open_positions || 0} /></Col>
              <Col span={4}><Statistic title="Closed Positions" value={data.paperSummary?.closed_positions || 0} /></Col>
              <Col span={4}><Statistic title="Open Weight" value={data.paperSummary?.open_weight_pct || 0} suffix="%" /></Col>
              <Col span={4}><Statistic title="Unrealized" value={data.paperSummary?.unrealized_pnl_pct || 0} suffix="%" /></Col>
              <Col span={4}><Statistic title="Realized" value={data.paperSummary?.realized_pnl_pct || 0} suffix="%" /></Col>
              <Col span={4}><Statistic title="Win Rate" value={data.paperSummary?.win_rate_pct || 0} suffix="%" /></Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Card size="small" title="Open Positions">
                  <Table
                    pagination={false}
                    dataSource={(data.paperPositions || []).filter((item: any) => item.status === 'open').map((item: any) => ({ ...item, key: `pos-${item.id}` }))}
                    columns={[
                      { title: '标的', dataIndex: 'name', key: 'name' },
                      { title: '仓位', dataIndex: 'target_weight_pct', key: 'target_weight_pct', render: (v: number) => `${v}%` },
                      { title: '开仓日', dataIndex: 'opened_trade_date', key: 'opened_trade_date' },
                      { title: '入场价', dataIndex: 'entry_price', key: 'entry_price' },
                    ]}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small" title="Recent Paper Trades">
                  <Table
                    pagination={false}
                    dataSource={(data.paperTrades || []).slice(0, 8).map((item: any) => ({ ...item, key: `trade-${item.id}` }))}
                    columns={[
                      { title: '日期', dataIndex: 'trade_date', key: 'trade_date' },
                      { title: '标的', dataIndex: 'name', key: 'name' },
                      { title: '方向', dataIndex: 'side', key: 'side' },
                      { title: '价格', dataIndex: 'price', key: 'price' },
                      { title: '仓位', dataIndex: 'weight_pct', key: 'weight_pct', render: (v: number) => `${v}%` },
                    ]}
                  />
                </Card>
              </Col>
            </Row>
          </Card>

          <Card title="Daily Report">
            <Paragraph>{data.report?.summary_cn || '暂无摘要'}</Paragraph>
            <Paragraph type="secondary">{data.report?.summary_en || ''}</Paragraph>
            <Space direction="vertical" size={8} style={{ width: '100%', marginTop: 12 }}>
              <Text strong>主线题材</Text>
              <Space wrap>
                {(data.report?.mainline_themes || []).map((item: string) => (
                  <Tag key={`mainline-${item}`} color="red">{item}</Tag>
                ))}
              </Space>
              <Text strong>强共振候选</Text>
              <Space wrap>
                {(data.report?.focus_candidates || []).map((item: string) => (
                  <Tag key={`focus-${item}`} color="volcano">{item}</Tag>
                ))}
              </Space>
              <Text strong>观察名单</Text>
              <Space wrap>
                {(data.report?.observe_candidates || []).map((item: string) => (
                  <Tag key={`observe-${item}`} color="gold">{item}</Tag>
                ))}
              </Space>
              <Text strong>回避名单</Text>
              <Space wrap>
                {(data.report?.avoid_candidates || []).map((item: string) => (
                  <Tag key={`avoid-${item}`} color="default">{item}</Tag>
                ))}
              </Space>
              <Text strong>明日计划</Text>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {(data.report?.tomorrow_plan || []).map((item: string, idx: number) => (
                  <li key={`plan-${idx}`}>{item}</li>
                ))}
              </ul>
            </Space>
          </Card>

          <Card title="题材热度榜">
            <Table columns={themeHeatColumns} dataSource={themeHeat} pagination={false} />
          </Card>

          <Row gutter={16} align="stretch">
            <Col span={14}>
              <Card title="强共振候选池">
                <Table
                  columns={signalColumns}
                  dataSource={candidates}
                  pagination={{ pageSize: 6 }}
                  rowClassName={(record: any) =>
                    record.key === selectedSignalKey ? 'selected-signal-row' : ''
                  }
                  onRow={(record: any) => ({
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
                      <Space wrap>
                        {(selectedSignal.strategies || []).map((v: string) => (
                          <Tag color="blue" key={v}>{strategyLabelMap[v] || v}</Tag>
                        ))}
                      </Space>
                      <Tag color={resonanceColorMap[selectedSignal.resonance_level] || 'default'}>共振等级：{selectedSignal.resonance_level}</Tag>
                      <Tag color="purple">共振角色：{resonanceRoleMap[selectedSignal.resonance_role] || selectedSignal.resonance_role}</Tag>
                      <Tag color="gold">主题材：{selectedSignal.theme || '未分类'}</Tag>
                      <Tag color="lime">次题材：{selectedSignal.secondary_theme || '-'}</Tag>
                      <Tag color={riskColorMap[selectedSignal.risk_level] || 'default'}>风险：{selectedSignal.risk_level}</Tag>
                      <Tag color="geekblue">策略共识数：{selectedSignal.strategy_count || 0}</Tag>
                      <Tag color="magenta">共振分：{selectedSignal.resonance_score}</Tag>
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
                      <Descriptions.Item label="共振角色">
                        {resonanceRoleMap[selectedSignal.resonance_role] || selectedSignal.resonance_role}
                      </Descriptions.Item>
                      <Descriptions.Item label="共振等级">
                        {selectedSignal.resonance_level}
                      </Descriptions.Item>
                      <Descriptions.Item label="策略共识">
                        {(selectedSignal.strategies || []).map((v: string) => strategyLabelMap[v] || v).join(' / ') || '单策略'}
                      </Descriptions.Item>
                      <Descriptions.Item label="入场说明">
                        {selectedSignal.source_signals?.[0]?.entry_note || '—'}
                      </Descriptions.Item>
                      <Descriptions.Item label="退出说明">
                        {selectedSignal.source_signals?.[0]?.exit_note || '—'}
                      </Descriptions.Item>
                      <Descriptions.Item label="失效条件">
                        {selectedSignal.source_signals?.[0]?.invalidation_note || '—'}
                      </Descriptions.Item>
                    </Descriptions>

                    <div>
                      <Text strong>概念列表</Text>
                      <Divider style={{ margin: '8px 0 12px' }} />
                      <Space wrap>
                        {(selectedSignal.concepts || []).slice(0, 8).map((concept: string) => (
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
                          selectedThemePeers.slice(0, 6).map((peer: any) => (
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
                        {selectedSignal.reasons?.map((reason: string, idx: number) => (
                          <Tag key={`${selectedSignal.key}-reason-${idx}`} color="geekblue">
                            {reason}
                          </Tag>
                        ))}
                      </Space>
                    </div>

                    <div>
                      <Text strong>共振说明</Text>
                      <Divider style={{ margin: '8px 0 12px' }} />
                      <Space wrap>
                        {selectedSignal.resonance_reasons?.map((reason: string, idx: number) => (
                          <Tag key={`${selectedSignal.key}-resonance-${idx}`} color="magenta">
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

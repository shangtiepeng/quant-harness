'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Card,
  Col,
  Descriptions,
  Divider,
  Empty,
  Progress,
  Row,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { apiUrl } from './config'
import { AppShell, MetricCard, PageIntro } from './components/AppShell'

const { Paragraph, Text, Title } = Typography

type ApiRecord = Record<string, unknown>

type DashboardData = {
  meta: ApiRecord | null
  market: ApiRecord | null
  signals: ApiRecord[]
  candidates: ApiRecord[]
  portfolioPlan: ApiRecord | null
  paperSummary: ApiRecord | null
  paperPositions: ApiRecord[]
  paperTrades: ApiRecord[]
  report: ApiRecord | null
  runs: ApiRecord[]
  validations: ApiRecord[]
  performance: ApiRecord[]
  themeHeat: ApiRecord[]
}

type CandidateRow = ApiRecord & {
  key: string
  display: string
  symbol: string
  name: string
  theme: string
  strategies: string[]
  risk_level: string
  resonance_level: string
  resonance_role: string
  resonance_score: number
  secondary_theme?: string
  concepts?: string[]
  reasons?: string[]
  resonance_reasons?: string[]
  strategy_count?: number
  score?: number
  source_signals?: Array<{
    entry_note?: string
    exit_note?: string
    invalidation_note?: string
  }>
}

type TableRow = ApiRecord & {
  key: string
}

const initialData: DashboardData = {
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

function asString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value ? value : fallback
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function asRecordArray(value: unknown): ApiRecord[] {
  return Array.isArray(value) ? value.filter((item): item is ApiRecord => typeof item === 'object' && item !== null && !Array.isArray(item)) : []
}

function strategyLabel(value: string): string {
  return strategyLabelMap[value] || value
}

function percentValue(value: unknown): string {
  return `${asNumber(value)}%`
}

export default function Page() {
  const [data, setData] = useState<DashboardData>(initialData)
  const [selectedSignalKey, setSelectedSignalKey] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let ignore = false

    async function load() {
      setLoading(true)
      setError('')

      const fetchJson = async <T,>(path: string, fallback: T): Promise<T> => {
        try {
          const res = await fetch(apiUrl(path))
          if (!res.ok) return fallback
          return (await res.json()) as T
        } catch {
          return fallback
        }
      }

      try {
        const openApi = await fetchJson<{ paths?: Record<string, unknown> }>('/openapi.json', { paths: {} })
        const paths = openApi?.paths || {}
        const hasPath = (path: string) => Boolean(paths[path])

        const [
          meta,
          market,
          signals,
          candidates,
          portfolioPlan,
          paperSummary,
          paperPositions,
          paperTrades,
          report,
          runs,
          validations,
          performance,
          themeHeatPayload,
        ] = await Promise.all([
          fetchJson<ApiRecord | null>('/api/meta', null),
          fetchJson<ApiRecord | null>('/api/market/overview', null),
          fetchJson<ApiRecord[]>('/api/signals', []),
          hasPath('/api/candidates') ? fetchJson<ApiRecord[]>('/api/candidates', []) : Promise.resolve([]),
          hasPath('/api/portfolio-plan') ? fetchJson<ApiRecord | null>('/api/portfolio-plan', null) : Promise.resolve(null),
          hasPath('/api/paper/summary') ? fetchJson<ApiRecord | null>('/api/paper/summary', null) : Promise.resolve(null),
          hasPath('/api/paper/positions') ? fetchJson<ApiRecord[]>('/api/paper/positions', []) : Promise.resolve([]),
          hasPath('/api/paper/trades') ? fetchJson<ApiRecord[]>('/api/paper/trades', []) : Promise.resolve([]),
          fetchJson<ApiRecord | null>('/api/report/daily', null),
          fetchJson<ApiRecord[]>('/api/history/runs', []),
          fetchJson<ApiRecord[]>('/api/history/validations', []),
          fetchJson<ApiRecord[]>('/api/analytics/strategy-performance', []),
          fetchJson<{ items?: ApiRecord[] }>('/api/themes/heat', { items: [] }),
        ])

        if (ignore) return

        setData({
          meta,
          market,
          signals,
          candidates,
          portfolioPlan,
          paperSummary,
          paperPositions,
          paperTrades,
          report,
          runs,
          validations,
          performance,
          themeHeat: themeHeatPayload.items || [],
        })
      } catch (err) {
        if (!ignore) {
          setError(err instanceof Error ? err.message : '加载失败')
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

  const candidates = useMemo<CandidateRow[]>(() => {
    return data.candidates.map((record, index) => {
      const symbol = asString(record.symbol, '-')
      const name = asString(record.name, '未命名')
      return {
        ...record,
        key: `candidate-${symbol}-${index}`,
        display: `${name} (${symbol})`,
        symbol,
        name,
        theme: asString(record.theme, '未分类'),
        strategies: asStringArray(record.strategies),
        risk_level: asString(record.risk_level, 'medium'),
        resonance_level: asString(record.resonance_level, 'D'),
        resonance_role: asString(record.resonance_role, 'follower'),
        resonance_score: asNumber(record.resonance_score),
        secondary_theme: asString(record.secondary_theme, '-'),
        concepts: asStringArray(record.concepts),
        reasons: asStringArray(record.reasons),
        resonance_reasons: asStringArray(record.resonance_reasons),
        strategy_count: asNumber(record.strategy_count),
        score: asNumber(record.score),
        source_signals: asRecordArray(record.source_signals) as CandidateRow['source_signals'],
      }
    })
  }, [data.candidates])

  useEffect(() => {
    if (!candidates.length) {
      setSelectedSignalKey(null)
      return
    }
    if (!selectedSignalKey || !candidates.find((item) => item.key === selectedSignalKey)) {
      setSelectedSignalKey(candidates[0].key)
    }
  }, [candidates, selectedSignalKey])

  const selectedSignal = candidates.find((item) => item.key === selectedSignalKey) || null
  const themeHeat = data.themeHeat.map((record) => ({ ...record, key: asString(record.theme, String(Math.random())) }))
  const mainlineThemes = data.themeHeat.filter((item) => Boolean(item.is_mainline)).map((item) => asString(item.theme))
  const selectedThemePeers = selectedSignal
    ? candidates.filter((item) => item.key !== selectedSignal.key && item.theme === selectedSignal.theme)
    : []
  const selectedThemeRank = selectedSignal
    ? data.themeHeat.findIndex((item) => asString(item.theme) === selectedSignal.theme) + 1
    : 0
  const candidatePlan = asRecordArray(data.portfolioPlan?.candidate_plan).map((item, index) => ({
    ...item,
    key: asString(item.symbol, `plan-${index}`),
  }))
  const strategyWeights = asRecordArray(data.portfolioPlan?.strategy_weights)
  const openPositions = data.paperPositions
    .filter((item) => item.status === 'open')
    .map((item) => ({ ...item, key: `pos-${String(item.id)}` }))
  const recentTrades = data.paperTrades.slice(0, 8).map((item) => ({ ...item, key: `trade-${String(item.id)}` }))
  const runs = data.runs.map((record) => ({ ...record, key: String(record.id) }))
  const validations = data.validations.map((record) => ({
    ...record,
    key: String(record.id),
    display: `${asString(record.name, '-')} (${asString(record.symbol, '-')})`,
  }))
  const performance = data.performance.map((record) => ({ ...record, key: asString(record.strategy, String(record.bucket || 'strategy')) }))

  const signalColumns: ColumnsType<CandidateRow> = [
    {
      title: '候选标的',
      dataIndex: 'display',
      width: 180,
      render: (value: string, record) => (
        <Space orientation="vertical" size={2}>
          <Text strong>{value}</Text>
          <Text type="secondary">{record.symbol}</Text>
        </Space>
      ),
    },
    {
      title: '策略共识',
      dataIndex: 'strategies',
      width: 180,
      render: (values: string[]) => (
        <Space wrap>
          {values.map((value) => <Tag color="blue" key={value}>{strategyLabel(value)}</Tag>)}
        </Space>
      ),
    },
    {
      title: '共振等级',
      dataIndex: 'resonance_level',
      width: 110,
      render: (value: string) => <Tag color={resonanceColorMap[value] || 'default'}>{value}</Tag>,
    },
    {
      title: '共振角色',
      dataIndex: 'resonance_role',
      width: 136,
      render: (value: string) => <Tag color="purple">{resonanceRoleMap[value] || value}</Tag>,
    },
    {
      title: '主题材',
      dataIndex: 'theme',
      width: 136,
      render: (value: string) => <Tag color="gold">{value || '未分类'}</Tag>,
    },
    {
      title: '共振分',
      dataIndex: 'resonance_score',
      width: 150,
      render: (value: number) => (
        <Space orientation="vertical" size={2} style={{ width: 120 }}>
          <Text strong>{value}</Text>
          <Progress percent={value} size="small" showInfo={false} />
        </Space>
      ),
    },
    {
      title: '风险',
      dataIndex: 'risk_level',
      width: 100,
      render: (value: string) => <Tag color={riskColorMap[value] || 'default'}>{value}</Tag>,
    },
  ]

  const planColumns: ColumnsType<TableRow> = [
    { title: '标的', dataIndex: 'display', key: 'display', width: 180 },
    { title: '目标仓位', dataIndex: 'target_weight_pct', key: 'target_weight_pct', width: 120, render: percentValue },
    { title: '共振等级', dataIndex: 'resonance_level', key: 'resonance_level', width: 120 },
    { title: '主题材', dataIndex: 'theme', key: 'theme', width: 140 },
    {
      title: '策略共识',
      dataIndex: 'strategies',
      key: 'strategies',
      width: 220,
      render: (values: unknown) => asStringArray(values).map(strategyLabel).join(' / '),
    },
  ]

  const runColumns: ColumnsType<TableRow> = [
    { title: 'Run ID', dataIndex: 'id', key: 'id', width: 220 },
    { title: '日期', dataIndex: 'trade_date', key: 'trade_date', width: 130 },
    { title: '数据源', dataIndex: 'source', key: 'source', width: 120 },
    { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 220 },
  ]

  const validationColumns: ColumnsType<TableRow> = [
    { title: '标的', dataIndex: 'display', key: 'display', width: 180 },
    { title: '策略', dataIndex: 'strategy', key: 'strategy', width: 120 },
    { title: '1D%', dataIndex: 'return_1d', key: 'return_1d', width: 100 },
    { title: '3D%', dataIndex: 'return_3d', key: 'return_3d', width: 100 },
    { title: '5D%', dataIndex: 'return_5d', key: 'return_5d', width: 100 },
    { title: '结果', dataIndex: 'outcome_label', key: 'outcome_label', width: 120 },
  ]

  const perfColumns: ColumnsType<TableRow> = [
    { title: '策略', dataIndex: 'strategy', key: 'strategy', width: 120 },
    { title: '样本数', dataIndex: 'count', key: 'count', width: 100 },
    { title: 'Avg 1D', dataIndex: 'avg_return_1d', key: 'avg_return_1d', width: 110 },
    { title: 'Avg 3D', dataIndex: 'avg_return_3d', key: 'avg_return_3d', width: 110 },
    { title: 'Avg 5D', dataIndex: 'avg_return_5d', key: 'avg_return_5d', width: 110 },
    { title: 'Win Rate 1D', dataIndex: 'win_rate_1d', key: 'win_rate_1d', width: 130 },
  ]

  const themeHeatColumns: ColumnsType<TableRow> = [
    {
      title: '题材',
      dataIndex: 'theme',
      key: 'theme',
      width: 180,
      render: (value: unknown, record) => (
        <Space wrap>
          <Tag color="volcano">{asString(value, '未分类')}</Tag>
          {record.is_mainline ? <Tag color="red">主线</Tag> : null}
        </Space>
      ),
    },
    { title: '出现数', dataIndex: 'count', key: 'count', width: 90 },
    { title: '强度分', dataIndex: 'heat_score', key: 'heat_score', width: 100 },
    {
      title: '代表个股',
      dataIndex: 'leaders',
      key: 'leaders',
      width: 280,
      render: (leaders: unknown) => (
        <Space wrap>
          {asStringArray(leaders).map((item) => <Tag key={item}>{item}</Tag>)}
        </Space>
      ),
    },
  ]

  const positionColumns: ColumnsType<TableRow> = [
    { title: '标的', dataIndex: 'name', key: 'name', width: 120 },
    { title: '仓位', dataIndex: 'target_weight_pct', key: 'target_weight_pct', width: 100, render: percentValue },
    { title: '开仓日', dataIndex: 'opened_trade_date', key: 'opened_trade_date', width: 130 },
    { title: '入场价', dataIndex: 'entry_price', key: 'entry_price', width: 100 },
  ]

  const tradeColumns: ColumnsType<TableRow> = [
    { title: '日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
    { title: '标的', dataIndex: 'name', key: 'name', width: 120 },
    { title: '方向', dataIndex: 'side', key: 'side', width: 90 },
    { title: '价格', dataIndex: 'price', key: 'price', width: 100 },
    { title: '仓位', dataIndex: 'weight_pct', key: 'weight_pct', width: 100, render: percentValue },
  ]

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="Dashboard"
          title="Quant Harness Dashboard"
          description="研究优先的 A 股战法系统：汇总市场情绪、策略共振、组合建议、模拟持仓和验证表现。"
        />

        {error ? <Alert type="error" showIcon title="加载失败" description={error} /> : null}

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} xl={6}>
            <MetricCard title="Data Source" value={asString(data.meta?.source, 'N/A')} />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <MetricCard title="Trade Date" value={asString(data.meta?.trade_date, 'N/A')} />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <MetricCard title="Sentiment" value={asString(data.market?.market_sentiment_stage, 'N/A')} />
          </Col>
          <Col xs={24} sm={12} xl={6}>
            <MetricCard title="Highest Board" value={asNumber(data.market?.highest_board)} />
          </Col>
        </Row>

        <Card title="今日策略组合建议" loading={loading}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Risk Mode" value={asString(data.portfolioPlan?.risk_mode, 'N/A')} />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Exec Policy" value={asString(data.portfolioPlan?.execution_policy, 'N/A')} />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Risk Budget" value={asNumber(data.portfolioPlan?.risk_budget_pct)} suffix="%" />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Max Positions" value={asNumber(data.portfolioPlan?.max_positions)} />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Theme Cap" value={asNumber(data.portfolioPlan?.max_theme_exposure_pct)} suffix="%" />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="No Trade" value={data.portfolioPlan?.no_trade ? 'YES' : 'NO'} />
            </Col>
          </Row>

          <Divider />
          <Space orientation="vertical" size={12} style={{ width: '100%' }}>
            <div>
              <Text strong>启用策略</Text>
              <div className="tag-block">
                {strategyWeights.length ? strategyWeights.map((item) => (
                  <Tag key={`sw-${asString(item.strategy)}`} color="blue">
                    {asString(item.label)}: 权重 {asNumber(item.weight_pct)}% / 暴露 {asNumber(item.planned_pct)}% / 上限 {asNumber(item.cap_pct)}%
                  </Tag>
                )) : <Text type="secondary">暂无策略权重。</Text>}
              </div>
            </div>
            <div>
              <Text strong>组合备注</Text>
              <ul className="compact-list">
                {asStringArray(data.portfolioPlan?.notes).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <Table
              className="app-table"
              pagination={false}
              dataSource={candidatePlan}
              columns={planColumns}
              scroll={{ x: 820 }}
              size="middle"
            />
          </Space>
        </Card>

        <Card title="Paper Portfolio" loading={loading}>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Open Positions" value={asNumber(data.paperSummary?.open_positions)} />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Closed Positions" value={asNumber(data.paperSummary?.closed_positions)} />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Open Weight" value={asNumber(data.paperSummary?.open_weight_pct)} suffix="%" />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Unrealized" value={asNumber(data.paperSummary?.unrealized_pnl_pct)} suffix="%" />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Realized" value={asNumber(data.paperSummary?.realized_pnl_pct)} suffix="%" />
            </Col>
            <Col xs={24} sm={12} xl={4}>
              <MetricCard title="Win Rate" value={asNumber(data.paperSummary?.win_rate_pct)} suffix="%" />
            </Col>
          </Row>
          <Row gutter={[16, 16]}>
            <Col xs={24} xl={12}>
              <div className="embedded-panel">
                <Text strong>Open Positions</Text>
                <Table
                  className="app-table"
                  pagination={false}
                  dataSource={openPositions}
                  columns={positionColumns}
                  scroll={{ x: 520 }}
                  size="small"
                />
              </div>
            </Col>
            <Col xs={24} xl={12}>
              <div className="embedded-panel">
                <Text strong>Recent Paper Trades</Text>
                <Table
                  className="app-table"
                  pagination={false}
                  dataSource={recentTrades}
                  columns={tradeColumns}
                  scroll={{ x: 560 }}
                  size="small"
                />
              </div>
            </Col>
          </Row>
        </Card>

        <Card title="Daily Report" loading={loading}>
          <Paragraph>{asString(data.report?.summary_cn, '暂无摘要')}</Paragraph>
          <Paragraph type="secondary">{asString(data.report?.summary_en)}</Paragraph>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Text strong>主线题材</Text>
              <div className="tag-block">
                {asStringArray(data.report?.mainline_themes).map((item) => <Tag key={item} color="red">{item}</Tag>)}
              </div>
            </Col>
            <Col xs={24} md={12}>
              <Text strong>强共振候选</Text>
              <div className="tag-block">
                {asStringArray(data.report?.focus_candidates).map((item) => <Tag key={item} color="volcano">{item}</Tag>)}
              </div>
            </Col>
            <Col xs={24} md={12}>
              <Text strong>观察名单</Text>
              <div className="tag-block">
                {asStringArray(data.report?.observe_candidates).map((item) => <Tag key={item} color="gold">{item}</Tag>)}
              </div>
            </Col>
            <Col xs={24} md={12}>
              <Text strong>回避名单</Text>
              <div className="tag-block">
                {asStringArray(data.report?.avoid_candidates).map((item) => <Tag key={item}>{item}</Tag>)}
              </div>
            </Col>
          </Row>
          <Divider />
          <Text strong>明日计划</Text>
          <ul className="compact-list">
            {asStringArray(data.report?.tomorrow_plan).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </Card>

        <Row gutter={[16, 16]} align="stretch">
          <Col xs={24} xl={10}>
            <Card title="题材热度榜" loading={loading} style={{ height: '100%' }}>
              <Table
                className="app-table"
                columns={themeHeatColumns}
                dataSource={themeHeat}
                pagination={{ pageSize: 6 }}
                scroll={{ x: 680 }}
                size="middle"
              />
            </Card>
          </Col>
          <Col xs={24} xl={14}>
            <Card title="强共振候选池" loading={loading} style={{ height: '100%' }}>
              <Table
                className="app-table"
                columns={signalColumns}
                dataSource={candidates}
                pagination={{ pageSize: 6 }}
                scroll={{ x: 980 }}
                rowClassName={(record) => record.key === selectedSignalKey ? 'selected-signal-row' : ''}
                onRow={(record) => ({
                  onClick: () => setSelectedSignalKey(record.key),
                  style: { cursor: 'pointer' },
                })}
              />
            </Card>
          </Col>
        </Row>

        <Card title="选中核心说明">
          {selectedSignal ? (
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={10}>
                <Title level={4} style={{ marginBottom: 4 }}>{selectedSignal.name}</Title>
                <Text type="secondary">{selectedSignal.symbol}</Text>
                <div className="tag-block">
                  {selectedSignal.strategies.map((value) => <Tag color="blue" key={value}>{strategyLabel(value)}</Tag>)}
                  <Tag color={resonanceColorMap[selectedSignal.resonance_level] || 'default'}>共振等级：{selectedSignal.resonance_level}</Tag>
                  <Tag color="purple">共振角色：{resonanceRoleMap[selectedSignal.resonance_role] || selectedSignal.resonance_role}</Tag>
                  <Tag color="gold">主题材：{selectedSignal.theme}</Tag>
                  <Tag color="lime">次题材：{selectedSignal.secondary_theme || '-'}</Tag>
                  <Tag color={riskColorMap[selectedSignal.risk_level] || 'default'}>风险：{selectedSignal.risk_level}</Tag>
                  <Tag color="magenta">共振分：{selectedSignal.resonance_score}</Tag>
                </div>
              </Col>
              <Col xs={24} lg={14}>
                <Descriptions column={1} size="small" bordered>
                  <Descriptions.Item label="主线判断">
                    {mainlineThemes.includes(selectedSignal.theme) ? '是，属于当前主线题材' : '否，暂不属于主线第一梯队'}
                  </Descriptions.Item>
                  <Descriptions.Item label="题材热度排名">
                    {selectedThemeRank > 0 ? `第 ${selectedThemeRank} 名` : '未进入热度榜'}
                  </Descriptions.Item>
                  <Descriptions.Item label="策略共识">
                    {selectedSignal.strategies.map(strategyLabel).join(' / ') || '单策略'}
                  </Descriptions.Item>
                  <Descriptions.Item label="入场说明">
                    {selectedSignal.source_signals?.[0]?.entry_note || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="退出说明">
                    {selectedSignal.source_signals?.[0]?.exit_note || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="失效条件">
                    {selectedSignal.source_signals?.[0]?.invalidation_note || '-'}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
              <Col xs={24} md={12}>
                <Text strong>概念列表</Text>
                <div className="tag-block">
                  {(selectedSignal.concepts || []).slice(0, 8).map((concept) => (
                    <Tag key={`${selectedSignal.key}-${concept}`} color="cyan">{concept}</Tag>
                  ))}
                </div>
              </Col>
              <Col xs={24} md={12}>
                <Text strong>同题材代表股对比</Text>
                <div className="tag-block">
                  {selectedThemePeers.length > 0 ? selectedThemePeers.slice(0, 6).map((peer) => (
                    <Tag key={peer.key} color="magenta">
                      {peer.name}({peer.symbol}) · {peer.score}
                    </Tag>
                  )) : <Text type="secondary">当前候选池中暂无更多同题材代表股。</Text>}
                </div>
              </Col>
              <Col xs={24} md={12}>
                <Text strong>核心理由</Text>
                <div className="tag-block">
                  {(selectedSignal.reasons || []).map((reason) => (
                    <Tag key={`${selectedSignal.key}-reason-${reason}`} color="geekblue">{reason}</Tag>
                  ))}
                </div>
              </Col>
              <Col xs={24} md={12}>
                <Text strong>共振说明</Text>
                <div className="tag-block">
                  {(selectedSignal.resonance_reasons || []).map((reason) => (
                    <Tag key={`${selectedSignal.key}-resonance-${reason}`} color="magenta">{reason}</Tag>
                  ))}
                </div>
              </Col>
            </Row>
          ) : (
            <Empty description="点击候选行后显示对应标的说明" />
          )}
        </Card>

        <Row gutter={[16, 16]}>
          <Col xs={24} xl={10}>
            <Card title="Historical Runs" loading={loading}>
              <Table className="app-table" columns={runColumns} dataSource={runs} pagination={{ pageSize: 5 }} scroll={{ x: 690 }} />
            </Card>
          </Col>
          <Col xs={24} xl={14}>
            <Card title="Validation Results" loading={loading}>
              <Table className="app-table" columns={validationColumns} dataSource={validations} pagination={{ pageSize: 5 }} scroll={{ x: 720 }} />
            </Card>
          </Col>
        </Row>

        <Card title="Strategy Performance" loading={loading}>
          <Table className="app-table" columns={perfColumns} dataSource={performance} pagination={false} scroll={{ x: 690 }} />
        </Card>
      </Space>
    </AppShell>
  )
}

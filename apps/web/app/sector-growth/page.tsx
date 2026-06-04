'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Card,
  Col,
  Descriptions,
  Divider,
  Progress,
  Row,
  Space,
  Statistic,
  Table,
  Tabs,
  Tag,
  Typography,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { apiConnectionError, apiUrl } from '../config'
import { AppShell, PageIntro } from '../components/AppShell'

const { Title, Paragraph, Text } = Typography

type TrackMode = 'early_alpha' | 'structural'

const modeCopy: Record<TrackMode, {
  tab: string
  title: string
  description: string
  topTitle: string
  tableTitle: string
  scoreFallback: string
}> = {
  early_alpha: {
    tab: '下一波推理赛道',
    title: '推理下一波赛道模型',
    description: '用“渗透率拐点、推理负载拉动、供应链瓶颈、商业催化、低拥挤度”寻找还没完全成长起来、但可能进入下一轮高增长的推理细分赛道。',
    topTitle: '高优先级埋伏方向',
    tableTitle: '推理下一波排名',
    scoreFallback: '埋伏分',
  },
  structural: {
    tab: '当前热门赛道',
    title: '当前结构性热门赛道',
    description: '保留已经成长起来、确定性更高的结构性高景气方向，用政策、需求、生态、国产替代、商业化和市场热度做排序。',
    topTitle: '当前热门高增长方向',
    tableTitle: '结构性增长排名',
    scoreFallback: '增长分',
  },
}

type FactorScores = {
  policy?: number
  demand?: number
  penetration_inflection?: number
  inference_pull?: number
  supply_bottleneck?: number
  business_catalyst?: number
  underowned?: number
  tech_readiness: number
  ecosystem: number
  localization?: number
  commercialization: number
  capital_efficiency: number
  risk: number
}

type LiveSnapshot = {
  pct_change: number
  volume_ratio: number
  theme: string
}

type TypicalCompany = {
  name: string
  symbol: string
  market: string
  role: string
  company_score: number
  exposure_score: number
  maturity_score: number
  rationale: string
  risk_note: string
  live_snapshot: LiveSnapshot | null
}

type MatchedTheme = {
  theme: string
  rank: number
  heat_score: number
  is_mainline: boolean
}

type MatchedSymbol = {
  symbol: string
  name: string
  theme: string
  pct_change: number
  volume_ratio: number
}

type GrowthTrack = {
  track_id: string
  sector: string
  segment: string
  horizon: string
  growth_score: number
  early_alpha_score?: number
  confidence_score: number
  confidence_level: string
  stage: string
  market_heat_score: number
  underowned_score?: number
  maturity_penalty?: number
  crowding_penalty?: number
  accumulation_window?: string
  trigger_events?: string[]
  matched_market_themes: MatchedTheme[]
  matched_market_symbols: MatchedSymbol[]
  factor_scores: FactorScores
  growth_drivers: string[]
  risk_factors: string[]
  evidence_tags: string[]
  typical_companies: TypicalCompany[]
  research_note: string
}

type GrowthTrackRow = GrowthTrack & {
  key: string
  rank: number
}

type PolicySource = {
  name: string
  url: string
  note: string
}

type SectorGrowthPayload = {
  model_version: string
  mode: string
  score_label: string
  trade_date: string
  source_meta: {
    market_source: string
    market_heat_enabled: boolean
    policy_sources: PolicySource[]
  }
  methodology: {
    score_formula: string
    disclaimer: string
  }
  items: GrowthTrack[]
}

const confidenceColor: Record<string, string> = {
  高: 'red',
  中: 'gold',
  低: 'default',
}

function scoreColor(score: number): string {
  if (score >= 80) return '#cf1322'
  if (score >= 70) return '#d46b08'
  if (score >= 60) return '#389e0d'
  return '#595959'
}

export default function SectorGrowthPage() {
  const [activeMode, setActiveMode] = useState<TrackMode>('early_alpha')
  const [payloads, setPayloads] = useState<Partial<Record<TrackMode, SectorGrowthPayload>>>({})
  const [selectedTrackIds, setSelectedTrackIds] = useState<Partial<Record<TrackMode, string>>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const copy = modeCopy[activeMode]
  const payload = payloads[activeMode] || null
  const selectedTrackId = selectedTrackIds[activeMode] || ''

  useEffect(() => {
    setError('')
    if (payloads[activeMode]) return

    let ignore = false

    async function load() {
      setLoading(true)
      try {
        const res = await fetch(apiUrl(`/api/research/sector-growth?limit=12&include_market_heat=true&market_limit=120&mode=${activeMode}`))
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }
        const json = (await res.json()) as SectorGrowthPayload
        if (ignore) return
        setPayloads((current) => ({ ...current, [activeMode]: json }))
        setSelectedTrackIds((current) => ({ ...current, [activeMode]: current[activeMode] || json.items[0]?.track_id || '' }))
      } catch (err) {
        if (ignore) return
        setError(err instanceof Error ? err.message : apiConnectionError().message)
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
  }, [activeMode, payloads])

  const items = useMemo(() => {
    return (payload?.items || []).map((item, index) => ({
      ...item,
      key: item.track_id,
      rank: index + 1,
    }))
  }, [payload])

  const selected = items.find((item) => item.track_id === selectedTrackId) || items[0]
  const topThree = items.slice(0, 3)
  const avgGrowth = items.length
    ? Math.round(items.reduce((sum, item) => sum + item.growth_score, 0) / items.length)
    : 0
  const scoreLabel = payload?.score_label || copy.scoreFallback

  function selectTrack(trackId: string) {
    setSelectedTrackIds((current) => ({ ...current, [activeMode]: trackId }))
  }

  const trackColumns: ColumnsType<GrowthTrackRow> = [
    {
      title: '排名',
      dataIndex: 'rank',
      width: 72,
      align: 'center',
    },
    {
      title: '推理赛道',
      dataIndex: 'sector',
      width: 320,
      render: (value: string, record) => (
        <div className="sector-track-name">
          <Text strong className="sector-track-title">{value}</Text>
          <Text type="secondary" className="sector-track-segment">{record.segment}</Text>
        </div>
      ),
    },
    {
      title: scoreLabel,
      dataIndex: 'growth_score',
      width: 170,
      render: (value: number) => (
        <Space orientation="vertical" size={2} style={{ width: 140 }}>
          <Text strong style={{ color: scoreColor(value) }}>{value}</Text>
          <Progress percent={value} size="small" strokeColor={scoreColor(value)} showInfo={false} />
        </Space>
      ),
    },
    {
      title: '信心',
      dataIndex: 'confidence_level',
      width: 126,
      render: (value: string, record) => (
        <Tag color={confidenceColor[value] || 'default'}>{value} · {record.confidence_score}</Tag>
      ),
    },
    {
      title: '阶段',
      dataIndex: 'stage',
      width: 130,
      render: (value: string) => <Tag color="blue">{value}</Tag>,
    },
    {
      title: '低拥挤',
      dataIndex: 'underowned_score',
      width: 104,
      align: 'center',
      render: (value: number | undefined) => value ?? '-',
    },
    {
      title: '周期',
      dataIndex: 'horizon',
      width: 104,
      align: 'center',
    },
    {
      title: '热度',
      dataIndex: 'market_heat_score',
      width: 96,
      align: 'center',
    },
  ]

  const companyColumns: ColumnsType<TypicalCompany> = [
    {
      title: '公司',
      dataIndex: 'name',
      width: 160,
      render: (value: string, record) => (
        <Space orientation="vertical" size={2} className="sector-company-name">
          <Text strong>{value}</Text>
          <Text type="secondary">{record.symbol} · {record.market}</Text>
        </Space>
      ),
    },
    {
      title: '产业角色',
      dataIndex: 'role',
      width: 150,
      render: (value: string) => <Tag color="geekblue">{value}</Tag>,
    },
    {
      title: '公司匹配分',
      dataIndex: 'company_score',
      width: 130,
      render: (value: number) => <Text strong style={{ color: scoreColor(value) }}>{value}</Text>,
    },
    {
      title: '逻辑',
      dataIndex: 'rationale',
      width: 300,
    },
    {
      title: '风险',
      dataIndex: 'risk_note',
      width: 280,
    },
    {
      title: '实时观察',
      dataIndex: 'live_snapshot',
      width: 150,
      render: (value: LiveSnapshot | null) => value ? (
        <Space orientation="vertical" size={2}>
          <Text>{value.pct_change}%</Text>
          <Text type="secondary">量比 {value.volume_ratio}</Text>
          <Text type="secondary">{value.theme}</Text>
        </Space>
      ) : (
        <Text type="secondary">未匹配</Text>
      ),
    },
  ]

  return (
    <AppShell>
      <Space orientation="vertical" size={16} style={{ width: '100%' }}>
        <PageIntro
          eyebrow="赛道雷达"
          title={copy.title}
          description={copy.description}
        />

        <Tabs
          activeKey={activeMode}
          className="mode-tabs"
          items={[
            { key: 'early_alpha', label: modeCopy.early_alpha.tab },
            { key: 'structural', label: modeCopy.structural.tab },
          ]}
          onChange={(key) => setActiveMode(key as TrackMode)}
        />

        {error ? <Alert type="error" showIcon title="加载失败" description={error} /> : null}

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="模型版本" value={payload?.model_version || '暂无'} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="研究日期" value={payload?.trade_date || '暂无'} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title={`平均${scoreLabel}`} value={avgGrowth} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="市场热度源" value={payload?.source_meta.market_source || '暂无'} />
            </Card>
          </Col>
        </Row>

        <Card title={copy.topTitle} loading={loading && !topThree.length}>
          <Row gutter={[16, 16]}>
            {topThree.map((item) => (
              <Col xs={24} lg={8} key={`top-${item.track_id}`}>
                <div
                  className={`sector-track-tile${item.track_id === selected?.track_id ? ' sector-track-tile-active' : ''}`}
                  onClick={() => selectTrack(item.track_id)}
                >
                  <Space orientation="vertical" size={8} style={{ width: '100%' }}>
                    <Space wrap>
                      <Tag color="red">#{item.rank}</Tag>
                      <Tag color={confidenceColor[item.confidence_level] || 'default'}>信心 {item.confidence_level}</Tag>
                      <Tag color="blue">{item.stage}</Tag>
                      {item.underowned_score ? <Tag color="cyan">低拥挤 {item.underowned_score}</Tag> : null}
                    </Space>
                    <Title level={4} style={{ margin: 0 }}>{item.sector}</Title>
                    <Text type="secondary">{item.segment}</Text>
                    <Progress percent={item.growth_score} strokeColor={scoreColor(item.growth_score)} />
                    <Text>{item.research_note}</Text>
                  </Space>
                </div>
              </Col>
            ))}
          </Row>
        </Card>

        <Row gutter={[16, 16]} align="stretch">
          <Col xs={24} xxl={15}>
            <Card title={copy.tableTitle}>
              <Table
                className="sector-growth-table"
                columns={trackColumns}
                dataSource={items}
                loading={loading}
                pagination={false}
                scroll={{ x: 1152 }}
                size="middle"
                rowClassName={(record) => record.track_id === selected?.track_id ? 'selected-signal-row' : ''}
                onRow={(record) => ({
                  onClick: () => selectTrack(record.track_id),
                  style: { cursor: 'pointer' },
                })}
              />
            </Card>
          </Col>
          <Col xs={24} xxl={9}>
            <Card title="选中赛道拆解" style={{ height: '100%' }}>
              {selected ? (
                <Space orientation="vertical" size={12} style={{ width: '100%' }}>
                  <div>
                    <Title level={3} style={{ marginBottom: 4 }}>{selected.sector}</Title>
                    <Text type="secondary">{selected.segment}</Text>
                  </div>
                  <Space wrap>
                    <Tag color="red">{scoreLabel} {selected.growth_score}</Tag>
                    <Tag color={confidenceColor[selected.confidence_level] || 'default'}>信心 {selected.confidence_level}</Tag>
                    <Tag color="blue">{selected.stage}</Tag>
                    <Tag color="gold">{selected.horizon}</Tag>
                    {selected.underowned_score ? <Tag color="cyan">低拥挤 {selected.underowned_score}</Tag> : null}
                  </Space>
                  <Descriptions column={1} size="small" bordered>
                    {selected.factor_scores.penetration_inflection ? (
                      <Descriptions.Item label="渗透拐点">{selected.factor_scores.penetration_inflection}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.inference_pull ? (
                      <Descriptions.Item label="推理拉动">{selected.factor_scores.inference_pull}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.supply_bottleneck ? (
                      <Descriptions.Item label="瓶颈属性">{selected.factor_scores.supply_bottleneck}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.business_catalyst ? (
                      <Descriptions.Item label="商业催化">{selected.factor_scores.business_catalyst}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.underowned ? (
                      <Descriptions.Item label="低拥挤度">{selected.factor_scores.underowned}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.policy ? (
                      <Descriptions.Item label="政策牵引">{selected.factor_scores.policy}</Descriptions.Item>
                    ) : null}
                    {selected.factor_scores.demand ? (
                      <Descriptions.Item label="需求空间">{selected.factor_scores.demand}</Descriptions.Item>
                    ) : null}
                    <Descriptions.Item label="技术成熟度">{selected.factor_scores.tech_readiness}</Descriptions.Item>
                    <Descriptions.Item label="产业生态">{selected.factor_scores.ecosystem}</Descriptions.Item>
                    {selected.factor_scores.localization ? (
                      <Descriptions.Item label="国产替代">{selected.factor_scores.localization}</Descriptions.Item>
                    ) : null}
                    <Descriptions.Item label="商业化">{selected.factor_scores.commercialization}</Descriptions.Item>
                    <Descriptions.Item label="资本效率">{selected.factor_scores.capital_efficiency}</Descriptions.Item>
                    <Descriptions.Item label="风险分">{selected.factor_scores.risk}</Descriptions.Item>
                    {selected.maturity_penalty ? (
                      <Descriptions.Item label="成熟惩罚">{selected.maturity_penalty}</Descriptions.Item>
                    ) : null}
                    {selected.crowding_penalty ? (
                      <Descriptions.Item label="拥挤惩罚">{selected.crowding_penalty}</Descriptions.Item>
                    ) : null}
                  </Descriptions>
                  {selected.accumulation_window ? (
                    <Alert type="info" showIcon title="埋伏窗口" description={selected.accumulation_window} />
                  ) : null}
                  {selected.trigger_events?.length ? (
                    <div>
                      <Text strong>触发事件</Text>
                      <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                        {selected.trigger_events.map((item) => (
                          <li key={`trigger-${item}`}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                  <div>
                    <Text strong>增长驱动</Text>
                    <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                      {selected.growth_drivers.map((item) => (
                        <li key={`driver-${item}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <Text strong>主要风险</Text>
                    <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                      {selected.risk_factors.map((item) => (
                        <li key={`risk-${item}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <Text strong>证据标签</Text>
                    <Divider style={{ margin: '8px 0 12px' }} />
                    <Space wrap>
                      {selected.evidence_tags.map((item) => (
                        <Tag key={`evidence-${item}`} color="cyan">{item}</Tag>
                      ))}
                    </Space>
                  </div>
                  <div>
                    <Text strong>当前市场匹配</Text>
                    <Divider style={{ margin: '8px 0 12px' }} />
                    <Space wrap>
                      {selected.matched_market_themes.length ? selected.matched_market_themes.map((item) => (
                        <Tag key={`theme-${item.theme}`} color={item.is_mainline ? 'red' : 'volcano'}>
                          {item.theme} · 热度 {item.heat_score}
                        </Tag>
                      )) : <Text type="secondary">暂无强匹配题材</Text>}
                    </Space>
                  </div>
                </Space>
              ) : (
                <Text type="secondary">暂无数据</Text>
              )}
            </Card>
          </Col>
        </Row>

        <Card title={`典型公司${selected ? `：${selected.sector}` : ''}`}>
          <Table
            className="sector-growth-table"
            columns={companyColumns}
            dataSource={(selected?.typical_companies || []).map((item) => ({ ...item, key: item.symbol }))}
            loading={loading}
            pagination={false}
            scroll={{ x: 1240 }}
            size="middle"
          />
        </Card>

        <Card title="政策与模型说明">
          <Paragraph>{payload?.methodology.score_formula || ''}</Paragraph>
          <Alert
            type="info"
            showIcon
            title={payload?.methodology.disclaimer || '模型仅用于研究。'}
            style={{ marginBottom: 16 }}
          />
          <Space orientation="vertical" size={8} style={{ width: '100%' }}>
            {(payload?.source_meta.policy_sources || []).map((item) => (
              <div className="sector-policy-source" key={item.url}>
                <Space orientation="vertical" size={4}>
                  <a href={item.url} target="_blank" rel="noreferrer">{item.name}</a>
                  <Text type="secondary">{item.note}</Text>
                </Space>
              </div>
            ))}
          </Space>
        </Card>
      </Space>
    </AppShell>
  )
}

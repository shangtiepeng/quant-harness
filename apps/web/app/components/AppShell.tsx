'use client'

import type { ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BarChartOutlined, DashboardOutlined, FileTextOutlined, PlayCircleOutlined, RadarChartOutlined } from '@ant-design/icons'
import { Card, Layout, Space, Statistic, Typography } from 'antd'

const { Header, Content } = Layout
const { Text, Title } = Typography

const navItems = [
  { href: '/', label: 'Dashboard', icon: <DashboardOutlined /> },
  { href: '/sector-growth', label: 'Sector Growth', icon: <RadarChartOutlined /> },
  { href: '/run-job', label: 'Run Job', icon: <PlayCircleOutlined /> },
  { href: '/reports', label: 'Reports', icon: <FileTextOutlined /> },
  { href: '/charts', label: 'Charts', icon: <BarChartOutlined /> },
]

function isActivePath(pathname: string, href: string): boolean {
  return href === '/' ? pathname === '/' : pathname.startsWith(href)
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()

  return (
    <Layout className="app-shell">
      <Header className="app-header">
        <Link href="/" className="app-brand">
          Quant Harness
        </Link>
        <nav className="app-nav" aria-label="Primary">
          {navItems.map((item) => (
            <Link
              href={item.href}
              key={item.href}
              className={`app-nav-link${isActivePath(pathname, item.href) ? ' app-nav-link-active' : ''}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </Header>
      <Content className="app-content">{children}</Content>
    </Layout>
  )
}

type PageIntroProps = {
  title: string
  description: ReactNode
  eyebrow?: string
  actions?: ReactNode
  children?: ReactNode
}

export function PageIntro({ title, description, eyebrow, actions, children }: PageIntroProps) {
  return (
    <section className="page-intro">
      <div className="page-intro-main">
        {eyebrow ? <Text className="page-eyebrow">{eyebrow}</Text> : null}
        <Title level={2} className="page-title">{title}</Title>
        <div className="page-description">{description}</div>
        {children ? <div className="page-intro-extra">{children}</div> : null}
      </div>
      {actions ? <div className="page-intro-actions">{actions}</div> : null}
    </section>
  )
}

type MetricCardProps = {
  title: string
  value: string | number
  suffix?: ReactNode
  precision?: number
  extra?: ReactNode
}

export function MetricCard({ title, value, suffix, precision, extra }: MetricCardProps) {
  return (
    <Card className="metric-card">
      <Statistic title={title} value={value} suffix={suffix} precision={precision} />
      {extra ? (
        <Space className="metric-extra" size={4}>
          {extra}
        </Space>
      ) : null}
    </Card>
  )
}

import 'antd/dist/reset.css'
import './globals.css'
import { SITE_NAME, SITE_TAGLINE } from './branding'

export const metadata = {
  title: `${SITE_NAME} - ${SITE_TAGLINE}`,
  description: '面向 A 股题材、赛道和短线共振的 AI 研究工作台',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        {children}
      </body>
    </html>
  )
}

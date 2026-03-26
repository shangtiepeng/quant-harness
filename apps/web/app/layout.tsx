import 'antd/dist/reset.css'
import './globals.css'

export const metadata = {
  title: 'Quant Harness',
  description: 'A-share tactical research dashboard',
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

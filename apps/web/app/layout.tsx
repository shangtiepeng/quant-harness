import 'antd/dist/reset.css'

export const metadata = {
  title: 'Quant Harness',
  description: 'A-share tactical research dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0, background: '#f5f5f5' }}>
        <style>{`
          .selected-signal-row > td {
            background: #e6f4ff !important;
          }
        `}</style>
        {children}
      </body>
    </html>
  )
}

export const metadata = {
  title: 'Quant Harness',
  description: 'A-share tactical research dashboard',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: '#fafafa' }}>{children}</body>
    </html>
  )
}

'use client'

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

type ChartRow = Record<string, unknown>

export default function ChartsClient({ data }: { data: ChartRow[] }) {
  return (
    <div style={{ width: '100%', height: 420 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="strategy" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="avg_return_1d" fill="#1677ff" name="1日均值" />
          <Bar dataKey="avg_return_3d" fill="#52c41a" name="3日均值" />
          <Bar dataKey="avg_return_5d" fill="#fa8c16" name="5日均值" />
          <Bar dataKey="win_rate_1d" fill="#722ed1" name="1日胜率" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

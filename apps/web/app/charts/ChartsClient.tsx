'use client'

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function ChartsClient({ data }: { data: any[] }) {
  return (
    <div style={{ width: '100%', height: 420 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="strategy" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="avg_return_1d" fill="#1677ff" name="Avg 1D" />
          <Bar dataKey="avg_return_3d" fill="#52c41a" name="Avg 3D" />
          <Bar dataKey="avg_return_5d" fill="#fa8c16" name="Avg 5D" />
          <Bar dataKey="win_rate_1d" fill="#722ed1" name="Win Rate 1D" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

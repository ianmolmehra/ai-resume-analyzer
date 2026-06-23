import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = {
  'Programming': '#6366f1',
  'Database': '#3b82f6',
  'Data Analytics': '#f59e0b',
  'AI/ML': '#22c55e',
  'Cloud': '#06b6d4',
  'DevOps': '#f97316',
  'Framework': '#a855f7',
  'Other': '#64748b',
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="glass-card p-3 text-sm border border-white/20">
        <p className="text-white font-semibold">{payload[0].payload.name}</p>
        <p className="text-slate-400">{payload[0].value} skills</p>
      </div>
    )
  }
  return null
}

export default function SkillCategoryChart({ skills }) {
  const categoryCounts = skills.reduce((acc, s) => {
    acc[s.category] = (acc[s.category] || 0) + 1
    return acc
  }, {})

  const data = Object.entries(categoryCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)

  if (data.length === 0) return null

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="name"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          interval={0}
          angle={-30}
          textAnchor="end"
          height={50}
        />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => (
            <Cell key={i} fill={COLORS[entry.name] || '#6366f1'} fillOpacity={0.8} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

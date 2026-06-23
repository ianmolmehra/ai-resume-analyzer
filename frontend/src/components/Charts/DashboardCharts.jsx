import React from 'react'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, LineChart, Line
} from 'recharts'

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#3b82f6', '#a855f7', '#06b6d4', '#f97316']

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="glass-card p-3 text-sm border border-white/20">
        {label && <p className="text-slate-400 mb-1">{label}</p>}
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }} className="font-semibold">
            {p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function TopSkillsChart({ data }) {
  const chartData = data?.slice(0, 10).map(s => ({ name: s.name, count: s.count })) || []
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 60, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
        <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} width={60} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} fillOpacity={0.85} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function SkillDistPieChart({ data }) {
  const chartData = Object.entries(data || {}).map(([name, value]) => ({ name, value }))
  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={3}
          dataKey="value"
        >
          {chartData.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.85} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }}
        />
        <Legend formatter={(v) => <span className="text-slate-300 text-xs">{v}</span>} />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function MatchDistChart({ data }) {
  const chartData = Object.entries(data || {}).map(([range, count]) => ({ range, count }))
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="range" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" fill="#22c55e" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function EduPieChart({ data }) {
  const chartData = Object.entries(data || {}).map(([name, value]) => ({ name, value }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={chartData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`} labelLine={false}>
          {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.85} />)}
        </Pie>
        <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }} />
      </PieChart>
    </ResponsiveContainer>
  )
}

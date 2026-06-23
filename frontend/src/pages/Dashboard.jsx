import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FileText, Users, Target, TrendingUp, BarChart3,
  Trophy, RefreshCw, ArrowRight
} from 'lucide-react'
import { analyticsAPI } from '../services/api'
import { TopSkillsChart, SkillDistPieChart, MatchDistChart, EduPieChart } from '../components/Charts/DashboardCharts'

function StatCard({ icon: Icon, label, value, sub, color = 'text-brand-400', bg = 'bg-brand-500/20' }) {
  return (
    <div className="glass-card p-6 flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl ${bg} flex items-center justify-center flex-shrink-0`}>
        <Icon size={22} className={color} />
      </div>
      <div>
        <p className="text-slate-400 text-sm">{label}</p>
        <p className="text-2xl font-bold text-white mt-0.5">{value}</p>
        {sub && <p className="text-slate-500 text-xs mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

function LoadingBlock({ rows = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-8 bg-white/5 rounded-xl animate-pulse" />
      ))}
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    analyticsAPI.dashboard()
      .then(setData)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const s = data?.summary || {}

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Platform-wide resume and matching insights</p>
        </div>
        <button onClick={load} className="btn-secondary py-2" disabled={loading}>
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText}  label="Total Resumes"     value={loading ? '—' : s.total_resumes ?? 0}     sub="Uploaded"       color="text-blue-400"    bg="bg-blue-500/20" />
        <StatCard icon={Users}     label="Candidates"        value={loading ? '—' : s.total_candidates ?? 0}  sub="Registered"     color="text-purple-400"  bg="bg-purple-500/20" />
        <StatCard icon={Target}    label="Match Reports"     value={loading ? '—' : s.total_matches ?? 0}     sub="Generated"      color="text-emerald-400" bg="bg-emerald-500/20" />
        <StatCard icon={TrendingUp}label="Avg Match Score"   value={loading ? '—' : `${s.avg_match_score ?? 0}%`} sub="Across all"  color="text-amber-400"   bg="bg-amber-500/20" />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <BarChart3 size={16} className="text-brand-400" />
            Top Skills in Demand
          </h3>
          {loading ? <LoadingBlock /> : <TopSkillsChart data={data?.top_skills} />}
        </div>
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <BarChart3 size={16} className="text-brand-400" />
            Skill Category Distribution
          </h3>
          {loading ? <LoadingBlock rows={4} /> : <SkillDistPieChart data={data?.skill_distribution} />}
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white">Match Score Distribution</h3>
          {loading ? <LoadingBlock rows={2} /> : <MatchDistChart data={data?.match_score_distribution} />}
        </div>
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white">Education Breakdown</h3>
          {loading ? <LoadingBlock rows={3} /> : <EduPieChart data={data?.education_breakdown} />}
        </div>
      </div>

      {/* Leaderboard + Recent */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leaderboard */}
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <Trophy size={16} className="text-amber-400" />
            Top Candidates
          </h3>
          {loading ? <LoadingBlock /> : (
            <div className="space-y-2">
              {(data?.leaderboard || []).slice(0, 8).map((c) => (
                <Link
                  key={c.id}
                  to={`/analysis/${c.id}`}
                  className="flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors group"
                >
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    c.rank === 1 ? 'bg-amber-500/30 text-amber-400' :
                    c.rank === 2 ? 'bg-slate-400/30 text-slate-300' :
                    c.rank === 3 ? 'bg-orange-500/30 text-orange-400' : 'bg-white/10 text-slate-400'
                  }`}>
                    {c.rank}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{c.name}</p>
                    <p className="text-slate-400 text-xs truncate">{c.email}</p>
                  </div>
                  <span className="text-emerald-400 font-bold text-sm">{c.employability_score?.toFixed(0)}%</span>
                  <ArrowRight size={14} className="text-slate-600 group-hover:text-brand-400 transition-colors" />
                </Link>
              ))}
              {!data?.leaderboard?.length && (
                <p className="text-slate-400 text-sm text-center py-4">No candidates yet. Upload a resume!</p>
              )}
            </div>
          )}
        </div>

        {/* Recent uploads */}
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <FileText size={16} className="text-blue-400" />
            Recent Uploads
          </h3>
          {loading ? <LoadingBlock /> : (
            <div className="space-y-2">
              {(data?.recent_uploads || []).map((r) => (
                <Link
                  key={r.id}
                  to={`/analysis/${r.id}`}
                  className="flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-colors group"
                >
                  <div className="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <FileText size={14} className="text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{r.name}</p>
                    <p className="text-slate-400 text-xs truncate">{r.email}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-brand-400 font-bold text-sm">{r.ats_score?.toFixed(0)}%</p>
                    <p className="text-slate-500 text-xs">ATS</p>
                  </div>
                  <ArrowRight size={14} className="text-slate-600 group-hover:text-brand-400 transition-colors" />
                </Link>
              ))}
              {!data?.recent_uploads?.length && (
                <p className="text-slate-400 text-sm text-center py-4">No uploads yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

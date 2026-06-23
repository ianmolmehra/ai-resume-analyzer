import React from 'react'
import { Brain, FileCheck, Code2, TrendingUp } from 'lucide-react'

function ScoreMeter({ score, label, icon: Icon, color }) {
  const getColor = (s) => {
    if (s >= 75) return { bar: '#22c55e', text: 'text-emerald-400', bg: 'bg-emerald-500/20' }
    if (s >= 50) return { bar: '#f59e0b', text: 'text-amber-400', bg: 'bg-amber-500/20' }
    return { bar: '#ef4444', text: 'text-red-400', bg: 'bg-red-500/20' }
  }
  const c = getColor(score)

  return (
    <div className="glass-card p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <p className={`text-3xl font-bold mt-1 ${c.text}`}>{score.toFixed(0)}</p>
          <p className="text-slate-500 text-xs">/ 100</p>
        </div>
        <div className={`w-10 h-10 rounded-xl ${c.bg} flex items-center justify-center`}>
          <Icon size={20} className={c.text} />
        </div>
      </div>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${score}%`, background: c.bar }}
        />
      </div>
      <p className={`text-xs font-semibold ${c.text}`}>
        {score >= 75 ? '⭐ Excellent' : score >= 50 ? '✦ Good' : '⚠ Needs Work'}
      </p>
    </div>
  )
}

export default function ScoreCard({ scorecard }) {
  if (!scorecard) return null
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <ScoreMeter score={scorecard.ats_score ?? 0} label="ATS Score" icon={FileCheck} />
      <ScoreMeter score={scorecard.resume_quality_score ?? 0} label="Resume Quality" icon={Brain} />
      <ScoreMeter score={scorecard.technical_skill_score ?? 0} label="Technical Skills" icon={Code2} />
      <ScoreMeter score={scorecard.employability_score ?? 0} label="Employability" icon={TrendingUp} />
    </div>
  )
}

import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronRight, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

const PRIORITY_STYLES = {
  High:   'bg-red-500/20 text-red-400 border-red-500/30',
  Medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Low:    'bg-slate-500/20 text-slate-400 border-slate-500/30',
}

const LEVEL_STYLES = {
  Beginner:     'bg-emerald-500/20 text-emerald-400',
  Intermediate: 'bg-blue-500/20 text-blue-400',
  Advanced:     'bg-purple-500/20 text-purple-400',
}

function GapItem({ item }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center gap-3 text-left hover:bg-white/5 transition-colors"
      >
        <AlertTriangle size={16} className="text-amber-400 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-white">{item.skill}</span>
            <span className={clsx('tag text-xs border', PRIORITY_STYLES[item.priority])}>
              {item.priority} Priority
            </span>
            <span className="text-xs text-slate-400">{item.category}</span>
          </div>
        </div>
        {expanded ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
      </button>

      {expanded && item.learning_path?.length > 0 && (
        <div className="border-t border-white/10 p-4 space-y-3">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-3">
            <BookOpen size={14} />
            <span>Recommended Learning Path</span>
          </div>
          {item.learning_path.map((step, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-brand-400 text-xs font-bold">{i + 1}</span>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-white text-sm font-medium">{step.title}</span>
                  <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium', LEVEL_STYLES[step.level])}>
                    {step.level}
                  </span>
                </div>
                {step.platform && (
                  <p className="text-slate-400 text-xs mt-0.5">{step.platform}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function SkillGapPanel({ gaps }) {
  if (!gaps || gaps.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400">
        <p>No skill gaps found! Great match.</p>
      </div>
    )
  }
  return (
    <div className="space-y-3">
      {gaps.map((item, i) => (
        <GapItem key={i} item={item} />
      ))}
    </div>
  )
}

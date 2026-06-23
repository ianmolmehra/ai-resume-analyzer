import React from 'react'
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'

function getColor(score) {
  if (score >= 75) return { primary: '#22c55e', trail: '#22c55e33', label: 'Excellent Match', labelColor: 'text-emerald-400' }
  if (score >= 50) return { primary: '#f59e0b', trail: '#f59e0b33', label: 'Good Match', labelColor: 'text-amber-400' }
  if (score >= 25) return { primary: '#f97316', trail: '#f9731633', label: 'Moderate Match', labelColor: 'text-orange-400' }
  return { primary: '#ef4444', trail: '#ef444433', label: 'Low Match', labelColor: 'text-red-400' }
}

export default function MatchGauge({ score }) {
  const c = getColor(score)
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="w-48 h-48">
        <CircularProgressbar
          value={score}
          text={`${score.toFixed(0)}%`}
          styles={buildStyles({
            textColor: '#f1f5f9',
            pathColor: c.primary,
            trailColor: c.trail,
            textSize: '18px',
            pathTransitionDuration: 1.0,
          })}
        />
      </div>
      <div className="text-center">
        <span className={`text-lg font-bold ${c.labelColor}`}>{c.label}</span>
        <p className="text-slate-400 text-sm mt-1">Overall Match Score</p>
      </div>
    </div>
  )
}

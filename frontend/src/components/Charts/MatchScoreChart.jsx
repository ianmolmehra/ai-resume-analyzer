import React from 'react'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

export default function MatchScoreChart({ scores }) {
  const data = [
    { subject: 'Skills', score: scores.skill_match_score },
    { subject: 'Experience', score: scores.experience_match_score },
    { subject: 'Education', score: scores.education_match_score },
    { subject: 'Projects', score: scores.project_relevance_score },
    { subject: 'Keywords', score: scores.keyword_match_score },
    { subject: 'ATS', score: scores.ats_compatibility },
  ]

  return (
    <ResponsiveContainer width="100%" height={250}>
      <RadarChart data={data}>
        <PolarGrid stroke="rgba(255,255,255,0.1)" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
        <Radar
          name="Match"
          dataKey="score"
          stroke="#6366f1"
          fill="#6366f1"
          fillOpacity={0.2}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{
            background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px', color: '#f1f5f9',
          }}
          formatter={(value) => [`${value.toFixed(1)}%`, 'Score']}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}

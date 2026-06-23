import React, { useState } from 'react'
import clsx from 'clsx'

const CATEGORY_STYLES = {
  'Programming':    'tag-purple',
  'Database':       'tag-blue',
  'Data Analytics': 'tag-amber',
  'AI/ML':          'tag-green',
  'Cloud':          'tag-blue',
  'DevOps':         'tag-amber',
  'Framework':      'tag-purple',
  'Soft Skill':     'tag-green',
  'Other':          'tag-blue',
}

const ALL_CATEGORIES = ['All', 'Programming', 'Database', 'Data Analytics', 'AI/ML', 'Cloud', 'DevOps', 'Framework']

export default function SkillBadges({ skills }) {
  const [filter, setFilter] = useState('All')

  const filtered = filter === 'All' ? skills : skills.filter(s => s.category === filter)
  const categories = ['All', ...new Set(skills.map(s => s.category))]

  return (
    <div className="space-y-4">
      {/* Filter pills */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={clsx(
              'px-3 py-1 rounded-full text-xs font-medium transition-all duration-200',
              filter === cat
                ? 'bg-brand-500 text-white'
                : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
            )}
          >
            {cat}
            {cat !== 'All' && (
              <span className="ml-1 opacity-60">
                ({skills.filter(s => s.category === cat).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Skills grid */}
      <div className="flex flex-wrap gap-2">
        {filtered.map((skill) => (
          <div
            key={skill.name}
            className={clsx('tag relative group cursor-default', CATEGORY_STYLES[skill.category] || 'tag-blue')}
            title={`${skill.proficiency_level} · ${(skill.confidence_score * 100).toFixed(0)}% confidence`}
          >
            {skill.name}
            <span className="ml-1.5 opacity-60 text-[10px]">
              {(skill.confidence_score * 100).toFixed(0)}%
            </span>
            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-dark-700 border border-white/20 rounded-lg text-xs text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
              {skill.proficiency_level} · {skill.category}
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <p className="text-slate-400 text-sm">No skills in this category</p>
        )}
      </div>

      <p className="text-xs text-slate-500">{filtered.length} skills shown · hover for details</p>
    </div>
  )
}

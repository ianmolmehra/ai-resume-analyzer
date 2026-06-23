import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Target, FileText, Building2, CheckCircle, XCircle, Download,
  Lightbulb, TrendingUp, ArrowLeft, Loader2, ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import { matchAPI } from '../services/api'
import MatchGauge from '../components/Matching/MatchGauge'
import SkillGapPanel from '../components/Matching/SkillGapPanel'
import ScoreCard from '../components/Analysis/ScoreCard'
import MatchScoreChart from '../components/Charts/MatchScoreChart'

function ScoreBar({ label, score }) {
  const color = score >= 75 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="font-bold" style={{ color }}>{score.toFixed(0)}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${score}%`, background: color }} />
      </div>
    </div>
  )
}

export default function Matching() {
  const { resumeId } = useParams()
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [company, setCompany] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  const TABS = ['overview', 'skills', 'gap analysis', 'recommendations']

  const handleAnalyze = async () => {
    if (!jdText.trim() && !jdFile) {
      toast.error('Please enter a job description or upload a JD file')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const res = await matchAPI.analyze({
        resumeId: parseInt(resumeId),
        jdText: jdText || undefined,
        jdFile: jdFile || undefined,
        jobTitle: jobTitle || undefined,
        company: company || undefined,
      })
      setResult(res)
      setActiveTab('overview')
      toast.success(`Match complete! Overall score: ${res.scores?.overall_match_score?.toFixed(0)}%`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to={`/analysis/${resumeId}`} className="btn-secondary py-2 px-3">
          <ArrowLeft size={16} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white">Job Matching</h1>
          <p className="text-slate-400 text-sm">Resume #{resumeId} — Paste or upload a job description</p>
        </div>
      </div>

      {/* JD Input */}
      {!result && (
        <div className="glass-card p-6 space-y-5">
          <h2 className="section-header">
            <Target size={18} className="text-brand-400" />
            Job Description
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-slate-400 mb-1 block">Job Title <span className="text-slate-500">(optional)</span></label>
              <input
                type="text"
                value={jobTitle}
                onChange={e => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Data Engineer"
                className="input-field"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-1 block">Company <span className="text-slate-500">(optional)</span></label>
              <input
                type="text"
                value={company}
                onChange={e => setCompany(e.target.value)}
                placeholder="e.g. Google"
                className="input-field"
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-1 block">Paste Job Description</label>
            <textarea
              value={jdText}
              onChange={e => setJdText(e.target.value)}
              placeholder="Paste the full job description here — requirements, responsibilities, qualifications..."
              rows={10}
              className="input-field resize-none font-mono text-sm leading-relaxed"
            />
            <p className="text-slate-500 text-xs mt-1">{jdText.length} characters · paste the complete JD for best results</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex-1 border-t border-white/10" />
            <span className="text-slate-500 text-xs">or upload JD file</span>
            <div className="flex-1 border-t border-white/10" />
          </div>

          <div className="flex items-center gap-3">
            <label className="btn-secondary cursor-pointer">
              <FileText size={16} />
              {jdFile ? jdFile.name : 'Upload PDF/DOCX'}
              <input
                type="file"
                accept=".pdf,.docx"
                className="hidden"
                onChange={e => setJdFile(e.target.files[0])}
              />
            </label>
            {jdFile && (
              <button onClick={() => setJdFile(null)} className="text-red-400 hover:text-red-300 text-sm">
                Remove
              </button>
            )}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || (!jdText.trim() && !jdFile)}
            className="btn-primary w-full justify-center py-4"
          >
            {loading ? (
              <><Loader2 size={20} className="animate-spin" /> Analyzing Match...</>
            ) : (
              <><Target size={20} /> Analyze Match<ChevronRight size={16} /></>
            )}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Results header */}
          <div className="glass-card p-5 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-white">
                {result.job?.title || 'Job Match'} {result.job?.company && `— ${result.job.company}`}
              </h2>
              <p className="text-slate-400 text-sm mt-1">
                {result.matched_skills?.length} matched skills · {result.missing_skills?.length} missing skills
              </p>
            </div>
            <div className="flex gap-3">
              <button onClick={() => { setResult(null); setJdText(''); setJdFile(null) }} className="btn-secondary py-2">
                New Analysis
              </button>
              <button
                onClick={() => matchAPI.downloadReport(result.match_report_id)}
                className="btn-primary py-2"
              >
                <Download size={16} />
                PDF Report
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 glass-card p-1 w-fit">
            {TABS.map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 capitalize ${
                  activeTab === tab
                    ? 'bg-brand-500 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-white/10'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Overview tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gauge */}
                <div className="glass-card p-6 flex flex-col items-center justify-center">
                  <MatchGauge score={result.scores?.overall_match_score ?? 0} />
                </div>
                {/* Score breakdown */}
                <div className="glass-card p-6 space-y-4">
                  <h3 className="font-semibold text-white">Score Breakdown</h3>
                  <ScoreBar label="Skill Match"        score={result.scores?.skill_match_score ?? 0} />
                  <ScoreBar label="Experience Match"   score={result.scores?.experience_match_score ?? 0} />
                  <ScoreBar label="Education Match"    score={result.scores?.education_match_score ?? 0} />
                  <ScoreBar label="Project Relevance"  score={result.scores?.project_relevance_score ?? 0} />
                  <ScoreBar label="Keyword Match"      score={result.scores?.keyword_match_score ?? 0} />
                  <ScoreBar label="ATS Compatibility"  score={result.scores?.ats_compatibility ?? 0} />
                </div>
              </div>
              {/* Radar */}
              <div className="glass-card p-6">
                <h3 className="font-semibold text-white mb-4">Match Profile Radar</h3>
                <MatchScoreChart scores={result.scores ?? {}} />
              </div>
              {/* Scorecard */}
              {result.scorecard && (
                <div className="glass-card p-6 space-y-4">
                  <h3 className="font-semibold text-white">Candidate Scorecard</h3>
                  <ScoreCard scorecard={result.scorecard} />
                </div>
              )}
            </div>
          )}

          {/* Skills tab */}
          {activeTab === 'skills' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Matched */}
              <div className="glass-card p-6 space-y-3">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <CheckCircle size={18} className="text-emerald-400" />
                  Matched Skills
                  <span className="ml-auto text-emerald-400 font-bold">{result.matched_skills?.length}</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.matched_skills?.map(skill => (
                    <span key={skill} className="flex items-center gap-1 tag tag-green">
                      <CheckCircle size={12} /> {skill}
                    </span>
                  ))}
                </div>
              </div>
              {/* Missing */}
              <div className="glass-card p-6 space-y-3">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <XCircle size={18} className="text-red-400" />
                  Missing Skills
                  <span className="ml-auto text-red-400 font-bold">{result.missing_skills?.length}</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.missing_skills?.map(skill => (
                    <span key={skill} className="flex items-center gap-1 tag tag-red">
                      <XCircle size={12} /> {skill}
                    </span>
                  ))}
                </div>
              </div>
              {/* Keyword optimization */}
              {result.keyword_optimization?.length > 0 && (
                <div className="lg:col-span-2 glass-card p-6 space-y-3">
                  <h3 className="font-semibold text-white">ATS Keywords to Add</h3>
                  <p className="text-slate-400 text-sm">Add these keywords to your resume to improve ATS compatibility:</p>
                  <div className="flex flex-wrap gap-2">
                    {result.keyword_optimization.map(kw => (
                      <span key={kw} className="tag tag-amber">{kw}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Gap Analysis tab */}
          {activeTab === 'gap analysis' && (
            <div className="space-y-4">
              <div className="glass-card p-4 bg-amber-500/5 border-amber-500/20">
                <p className="text-amber-400 text-sm">
                  <strong>{result.skill_gap_analysis?.length}</strong> skill gaps identified.
                  Click any skill below to see a recommended learning path.
                </p>
              </div>
              <SkillGapPanel gaps={result.skill_gap_analysis} />
            </div>
          )}

          {/* Recommendations tab */}
          {activeTab === 'recommendations' && (
            <div className="space-y-4">
              <div className="glass-card p-6 space-y-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <Lightbulb size={18} className="text-amber-400" />
                  Recommendations
                </h3>
                {result.recommendations?.map((rec, i) => (
                  <div key={i} className="flex gap-3 p-3 bg-white/5 rounded-xl">
                    <span className="text-brand-400 font-bold text-sm flex-shrink-0">{String(i+1).padStart(2,'0')}</span>
                    <p className="text-slate-300 text-sm">{rec}</p>
                  </div>
                ))}
              </div>
              <div className="glass-card p-6 space-y-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <TrendingUp size={18} className="text-emerald-400" />
                  Resume Improvement Suggestions
                </h3>
                {result.improvement_suggestions?.map((sug, i) => (
                  <div key={i} className="flex gap-3 p-3 bg-white/5 rounded-xl">
                    <CheckCircle size={16} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                    <p className="text-slate-300 text-sm">{sug}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

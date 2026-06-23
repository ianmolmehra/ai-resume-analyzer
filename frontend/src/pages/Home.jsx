import React, { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Zap, Target, BarChart3, FileText, CheckCircle, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import DropZone from '../components/Upload/DropZone'
import { resumeAPI } from '../services/api'

const FEATURES = [
  { icon: FileText,  color: 'text-blue-400',   bg: 'bg-blue-500/20',   title: 'Smart Parsing',   desc: 'Extracts name, contact, education, skills, projects & experience' },
  { icon: Brain,     color: 'text-purple-400',  bg: 'bg-purple-500/20', title: 'Skill Detection', desc: '100+ skills across Programming, AI/ML, Cloud, DevOps & more' },
  { icon: Target,    color: 'text-emerald-400', bg: 'bg-emerald-500/20',title: 'Job Matching',    desc: 'Match score with skill gap analysis and learning paths' },
  { icon: BarChart3, color: 'text-amber-400',   bg: 'bg-amber-500/20',  title: 'Analytics',      desc: 'ATS score, employability index and detailed scorecard' },
]

export default function Home() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleFileAccepted = useCallback((f) => {
    setFile(f)
  }, [])

  const handleUpload = async () => {
    if (!file) { toast.error('Please select a resume file first'); return }
    setIsLoading(true)
    try {
      const result = await resumeAPI.upload(file)
      toast.success(`Resume parsed! Found ${result.parsed_data?.skills?.length || 0} skills.`)
      navigate(`/analysis/${result.resume_id}`, { state: { uploadResult: result } })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-10">
      {/* Hero */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 glass-card px-4 py-2 text-sm text-brand-400 font-medium border-brand-500/30">
          <Zap size={14} className="animate-pulse" />
          AI-Powered Resume Intelligence
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold">
          <span className="text-gradient">Analyze Your Resume.</span>
          <br />
          <span className="text-white">Land Your Dream Job.</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          Upload your resume and get instant AI-powered analysis, skill extraction,
          job matching, and actionable improvement suggestions.
        </p>
      </div>

      {/* Upload Card */}
      <div className="glass-card p-8 space-y-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText size={20} className="text-brand-400" />
          Upload Your Resume
        </h2>
        <DropZone onFileAccepted={handleFileAccepted} isLoading={isLoading} />
        <button
          onClick={handleUpload}
          disabled={!file || isLoading}
          className="btn-primary w-full justify-center py-4 text-base"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Analyzing Resume...
            </>
          ) : (
            <>
              <Brain size={20} />
              Analyze Resume
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {FEATURES.map(({ icon: Icon, color, bg, title, desc }) => (
          <div key={title} className="glass-card-hover p-5 flex gap-4">
            <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center flex-shrink-0`}>
              <Icon size={20} className={color} />
            </div>
            <div>
              <h3 className="font-semibold text-white">{title}</h3>
              <p className="text-slate-400 text-sm mt-1">{desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Process steps */}
      <div className="glass-card p-6">
        <h2 className="section-header mb-6">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {[
            { step: '01', title: 'Upload Resume', desc: 'Drop your PDF or DOCX file' },
            { step: '02', title: 'AI Analysis',   desc: 'Skills, education & experience extracted instantly' },
            { step: '03', title: 'Job Matching',  desc: 'Paste a job description and get a detailed match report' },
          ].map(({ step, title, desc }) => (
            <div key={step} className="flex flex-col items-center text-center gap-3">
              <div className="w-12 h-12 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center">
                <span className="text-brand-400 font-bold">{step}</span>
              </div>
              <div>
                <h3 className="font-semibold text-white">{title}</h3>
                <p className="text-slate-400 text-sm mt-1">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

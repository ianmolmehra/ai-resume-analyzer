import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import {
  User, Mail, Phone, Linkedin, Github, GraduationCap, Briefcase,
  FolderGit2, Award, Code2, Target, ArrowRight, Download, RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'
import { resumeAPI } from '../services/api'
import ScoreCard from '../components/Analysis/ScoreCard'
import SkillBadges from '../components/Analysis/SkillBadges'
import SkillCategoryChart from '../components/Charts/SkillRadar'

function InfoRow({ icon: Icon, label, value }) {
  if (!value) return null
  return (
    <div className="flex items-start gap-3">
      <Icon size={16} className="text-slate-400 mt-0.5 flex-shrink-0" />
      <div>
        <span className="text-slate-400 text-xs">{label}</span>
        <p className="text-white text-sm font-medium break-all">{value}</p>
      </div>
    </div>
  )
}

function Section({ title, icon: Icon, children, isEmpty }) {
  if (isEmpty) return null
  return (
    <div className="glass-card p-6 space-y-4">
      <h3 className="section-header">
        <Icon size={18} className="text-brand-400" />
        {title}
      </h3>
      {children}
    </div>
  )
}

export default function Analysis() {
  const { resumeId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [data, setData] = useState(location.state?.uploadResult || null)
  const [loading, setLoading] = useState(!location.state?.uploadResult)

  useEffect(() => {
    if (!location.state?.uploadResult) {
      resumeAPI.get(resumeId)
        .then(setData)
        .catch(() => { toast.error('Resume not found'); navigate('/') })
        .finally(() => setLoading(false))
    }
  }, [resumeId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-slate-400">Loading analysis...</p>
        </div>
      </div>
    )
  }

  if (!data) return null

  const parsed = data.parsed_data || data
  const candidate = data.candidate || parsed
  const skills = parsed.skills || data.parsed_data?.skills || []
  const education = parsed.education || []
  const experience = parsed.experience || []
  const projects = parsed.projects || []
  const certifications = parsed.certifications || []

  const scorecard = {
    ats_score: data.ats_score ?? parsed.ats_score ?? 0,
    resume_quality_score: data.resume_quality_score ?? parsed.resume_quality_score ?? 0,
    technical_skill_score: data.technical_skill_score ?? parsed.technical_skill_score ?? 0,
    employability_score: data.employability_score ?? parsed.employability_score ?? 0,
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {candidate.full_name || 'Resume Analysis'}
          </h1>
          <p className="text-slate-400 text-sm mt-1">Resume #{resumeId} · {skills.length} skills extracted</p>
        </div>
        <Link
          to={`/matching/${resumeId}`}
          className="btn-primary"
        >
          <Target size={18} />
          Match to Job
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Scorecard */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="section-header">
          <Award size={18} className="text-brand-400" />
          Candidate Scorecard
        </h2>
        <ScoreCard scorecard={scorecard} />
      </div>

      {/* Profile + Skills row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile */}
        <div className="glass-card p-6 space-y-5">
          <h3 className="section-header">
            <User size={18} className="text-brand-400" />
            Profile
          </h3>
          <div className="space-y-4">
            <InfoRow icon={User}     label="Full Name" value={candidate.full_name} />
            <InfoRow icon={Mail}     label="Email"     value={candidate.email} />
            <InfoRow icon={Phone}    label="Phone"     value={candidate.phone} />
            <InfoRow icon={Linkedin} label="LinkedIn"  value={candidate.linkedin_url} />
            <InfoRow icon={Github}   label="GitHub"    value={candidate.github_url} />
            {parsed.total_experience_years > 0 && (
              <InfoRow icon={Briefcase} label="Experience" value={`${parsed.total_experience_years} years`} />
            )}
            {parsed.highest_education && (
              <InfoRow icon={GraduationCap} label="Highest Education" value={parsed.highest_education} />
            )}
          </div>
        </div>

        {/* Skills */}
        <div className="lg:col-span-2 glass-card p-6 space-y-4">
          <h3 className="section-header">
            <Code2 size={18} className="text-brand-400" />
            Extracted Skills
            <span className="ml-auto text-sm font-normal text-slate-400">{skills.length} found</span>
          </h3>
          {skills.length > 0 ? (
            <>
              <SkillBadges skills={skills} />
              <div className="mt-4">
                <p className="text-xs text-slate-500 mb-3">Skill Category Distribution</p>
                <SkillCategoryChart skills={skills} />
              </div>
            </>
          ) : (
            <p className="text-slate-400 text-sm">No skills detected. The resume may need better formatting.</p>
          )}
        </div>
      </div>

      {/* Education */}
      <Section title="Education" icon={GraduationCap} isEmpty={education.length === 0}>
        <div className="space-y-4">
          {education.map((edu, i) => (
            <div key={i} className="flex items-start gap-4 p-4 bg-white/5 rounded-xl">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                <GraduationCap size={18} className="text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-semibold">{edu.degree || 'Degree'}</p>
                <p className="text-slate-300 text-sm">{edu.university}</p>
                {edu.graduation_year && <p className="text-slate-400 text-xs mt-1">Class of {edu.graduation_year}</p>}
                {edu.gpa && <p className="text-slate-400 text-xs">GPA: {edu.gpa}</p>}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Experience */}
      <Section title="Work Experience" icon={Briefcase} isEmpty={experience.length === 0}>
        <div className="space-y-4">
          {experience.map((exp, i) => (
            <div key={i} className="flex gap-4 p-4 bg-white/5 rounded-xl">
              <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Briefcase size={18} className="text-purple-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-semibold">{exp.role}</p>
                {exp.company && <p className="text-brand-400 text-sm">{exp.company}</p>}
                {exp.duration && <p className="text-slate-400 text-xs mt-1">{exp.duration}</p>}
                {exp.description && (
                  <p className="text-slate-400 text-sm mt-2 line-clamp-3">{exp.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Projects */}
      <Section title="Projects" icon={FolderGit2} isEmpty={projects.length === 0}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {projects.map((proj, i) => (
            <div key={i} className="p-4 bg-white/5 rounded-xl space-y-2">
              <p className="text-white font-semibold">{proj.name}</p>
              {proj.description && <p className="text-slate-400 text-sm line-clamp-2">{proj.description}</p>}
              {proj.tech_stack?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {proj.tech_stack.map(tech => (
                    <span key={tech} className="tag tag-purple text-xs">{tech}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </Section>

      {/* Certifications */}
      <Section title="Certifications" icon={Award} isEmpty={certifications.length === 0}>
        <div className="space-y-2">
          {certifications.map((cert, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl">
              <Award size={16} className="text-amber-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium">{cert.name}</p>
                {cert.issuer && <p className="text-slate-400 text-xs">{cert.issuer}</p>}
              </div>
              {cert.year && <span className="text-slate-400 text-xs">{cert.year}</span>}
            </div>
          ))}
        </div>
      </Section>
    </div>
  )
}

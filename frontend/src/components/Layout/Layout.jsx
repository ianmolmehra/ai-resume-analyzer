import React, { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  Brain, LayoutDashboard, Upload, Target, BarChart3,
  Shield, Menu, X, Zap, Github, ExternalLink
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/',          label: 'Upload',    icon: Upload,        exact: true },
  { to: '/dashboard', label: 'Analytics', icon: BarChart3 },
  { to: '/admin',     label: 'Admin',     icon: Shield },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="flex min-h-screen bg-dark-900 bg-mesh">
      {/* Sidebar */}
      <aside className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 glass-card border-r border-white/10 rounded-none',
        'flex flex-col transition-transform duration-300',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
          <div className="w-9 h-9 bg-brand-500 rounded-xl flex items-center justify-center shadow-glow">
            <Brain size={20} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white text-sm leading-tight">AI Resume</h1>
            <p className="text-brand-400 text-xs font-medium">Analyzer</p>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="ml-auto lg:hidden text-slate-400 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-4 mb-3">Menu</p>
          {navItems.map(({ to, label, icon: Icon, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                clsx(isActive ? 'nav-link-active' : 'nav-link')
              }
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}

          {/* Dynamic links based on URL */}
          {location.pathname.startsWith('/analysis/') && (
            <>
              <div className="border-t border-white/10 my-3" />
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-4 mb-3">Current Resume</p>
              <NavLink
                to={location.pathname}
                className="nav-link-active"
              >
                <Zap size={18} />
                Analysis
              </NavLink>
              <NavLink
                to={location.pathname.replace('/analysis/', '/matching/')}
                className={({ isActive }) => clsx(isActive ? 'nav-link-active' : 'nav-link')}
              >
                <Target size={18} />
                Job Matching
              </NavLink>
            </>
          )}
          {location.pathname.startsWith('/matching/') && (
            <>
              <div className="border-t border-white/10 my-3" />
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-4 mb-3">Current Resume</p>
              <NavLink
                to={location.pathname.replace('/matching/', '/analysis/')}
                className={({ isActive }) => clsx(isActive ? 'nav-link-active' : 'nav-link')}
              >
                <Zap size={18} />
                Analysis
              </NavLink>
              <NavLink
                to={location.pathname}
                className="nav-link-active"
              >
                <Target size={18} />
                Job Matching
              </NavLink>
            </>
          )}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/10">
          <div className="glass-card p-3 text-center">
            <p className="text-xs text-slate-400">AI Resume Analyzer</p>
            <p className="text-xs text-brand-400 font-medium">v1.0.0 Production</p>
          </div>
        </div>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="sticky top-0 z-30 glass-card rounded-none border-b border-white/10 border-x-0 border-t-0 px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <Menu size={20} />
            </button>
            <div className="flex-1">
              <h2 className="font-semibold text-white">
                {location.pathname === '/' && 'Upload Resume'}
                {location.pathname === '/dashboard' && 'Analytics Dashboard'}
                {location.pathname === '/admin' && 'Admin Panel'}
                {location.pathname.startsWith('/analysis/') && 'Resume Analysis'}
                {location.pathname.startsWith('/matching/') && 'Job Matching'}
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
                <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                API Connected
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

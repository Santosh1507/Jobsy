import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, Briefcase, Send, FileText, MessageSquare, 
  TrendingUp, Users, Settings, Play, Star, Target, Zap
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Applications from './pages/Applications'
import InterviewPrep from './pages/InterviewPrep'
import ResumeBuilder from './pages/ResumeBuilder'
import VoiceInterview from './pages/VoiceInterview'
import BatchApply from './pages/BatchApply'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/jobs', label: 'Jobs', icon: Briefcase },
  { path: '/batch-apply', label: 'Batch Apply', icon: Zap },
  { path: '/applications', label: 'Applications', icon: Send },
  { path: '/interview-prep', label: 'Interview Prep', icon: Target },
  { path: '/resume-builder', label: 'Resume', icon: FileText },
  { path: '/voice-interview', label: 'Voice Practice', icon: Play },
]

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/batch-apply" element={<BatchApply />} />
            <Route path="/applications" element={<Applications />} />
            <Route path="/interview-prep" element={<InterviewPrep />} />
            <Route path="/resume-builder" element={<ResumeBuilder />} />
            <Route path="/voice-interview" element={<VoiceInterview />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

function Sidebar() {
  const location = useLocation()
  
  return (
    <aside className="sidebar">
      <div className="logo">
        <Briefcase size={24} />
        Jobsy
      </div>
      <nav className="nav">
        {navItems.map(item => (
          <Link 
            key={item.path} 
            to={item.path} 
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <item.icon size={20} />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

export default App
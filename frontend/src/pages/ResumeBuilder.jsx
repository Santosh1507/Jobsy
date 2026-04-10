import React, { useState } from 'react'
import { FileText, Download, Upload } from 'lucide-react'

export default function ResumeBuilder() {
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    summary: '',
    experience: [],
    education: [],
    skills: []
  })
  const [generated, setGenerated] = useState(false)

  const generateResume = async () => {
    try {
      const response = await fetch('/api/v1/tools/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo-user',
          user_data: userData,
          keywords: userData.skills
        })
      })
      const data = await response.json()
      if (data.success) {
        setGenerated(true)
      }
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div>
      <div className="header">
        <h1>Resume Builder</h1>
        <p>Generate ATS-optimized resumes tailored to specific jobs.</p>
      </div>

      <div className="grid-2">
        <div className="section">
          <h2><FileText size={20} /> Basic Information</h2>
          <div className="form-group">
            <label>Full Name</label>
            <input className="input" placeholder="John Doe" value={userData.name} onChange={e => setUserData({...userData, name: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input className="input" placeholder="john@example.com" value={userData.email} onChange={e => setUserData({...userData, email: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Location</label>
            <input className="input" placeholder="San Francisco, CA" value={userData.location} onChange={e => setUserData({...userData, location: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Skills (comma separated)</label>
            <input className="input" placeholder="Python, React, AWS, SQL" value={userData.skills.join(', ')} onChange={e => setUserData({...userData, skills: e.target.value.split(',').map(s => s.trim())})} />
          </div>
          <div className="form-group">
            <label>Professional Summary</label>
            <textarea className="input" rows={3} placeholder="Brief summary of your experience..." value={userData.summary} onChange={e => setUserData({...userData, summary: e.target.value})} />
          </div>
          <button className="btn btn-primary" onClick={generateResume}><Download size={18} /> Generate PDF Resume</button>
        </div>

        <div className="section">
          <h2>Features</h2>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h4>ATS-Optimized Format</h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Optimized for Applicant Tracking Systems with proper formatting and keyword matching.</p>
          </div>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h4>Tailored Resumes</h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Generate job-specific resumes by pasting job descriptions.</p>
          </div>
          <div className="card">
            <h4>Multiple Formats</h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Export to PDF, DOCX, and plain text formats.</p>
          </div>
        </div>
      </div>

      {generated && (
        <div className="section" style={{ background: 'rgba(16, 185, 129, 0.1)', borderColor: 'var(--success)' }}>
          <h2 style={{ color: 'var(--success)' }}>Resume Generated Successfully!</h2>
          <p>Your ATS-optimized PDF resume has been created. Download it from your dashboard.</p>
        </div>
      )}
    </div>
  )
}
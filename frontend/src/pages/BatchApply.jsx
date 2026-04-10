import React, { useState } from 'react'
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function BatchApply() {
  const [jobs, setJobs] = useState([
    { id: '1', title: 'Senior Software Engineer', company: 'Google', url: '', selected: false },
    { id: '2', title: 'Staff Backend Engineer', company: 'Stripe', url: '', selected: false },
    { id: '3', title: 'ML Engineer', company: 'OpenAI', url: '', selected: false },
    { id: '4', title: 'Senior DevOps', company: 'Datadog', url: '', selected: false },
  ])
  
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    phone: '',
    resume_file: null
  })
  const [applying, setApplying] = useState(false)
  const [results, setResults] = useState(null)

  const toggleJob = (id) => {
    setJobs(jobs.map(j => j.id === id ? { ...j, selected: !j.selected } : j))
  }

  const addCustomJob = () => {
    setJobs([...jobs, { id: Date.now().toString(), title: '', company: '', url: '', selected: true }])
  }

  const updateJob = (id, field, value) => {
    setJobs(jobs.map(j => j.id === id ? { ...j, [field]: value } : j))
  }

  const runBatchApply = async () => {
    const selectedJobs = jobs.filter(j => j.selected)
    if (selectedJobs.length === 0) return
    
    setApplying(true)
    
    try {
      const response = await fetch('/api/v1/tools/batch-apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo-user',
          jobs: selectedJobs,
          user_data: userData,
          cover_letter_template: 'standard'
        })
      })
      const data = await response.json()
      setResults(data)
    } catch (e) {
      console.error(e)
      setResults({ error: e.message })
    }
    
    setApplying(false)
  }

  const selectedCount = jobs.filter(j => j.selected).length

  return (
    <div>
      <div className="header">
        <h1>Batch Apply</h1>
        <p>Auto-apply to multiple jobs with tailored cover letters.</p>
      </div>

      <div className="grid-2">
        <div className="section">
          <h2>Select Jobs</h2>
          
          <div style={{ marginBottom: '1rem' }}>
            {jobs.map(job => (
              <div key={job.id} style={{ 
                display: 'flex', 
                gap: '0.5rem', 
                marginBottom: '0.5rem',
                alignItems: 'center'
              }}>
                <input 
                  type="checkbox" 
                  checked={job.selected} 
                  onChange={() => toggleJob(job.id)}
                />
                <input 
                  className="input" 
                  style={{ marginBottom: 0, flex: 1 }}
                  placeholder="Job title"
                  value={job.title}
                  onChange={(e) => updateJob(job.id, 'title', e.target.value)}
                />
                <input 
                  className="input" 
                  style={{ marginBottom: 0, flex: 1 }}
                  placeholder="Company"
                  value={job.company}
                  onChange={(e) => updateJob(job.id, 'company', e.target.value)}
                />
              </div>
            ))}
          </div>
          
          <button className="btn btn-secondary" onClick={addCustomJob}>+ Add Job</button>
          
          <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--surface-light)', borderRadius: '0.5rem' }}>
            <strong>{selectedCount}</strong> jobs selected
          </div>
        </div>

        <div className="section">
          <h2>Your Info</h2>
          <div className="form-group">
            <label>Full Name</label>
            <input className="input" placeholder="John Doe" value={userData.name} onChange={e => setUserData({...userData, name: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input className="input" placeholder="john@example.com" value={userData.email} onChange={e => setUserData({...userData, email: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input className="input" placeholder="+1234567890" value={userData.phone} onChange={e => setUserData({...userData, phone: e.target.value})} />
          </div>
          
          <button 
            className="btn btn-primary" 
            onClick={runBatchApply}
            disabled={applying || selectedCount === 0}
          >
            {applying ? 'Applying...' : <><Play size={18} /> Apply to {selectedCount} Jobs</>}
          </button>
        </div>
      </div>

      {results && (
        <div className="section">
          <h2>Results</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total</h3>
              <div className="value">{results.total || 0}</div>
            </div>
            <div className="stat-card">
              <h3>Successful</h3>
              <div className="value success">{results.successful || 0}</div>
            </div>
            <div className="stat-card">
              <h3>Failed</h3>
              <div className="value error">{results.failed || 0}</div>
            </div>
          </div>
          
          {results.results?.map((r, i) => (
            <div key={i} className="card" style={{ marginBottom: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong>{r.job}</strong> at {r.company}
                </div>
                {r.result?.success ? 
                  <span className="badge success"><CheckCircle size={14} /> Applied</span> :
                  <span className="badge error"><XCircle size={14} /> Failed</span>
                }
              </div>
              {r.result?.message && !r.result.success && (
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  {r.result.message}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
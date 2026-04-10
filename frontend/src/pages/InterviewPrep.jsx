import React, { useState } from 'react'
import { Target, BookOpen, MessageSquare, Star } from 'lucide-react'

export default function InterviewPrep() {
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [generatedQuestions, setGeneratedQuestions] = useState(null)

  const generateQuestions = async () => {
    if (!company || !role) return
    
    try {
      const response = await fetch('/api/v1/tools/interview-prep', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, role, question_type: 'mixed' })
      })
      const data = await response.json()
      setGeneratedQuestions(data)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div>
      <div className="header">
        <h1>Interview Prep</h1>
        <p>Prepare for interviews with company-specific questions and STAR stories.</p>
      </div>

      <div className="grid-2">
        <div className="section">
          <h2>Generate Questions</h2>
          <div className="form-group">
            <label>Company</label>
            <input className="input" placeholder="e.g., Google, Meta, Amazon" value={company} onChange={e => setCompany(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Role</label>
            <input className="input" placeholder="e.g., Senior Engineer" value={role} onChange={e => setRole(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={generateQuestions}><Target size={18} /> Generate Questions</button>
        </div>

        <div className="section">
          <h2>Quick Links</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <a href="#" className="nav-item">
              <BookOpen size={20} /> STAR Story Bank
            </a>
            <a href="#" className="nav-item">
              <MessageSquare size={20} /> Company Patterns
            </a>
            <a href="#" className="nav-item">
              <Star size={20} /> Practice Sessions
            </a>
          </div>
        </div>
      </div>

      {generatedQuestions && (
        <div className="section">
          <h2>Questions for {company}</h2>
          {generatedQuestions.questions.map((q, i) => (
            <div key={i} className="card" style={{ marginBottom: '1rem' }}>
              <h4>Q{i + 1}: {q}</h4>
            </div>
          ))}
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: '0.5rem' }}>
            <strong>Rounds:</strong> {generatedQuestions.rounds} | <strong>Types:</strong> {generatedQuestions.round_types?.join(', ')}
          </div>
        </div>
      )}
    </div>
  )
}
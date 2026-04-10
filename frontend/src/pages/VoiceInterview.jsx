import React, { useState } from 'react'
import { Play, CheckCircle, MessageSquare, Clock } from 'lucide-react'

export default function VoiceInterview() {
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [interviewType, setInterviewType] = useState('mixed')
  const [session, setSession] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [answer, setAnswer] = useState('')
  const [answers, setAnswers] = useState([])

  const startInterview = async () => {
    if (!company || !role) return
    
    try {
      const response = await fetch('/api/v1/tools/voice-interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo-user',
          company,
          role,
          interview_type: interviewType
        })
      })
      const data = await response.json()
      setSession(data)
      fetchQuestion(data.session_id)
    } catch (e) {
      console.error(e)
    }
  }

  const fetchQuestion = async (sessionId) => {
    try {
      const response = await fetch(`/api/v1/tools/voice-interview/${sessionId}/question`)
      if (response.ok) {
        const data = await response.json()
        setCurrentQuestion(data)
      }
    } catch (e) {
      console.error(e)
    }
  }

  const submitAnswer = async () => {
    if (!answer || !session) return
    
    try {
      const response = await fetch('/api/v1/tools/voice-interview/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.session_id,
          answer,
          time_taken_seconds: 60
        })
      })
      const data = await response.json()
      setAnswers([...answers, { question: currentQuestion?.question?.question, answer }])
      setAnswer('')
      
      if (data.next_question) {
        setCurrentQuestion(data.next_question)
      } else {
        completeInterview()
      }
    } catch (e) {
      console.error(e)
    }
  }

  const completeInterview = async () => {
    if (!session) return
    
    try {
      const response = await fetch(`/api/v1/tools/voice-interview/${session.session_id}/complete`, {
        method: 'POST'
      })
      const data = await response.json()
      setSession({ ...session, completed: true, feedback: data.feedback })
      setCurrentQuestion(null)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div>
      <div className="header">
        <h1>Voice Mock Interview</h1>
        <p>Practice behavioral and technical interviews with AI feedback.</p>
      </div>

      {!session ? (
        <div className="section">
          <h2>Start New Interview</h2>
          <div className="grid-2">
            <div>
              <div className="form-group">
                <label>Company</label>
                <input className="input" placeholder="e.g., Google, Amazon" value={company} onChange={e => setCompany(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Role</label>
                <input className="input" placeholder="e.g., Senior Engineer" value={role} onChange={e => setRole(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Interview Type</label>
                <select className="input" value={interviewType} onChange={e => setInterviewType(e.target.value)}>
                  <option value="mixed">Mixed (Behavioral + Technical)</option>
                  <option value="behavioral">Behavioral (STAR Questions)</option>
                  <option value="technical">Technical (Coding + System Design)</option>
                  <option value="cultural_fit">Cultural Fit</option>
                </select>
              </div>
              <button className="btn btn-primary" onClick={startInterview}><Play size={18} /> Start Interview</button>
            </div>
            <div>
              <div className="card">
                <h4>How It Works</h4>
                <ul style={{ fontSize: '0.875rem', color: 'var(--text-muted)', paddingLeft: '1rem' }}>
                  <li>Answer questions verbally or in writing</li>
                  <li>Get company-specific questions</li>
                  <li>Receive AI-powered feedback</li>
                  <li>Improve with STAR framework tips</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : session.completed ? (
        <div className="section">
          <h2>Interview Complete!</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Overall Score</h3>
              <div className="value success">{session.feedback?.overall_score}/10</div>
            </div>
            <div className="stat-card">
              <h3>Behavioral Score</h3>
              <div className="value">{session.feedback?.behavioral_score}/10</div>
            </div>
            <div className="stat-card">
              <h3>Technical Score</h3>
              <div className="value">{session.feedback?.technical_score}/10</div>
            </div>
            <div className="stat-card">
              <h3>Grade</h3>
              <div className="value">{session.feedback?.estimated_grade}</div>
            </div>
          </div>
          
          {session.feedback?.strengths && (
            <div style={{ marginBottom: '1rem' }}>
              <h3>Strengths</h3>
              <ul style={{ color: 'var(--success)' }}>
                {session.feedback.strengths.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
          
          {session.feedback?.areas_for_improvement && (
            <div>
              <h3>Areas for Improvement</h3>
              <ul style={{ color: 'var(--warning)' }}>
                {session.feedback.areas_for_improvement.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </div>
          )}
          
          <button className="btn btn-secondary" onClick={() => { setSession(null); setAnswers([]) }}>Start Another Interview</button>
        </div>
      ) : (
        <div className="section">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2>{session.company} - {session.role}</h2>
            <span className="badge info">{session.interview_type}</span>
          </div>
          
          {currentQuestion?.question && (
            <div>
              <div style={{ marginBottom: '1rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: '0.5rem' }}>
                <strong>Question {currentQuestion.question_number}/{currentQuestion.total_questions}</strong>
                <p style={{ marginTop: '0.5rem', fontSize: '1.125rem' }}>{currentQuestion.question.question}</p>
                {currentQuestion.question.star_framework && (
                  <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--background)', borderRadius: '0.5rem', fontSize: '0.875rem' }}>
                    <strong>STAR Framework:</strong> {currentQuestion.question.star_framework}
                  </div>
                )}
              </div>
              
              <div className="form-group">
                <label>Your Answer</label>
                <textarea 
                  className="input" 
                  rows={6} 
                  placeholder="Type your answer here..." 
                  value={answer}
                  onChange={e => setAnswer(e.target.value)}
                />
              </div>
              
              <button className="btn btn-primary" onClick={submitAnswer}><CheckCircle size={18} /> Submit Answer</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
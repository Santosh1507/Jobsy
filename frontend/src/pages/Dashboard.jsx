import React, { useState } from 'react'
import { TrendingUp, Briefcase, Send, Users, Star } from 'lucide-react'

const API_BASE = '/api/v1'

export default function Dashboard() {
  const [stats] = useState({
    totalJobs: 24,
    applied: 12,
    interview: 4,
    offers: 2,
    successRate: 33,
    avgResponseTime: '2.3 days'
  })

  const [recentJobs] = useState([
    { id: 1, title: 'Senior Software Engineer', company: 'Google', grade: 'A', status: 'applied' },
    { id: 2, title: 'ML Engineer', company: 'OpenAI', grade: 'B+', status: 'interview' },
    { id: 3, title: 'Backend Developer', company: 'Stripe', grade: 'A-', status: 'applied' },
    { id: 4, title: 'Staff Engineer', company: 'Netflix', grade: 'B', status: 'pending' },
  ])

  return (
    <div>
      <div className="header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's your job search overview.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Jobs Found</h3>
          <div className="value">{stats.totalJobs}</div>
        </div>
        <div className="stat-card">
          <h3>Applications Sent</h3>
          <div className="value success">{stats.applied}</div>
        </div>
        <div className="stat-card">
          <h3>Interviews</h3>
          <div className="value warning">{stats.interview}</div>
        </div>
        <div className="stat-card">
          <h3>Offers</h3>
          <div className="value success">{stats.offers}</div>
        </div>
      </div>

      <div className="section">
        <h2>Recent Jobs</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Position</th>
              <th>Company</th>
              <th>Grade</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentJobs.map(job => (
              <tr key={job.id}>
                <td>{job.title}</td>
                <td>{job.company}</td>
                <td><span className={`badge ${job.grade.startsWith('A') ? 'success' : job.grade.startsWith('B') ? 'warning' : 'error'}`}>{job.grade}</span></td>
                <td><span className={`badge ${job.status === 'applied' ? 'info' : job.status === 'interview' ? 'warning' : 'success'}`}>{job.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid-2">
        <div className="section">
          <h2>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary">Find Jobs</button>
            <button className="btn btn-secondary">Generate Resume</button>
            <button className="btn btn-secondary">Start Mock Interview</button>
          </div>
        </div>
        <div className="section">
          <h2>Performance</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 700 }}>{stats.successRate}%</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Success Rate</div>
            </div>
            <div>
              <div style={{ fontSize: '2rem', fontWeight: 700 }}>{stats.avgResponseTime}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Avg Response</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
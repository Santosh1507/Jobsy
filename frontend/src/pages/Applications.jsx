import React, { useState } from 'react'
import { Send, CheckCircle, Clock, XCircle } from 'lucide-react'

export default function Applications() {
  const [applications] = useState([
    { id: 1, position: 'Senior Software Engineer', company: 'Google', date: '2024-01-15', status: 'interview', responseTime: '3 days' },
    { id: 2, position: 'Staff Backend Engineer', company: 'Stripe', date: '2024-01-14', status: 'applied', responseTime: '-' },
    { id: 3, position: 'ML Engineer', company: 'OpenAI', date: '2024-01-12', status: 'rejected', responseTime: '5 days' },
    { id: 4, position: 'Principal Engineer', company: 'Netflix', date: '2024-01-10', status: 'offer', responseTime: '7 days' },
    { id: 5, position: 'Senior DevOps', company: 'Datadog', date: '2024-01-08', status: 'applied', responseTime: '-' },
  ])

  const getStatusIcon = (status) => {
    switch(status) {
      case 'interview': return <Clock size={16} className="warning" />
      case 'applied': return <Send size={16} className="info" />
      case 'offer': return <CheckCircle size={16} className="success" />
      case 'rejected': return <XCircle size={16} className="error" />
      default: return null
    }
  }

  return (
    <div>
      <div className="header">
        <h1>Applications</h1>
        <p>Track your job applications and their status.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Applied</h3>
          <div className="value">12</div>
        </div>
        <div className="stat-card">
          <h3>Interviews</h3>
          <div className="value warning">4</div>
        </div>
        <div className="stat-card">
          <h3>Offers</h3>
          <div className="value success">2</div>
        </div>
        <div className="stat-card">
          <h3>Response Rate</h3>
          <div className="value">58%</div>
        </div>
      </div>

      <div className="section">
        <table className="table">
          <thead>
            <tr>
              <th>Position</th>
              <th>Company</th>
              <th>Applied</th>
              <th>Status</th>
              <th>Response Time</th>
            </tr>
          </thead>
          <tbody>
            {applications.map(app => (
              <tr key={app.id}>
                <td><strong>{app.position}</strong></td>
                <td>{app.company}</td>
                <td>{app.date}</td>
                <td>
                  <span className={`badge ${app.status === 'interview' ? 'warning' : app.status === 'offer' ? 'success' : app.status === 'rejected' ? 'error' : 'info'}`}>
                    {getStatusIcon(app.status)} {app.status}
                  </span>
                </td>
                <td>{app.responseTime}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
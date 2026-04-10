import React, { useState } from 'react'
import { Search, Filter, Star } from 'lucide-react'

export default function Jobs() {
  const [jobs, setJobs] = useState([
    { id: 1, title: 'Senior Software Engineer', company: 'Google', location: 'Remote', salary: '$180k-$250k', grade: 'A', fit: 92 },
    { id: 2, title: 'Staff Backend Engineer', company: 'Stripe', location: 'San Francisco', salary: '$220k-$300k', grade: 'A-', fit: 88 },
    { id: 3, title: 'ML Platform Engineer', company: 'OpenAI', location: 'Remote', salary: '$200k-$280k', grade: 'B+', fit: 85 },
    { id: 4, title: 'Principal Engineer', company: 'Netflix', location: 'Los Angeles', salary: '$250k-$350k', grade: 'B', fit: 78 },
    { id: 5, title: 'Senior DevOps Engineer', company: 'Datadog', location: 'Remote', salary: '$160k-$220k', grade: 'A-', fit: 90 },
  ])

  return (
    <div>
      <div className="header">
        <h1>Job Discovery</h1>
        <p>Find and evaluate opportunities that match your profile.</p>
      </div>

      <div className="section">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={20} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input className="input" placeholder="Search jobs..." style={{ paddingLeft: '3rem' }} />
          </div>
          <button className="btn btn-secondary"><Filter size={18} /> Filters</button>
        </div>

        <table className="table">
          <thead>
            <tr>
              <th>Position</th>
              <th>Company</th>
              <th>Location</th>
              <th>Salary</th>
              <th>Fit Score</th>
              <th>Grade</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map(job => (
              <tr key={job.id}>
                <td><strong>{job.title}</strong></td>
                <td>{job.company}</td>
                <td>{job.location}</td>
                <td>{job.salary}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '60px', height: '6px', background: 'var(--surface-light)', borderRadius: '3px' }}>
                      <div style={{ width: `${job.fit}%`, height: '100%', background: job.fit > 85 ? 'var(--success)' : 'var(--warning)', borderRadius: '3px' }} />
                    </div>
                    <span>{job.fit}%</span>
                  </div>
                </td>
                <td><span className={`badge ${job.grade.startsWith('A') ? 'success' : 'warning'}`}>{job.grade}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
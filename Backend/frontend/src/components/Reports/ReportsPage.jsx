import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './ReportsPage.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];
const API_BASE = 'http://localhost:8000/api/reports';

const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [sessionData, setSessionData] = useState([]);
  const [studentData, setStudentData] = useState([]);
  const [questionData, setQuestionData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    days: 30,
    subject: '',
    student: ''
  });

  // Fetch dashboard overview data
  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE}/dashboard`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch session reports
  const fetchSessionData = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions?days=${filters.days}`);
      if (!response.ok) throw new Error('Failed to fetch session data');
      const data = await response.json();
      setSessionData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch student performance data
  const fetchStudentData = async () => {
    try {
      const response = await fetch(`${API_BASE}/students?days=${filters.days}`);
      if (!response.ok) throw new Error('Failed to fetch student data');
      const data = await response.json();
      setStudentData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch question analytics
  const fetchQuestionData = async () => {
    try {
      const response = await fetch(`${API_BASE}/questions`);
      if (!response.ok) throw new Error('Failed to fetch question data');
      const data = await response.json();
      setQuestionData(data.slice(0, 20)); // Limit to first 20 questions for better visualization
    } catch (err) {
      setError(err.message);
    }
  };

  // Load data when component mounts or filters change
  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchDashboardData(),
      fetchSessionData(),
      fetchStudentData(),
      fetchQuestionData()
    ]).finally(() => setLoading(false));
  }, [filters]);

  // Process data for charts
  const getPerformanceTrendData = () => {
    if (!dashboardData?.performance_trends?.daily_accuracy) return [];
    return dashboardData.performance_trends.daily_accuracy.map((accuracy, index) => ({
      day: `Day ${index + 1}`,
      accuracy: accuracy
    }));
  };

  const getSessionAccuracyData = () => {
    return sessionData.map(session => ({
      session: session.student_name.substring(0, 10) + '...',
      accuracy: session.accuracy_percentage,
      questions: session.total_questions
    }));
  };

  const getStudentRankingData = () => {
    return studentData
      .sort((a, b) => b.overall_accuracy - a.overall_accuracy)
      .slice(0, 10)
      .map(student => ({
        name: student.student_name.substring(0, 15) + '...',
        accuracy: student.overall_accuracy,
        sessions: student.total_sessions
      }));
  };

  const getQuestionDifficultyData = () => {
    const difficultyGroups = questionData.reduce((acc, question) => {
      const difficulty = question.difficulty_level || 'unknown';
      acc[difficulty] = (acc[difficulty] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(difficultyGroups).map(([difficulty, count]) => ({
      name: difficulty.charAt(0).toUpperCase() + difficulty.slice(1),
      value: count
    }));
  };

  const getSubjectDistributionData = () => {
    const subjectGroups = questionData.reduce((acc, question) => {
      const subject = question.subject || 'unknown';
      acc[subject] = (acc[subject] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(subjectGroups).map(([subject, count]) => ({
      name: subject.replace('_', ' ').toUpperCase(),
      value: count
    }));
  };

  if (loading) {
    return (
      <div className="reports-loading">
        <div className="loading-spinner">🔄</div>
        <p>Loading analytics data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reports-error">
        <h3>❌ Error Loading Reports</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="reports-page">
      <div className="reports-header">
        <h1>📊 Analytics Dashboard</h1>
        <div className="reports-filters">
          <select 
            value={filters.days} 
            onChange={(e) => setFilters({...filters, days: parseInt(e.target.value)})}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      <div className="reports-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
          onClick={() => setActiveTab('sessions')}
        >
          📝 Session Reports
        </button>
        <button 
          className={`tab-button ${activeTab === 'students' ? 'active' : ''}`}
          onClick={() => setActiveTab('students')}
        >
          👥 Student Performance
        </button>
        <button 
          className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          ❓ Question Analytics
        </button>
      </div>

      <div className="reports-content">
        {activeTab === 'overview' && (
          <OverviewTab 
            dashboardData={dashboardData}
            performanceTrendData={getPerformanceTrendData()}
          />
        )}
        
        {activeTab === 'sessions' && (
          <SessionReportsTab 
            sessionData={sessionData}
            accuracyData={getSessionAccuracyData()}
          />
        )}
        
        {activeTab === 'students' && (
          <StudentPerformanceTab 
            studentData={studentData}
            rankingData={getStudentRankingData()}
          />
        )}
        
        {activeTab === 'questions' && (
          <QuestionAnalyticsTab 
            questionData={questionData}
            difficultyData={getQuestionDifficultyData()}
            subjectData={getSubjectDistributionData()}
          />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ dashboardData, performanceTrendData }) => {
  if (!dashboardData) return <div>No dashboard data available</div>;

  return (
    <div className="overview-tab">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{dashboardData.total_students}</h3>
            <p>Total Students</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <h3>{dashboardData.total_sessions}</h3>
            <p>Total Sessions</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✍️</div>
          <div className="stat-content">
            <h3>{dashboardData.total_submissions}</h3>
            <p>Total Submissions</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>{dashboardData.average_session_accuracy}%</h3>
            <p>Average Accuracy</p>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>📈 Performance Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
              <Line 
                type="monotone" 
                dataKey="accuracy" 
                stroke="#8884d8" 
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>🏆 Popular Subject</h3>
          <div className="popular-subject">
            <div className="subject-icon">📚</div>
            <h4>{dashboardData.most_popular_subject}</h4>
            <p>Most studied subject</p>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>🕒 Recent Activity</h3>
        <div className="activity-list">
          {dashboardData.recent_activity?.slice(0, 5).map((activity, index) => (
            <div key={index} className="activity-item">
              <div className="activity-student">
                <strong>{activity.student}</strong>
                <div className="activity-subject">{activity.subject}</div>
              </div>
              <div className="activity-result">
                <span className={`result-badge ${activity.correct ? 'correct' : 'incorrect'}`}>
                  {activity.correct ? '✓ Correct' : '✗ Incorrect'}
                </span>
                <div className="mastery-level">
                  Mastery: {(activity.mastery * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Session Reports Tab Component
const SessionReportsTab = ({ sessionData, accuracyData }) => {
  return (
    <div className="sessions-tab">
      <div className="session-stats">
        <h3>📊 Session Accuracy Overview</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={accuracyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="session" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="accuracy" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="session-details">
        <h3>📝 Session Details</h3>
        <div className="session-table">
          {sessionData.slice(0, 10).map((session, index) => (
            <div key={index} className="session-row">
              <div className="session-info">
                <strong>{session.student_name}</strong>
                <div className="session-meta">
                  {session.subject} • {session.total_questions} questions
                </div>
              </div>
              <div className="session-metrics">
                <div className="accuracy-badge">
                  {session.accuracy_percentage}% accuracy
                </div>
                <div className="duration-info">
                  {session.session_duration_minutes.toFixed(1)} min
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Student Performance Tab Component
const StudentPerformanceTab = ({ studentData, rankingData }) => {
  return (
    <div className="students-tab">
      <div className="student-ranking">
        <h3>🏆 Top Performing Students</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={rankingData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="accuracy" fill="#00C49F" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="student-details">
        <h3>👥 Student Performance Details</h3>
        <div className="student-grid">
          {studentData.slice(0, 8).map((student, index) => (
            <div key={index} className="student-card">
              <div className="student-header">
                <h4>{student.student_name}</h4>
                <div className="accuracy-circle">
                  {student.overall_accuracy}%
                </div>
              </div>
              <div className="student-metrics">
                <div className="metric">
                  <span>Sessions:</span> {student.total_sessions}
                </div>
                <div className="metric">
                  <span>Questions:</span> {student.total_questions_attempted}
                </div>
                <div className="metric">
                  <span>Growth:</span> {(student.mastery_growth * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Question Analytics Tab Component
const QuestionAnalyticsTab = ({ questionData, difficultyData, subjectData }) => {
  return (
    <div className="questions-tab">
      <div className="charts-row">
        <div className="chart-card">
          <h3>📊 Difficulty Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={difficultyData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {difficultyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>📚 Subject Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={subjectData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#82ca9d"
                dataKey="value"
              >
                {subjectData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="question-performance">
        <h3>❓ Question Performance</h3>
        <div className="question-list">
          {questionData.slice(0, 10).map((question, index) => (
            <div key={index} className="question-item">
              <div className="question-text">
                <strong>Q{index + 1}:</strong> {question.question_text}
              </div>
              <div className="question-stats">
                <span className="difficulty-tag">
                  {question.difficulty_level}
                </span>
                <span className="success-rate">
                  Success: {question.success_rate}%
                </span>
                <span className="attempts">
                  {question.total_attempts} attempts
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
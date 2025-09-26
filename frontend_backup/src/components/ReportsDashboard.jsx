import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

// ============================================================================
// Main Reports Dashboard Component
// ============================================================================

const ReportsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [sessionReports, setSessionReports] = useState([]);
  const [studentReports, setStudentReports] = useState([]);
  const [questionAnalytics, setQuestionAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const API_BASE = 'http://localhost:8000/api/reports';

  useEffect(() => {
    fetchAllData();
    // Auto-refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [dashboard, sessions, students, questions] = await Promise.all([
        fetch(`${API_BASE}/dashboard`).then(async r => {
          if (!r.ok) throw new Error(`Dashboard API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/sessions?days=30`).then(async r => {
          if (!r.ok) throw new Error(`Sessions API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/students?days=30`).then(async r => {
          if (!r.ok) throw new Error(`Students API error: ${r.status}`);
          return r.json();
        }),
        fetch(`${API_BASE}/questions`).then(async r => {
          if (!r.ok) throw new Error(`Questions API error: ${r.status}`);
          return r.json();
        })
      ]);

      setDashboardData(dashboard);
      setSessionReports(sessions);
      setStudentReports(students);
      setQuestionAnalytics(questions);
      setError(null);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'sessions', name: 'Session Reports', icon: '📝' },
    { id: 'students', name: 'Student Performance', icon: '👥' },
    { id: 'questions', name: 'Question Analytics', icon: '❓' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Learning Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">Comprehensive reports and insights from adaptive learning data</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              error ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${error ? 'bg-red-500' : 'bg-green-500'}`}></div>
              <span>{error ? 'Disconnected' : 'Connected'}</span>
            </div>
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
            </div>
            <button
              onClick={fetchAllData}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium ${
                loading 
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {loading ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Refreshing...
                </span>
              ) : (
                '🔄 Refresh Data'
              )}
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-red-400 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>Unable to fetch latest data: {error}</p>
                  <p className="mt-1">Make sure the Django server is running on http://localhost:8000</p>
                </div>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => {setError(null); fetchAllData();}}
                  className="bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'overview' && <OverviewTab data={dashboardData} />}
        {activeTab === 'sessions' && <SessionReportsTab data={sessionReports} />}
        {activeTab === 'students' && <StudentPerformanceTab data={studentReports} />}
        {activeTab === 'questions' && <QuestionAnalyticsTab data={questionAnalytics} />}
      </div>
    </div>
  );
};

// ============================================================================
// Overview Tab Component
// ============================================================================

const OverviewTab = ({ data }) => {
  if (!data) return (
    <div className="text-center py-12">
      <div className="text-gray-400 text-4xl mb-4">📊</div>
      <p className="text-gray-500">Loading overview data...</p>
    </div>
  );

  const dailyTrendData = data.performance_trends?.daily_accuracy?.map((accuracy, index) => ({
    day: `Day ${index + 1}`,
    accuracy: accuracy,
  })) || [];

  const statsCards = [
    { title: 'Total Students', value: data.total_students, icon: '👥', color: 'blue' },
    { title: 'Total Sessions', value: data.total_sessions, icon: '📝', color: 'green' },
    { title: 'Total Submissions', value: data.total_submissions, icon: '✍️', color: 'purple' },
    { title: 'Average Accuracy', value: `${data.average_session_accuracy}%`, icon: '🎯', color: 'orange' },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`text-3xl mr-4`}>{stat.icon}</div>
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Performance Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📈 Daily Performance Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
              <Line type="monotone" dataKey="accuracy" stroke="#3B82F6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">🕒 Recent Activity</h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {(data.recent_activity || []).map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">{activity.student}</p>
                  <p className="text-sm text-gray-600">{activity.subject}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex px-2 py-1 text-xs rounded ${
                    activity.correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {activity.correct ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">Mastery: {(activity.mastery * 100).toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">🏆 Most Popular Subject</h3>
        <div className="text-center">
          <div className="text-4xl mb-2">📚</div>
          <p className="text-xl font-semibold">{data.most_popular_subject}</p>
          <p className="text-gray-600">Students are focusing on this subject the most</p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Session Reports Tab Component
// ============================================================================

const SessionReportsTab = ({ data }) => {
  const [selectedSession, setSelectedSession] = useState(null);

  const processSessionData = (sessions) => {
    return sessions.map(session => ({
      ...session,
      date: new Date(session.start_time).toLocaleDateString(),
      time: new Date(session.start_time).toLocaleTimeString(),
    }));
  };

  const sessionChartData = processSessionData(data).slice(0, 10).map(session => ({
    session: `${session.student_name.substring(0, 10)}...`,
    accuracy: session.accuracy_percentage,
    questions: session.total_questions,
    time: session.average_time_per_question,
  }));

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Session Performance Overview</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={sessionChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="session" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="accuracy" fill="#3B82F6" name="Accuracy %" />
            <Bar yAxisId="right" dataKey="questions" fill="#10B981" name="Questions" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📝 Recent Sessions</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {processSessionData(data).map((session, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedSession?.session_id === session.session_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedSession(session)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{session.student_name}</p>
                    <p className="text-sm text-gray-600">{session.subject}</p>
                    <p className="text-xs text-gray-500">{session.date} at {session.time}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">{session.accuracy_percentage}%</p>
                    <p className="text-sm text-gray-600">{session.correct_answers}/{session.total_questions}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Session Detail */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Session Details</h3>
          {selectedSession ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">Session Information</h4>
                <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Student:</span> {selectedSession.student_name}
                  </div>
                  <div>
                    <span className="text-gray-600">Subject:</span> {selectedSession.subject}
                  </div>
                  <div>
                    <span className="text-gray-600">Duration:</span> {selectedSession.session_duration_minutes} min
                  </div>
                  <div>
                    <span className="text-gray-600">Avg Time/Question:</span> {selectedSession.average_time_per_question}s
                  </div>
                </div>
              </div>

              {/* Mastery Progression Chart */}
              {selectedSession.mastery_progression.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">📈 Mastery Progression</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={selectedSession.mastery_progression.map((mastery, index) => ({
                      question: `Q${index + 1}`,
                      mastery: (mastery * 100).toFixed(1),
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="question" />
                      <YAxis />
                      <Tooltip formatter={(value) => [`${value}%`, 'Mastery']} />
                      <Area type="monotone" dataKey="mastery" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Difficulty Distribution */}
              <div>
                <h4 className="font-medium mb-2">📊 Difficulty Distribution</h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(selectedSession.difficulty_distribution).map(([level, count]) => (
                    <div key={level} className="flex justify-between p-2 bg-gray-50 rounded">
                      <span className="capitalize">{level}:</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Select a session to view details</p>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Student Performance Tab Component
// ============================================================================

const StudentPerformanceTab = ({ data }) => {
  const [selectedStudent, setSelectedStudent] = useState(null);

  const studentChartData = data.slice(0, 10).map(student => ({
    name: student.student_name.substring(0, 12) + '...',
    accuracy: student.overall_accuracy,
    questions: student.total_questions_attempted,
    mastery_growth: student.mastery_growth * 100,
  }));

  return (
    <div className="space-y-6">
      {/* Student Performance Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">👥 Student Performance Comparison</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={studentChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="accuracy" fill="#3B82F6" name="Accuracy %" />
            <Bar dataKey="mastery_growth" fill="#10B981" name="Mastery Growth %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Student List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">🎓 Student Rankings</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {data
              .sort((a, b) => b.overall_accuracy - a.overall_accuracy)
              .map((student, index) => (
                <div
                  key={student.student_id}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedStudent?.student_id === student.student_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedStudent(student)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 ${
                        index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium">{student.student_name}</p>
                        <p className="text-sm text-gray-600">{student.subjects_studied.join(', ')}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">{student.overall_accuracy}%</p>
                      <p className="text-sm text-gray-600">{student.total_questions_attempted} questions</p>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* Student Detail */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Student Analysis</h3>
          {selectedStudent ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">Performance Metrics</h4>
                <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Sessions:</span> {selectedStudent.total_sessions}
                  </div>
                  <div>
                    <span className="text-gray-600">Questions:</span> {selectedStudent.total_questions_attempted}
                  </div>
                  <div>
                    <span className="text-gray-600">Accuracy:</span> {selectedStudent.overall_accuracy}%
                  </div>
                  <div>
                    <span className="text-gray-600">Mastery Growth:</span> {(selectedStudent.mastery_growth * 100).toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Performance Trend */}
              {selectedStudent.performance_trend.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">📈 Weekly Performance Trend</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={selectedStudent.performance_trend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
                      <Line type="monotone" dataKey="accuracy" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Subjects */}
              <div>
                <h4 className="font-medium mb-2">📚 Subjects Studied</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedStudent.subjects_studied.map((subject) => (
                    <span key={subject} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                      {subject}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium">Last Activity</h4>
                <p className="text-sm text-gray-600 mt-1">
                  {new Date(selectedStudent.last_activity).toLocaleString()}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Select a student to view detailed analysis</p>
          )}
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// Question Analytics Tab Component
// ============================================================================

const QuestionAnalyticsTab = ({ data }) => {
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [subjectFilter, setSubjectFilter] = useState('all');

  const subjects = [...new Set(data.map(q => q.subject))];
  
  const filteredData = subjectFilter === 'all' 
    ? data 
    : data.filter(q => q.subject === subjectFilter);

  const difficultyData = Object.values(
    filteredData.reduce((acc, question) => {
      const level = question.difficulty_level;
      if (!acc[level]) {
        acc[level] = { level, count: 0, totalSuccess: 0 };
      }
      acc[level].count++;
      acc[level].totalSuccess += question.success_rate;
      acc[level].avgSuccess = acc[level].totalSuccess / acc[level].count;
      return acc;
    }, {})
  );

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-4">
          <label className="font-medium">Filter by Subject:</label>
          <select
            value={subjectFilter}
            onChange={(e) => setSubjectFilter(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="all">All Subjects</option>
            {subjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Question Difficulty Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📊 Questions by Difficulty</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={difficultyData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({level, count}) => `${level}: ${count}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {difficultyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">📈 Success Rate by Difficulty</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={difficultyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="level" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Success Rate']} />
              <Bar dataKey="avgSuccess" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Questions List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">❓ Question Performance</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredData.slice(0, 20).map((question, index) => (
              <div
                key={question.question_id}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedQuestion?.question_id === question.question_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedQuestion(question)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 mr-4">
                    <p className="text-sm font-medium">{question.question_text}</p>
                    <div className="flex items-center mt-2 space-x-4 text-xs text-gray-600">
                      <span>📚 {question.subject}</span>
                      <span>⭐ {question.difficulty_level}</span>
                      <span>👥 {question.total_attempts} attempts</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      question.success_rate >= 80 ? 'text-green-600' :
                      question.success_rate >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {question.success_rate}%
                    </p>
                    <p className="text-sm text-gray-600">success rate</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Question Detail */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Question Analysis</h3>
          {selectedQuestion ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">Question Details</h4>
                <p className="text-sm text-gray-600 mt-2">{selectedQuestion.question_text}</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Subject:</span> {selectedQuestion.subject}
                </div>
                <div>
                  <span className="text-gray-600">Difficulty:</span> {selectedQuestion.difficulty_level}
                </div>
                <div>
                  <span className="text-gray-600">Total Attempts:</span> {selectedQuestion.total_attempts}
                </div>
                <div>
                  <span className="text-gray-600">Correct Attempts:</span> {selectedQuestion.correct_attempts}
                </div>
                <div>
                  <span className="text-gray-600">Success Rate:</span> {selectedQuestion.success_rate}%
                </div>
                <div>
                  <span className="text-gray-600">Avg Time:</span> {selectedQuestion.average_time_spent}s
                </div>
              </div>

              {selectedQuestion.most_common_wrong_answer && (
                <div>
                  <h4 className="font-medium">Common Mistakes</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    Most common wrong answer: <span className="font-medium">{selectedQuestion.most_common_wrong_answer}</span>
                  </p>
                </div>
              )}

              {/* Performance Indicator */}
              <div>
                <h4 className="font-medium">Performance Indicator</h4>
                <div className={`mt-2 p-3 rounded ${
                  selectedQuestion.success_rate >= 80 ? 'bg-green-100 text-green-800' :
                  selectedQuestion.success_rate >= 60 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {selectedQuestion.success_rate >= 80 ? '🟢 Easy - Students perform well' :
                   selectedQuestion.success_rate >= 60 ? '🟡 Moderate - Room for improvement' :
                   '🔴 Challenging - Consider review or hints'}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Select a question to view detailed analysis</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsDashboard;
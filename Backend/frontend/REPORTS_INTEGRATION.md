# Reports Dashboard Integration Guide

## 📊 Overview
This guide helps you integrate the comprehensive Reports Dashboard into your main React application.

## 🚀 Quick Setup

### 1. Install Required Dependencies
```bash
npm install recharts
# or
yarn add recharts
```

### 2. Copy Component Files
- Copy `ReportsPage.jsx` to your components directory
- Copy `ReportsPage.css` to the same directory
- Import both files in your main app

### 3. Add Route (if using React Router)
```jsx
import ReportsPage from './components/Reports/ReportsPage';

// In your App.js or router configuration
<Route path="/reports" component={ReportsPage} />
```

### 4. Add Navigation Link
```jsx
// In your navigation component
<Link to="/reports">📊 Analytics Dashboard</Link>
```

## 🔧 Configuration

### API Base URL
Update the API_BASE constant in ReportsPage.jsx:
```jsx
const API_BASE = 'http://your-domain.com/api/reports';
```

### Custom Styling
The component uses CSS modules. You can customize:
- Colors in the COLORS array
- Chart dimensions in ResponsiveContainer
- Styling in ReportsPage.css

## 📈 Features Included

### 1. Overview Tab
- **Key Metrics Cards**: Total students, sessions, submissions, average accuracy
- **Performance Trend Chart**: Daily accuracy progression
- **Popular Subject Display**: Most studied subject
- **Recent Activity Feed**: Live student activity with mastery levels

### 2. Session Reports Tab
- **Session Accuracy Chart**: Bar chart showing accuracy per session
- **Session Details Table**: Comprehensive session information with duration and metrics

### 3. Student Performance Tab
- **Top Students Ranking**: Bar chart of highest performing students
- **Student Cards Grid**: Individual student performance with growth metrics

### 4. Question Analytics Tab
- **Difficulty Distribution**: Pie chart showing question difficulty breakdown
- **Subject Distribution**: Pie chart of questions by subject
- **Question Performance List**: Detailed question analytics with success rates

## 🎨 Customization Options

### Chart Colors
```jsx
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];
```

### Filter Options
```jsx
const [filters, setFilters] = useState({
  days: 30,        // Time range filter
  subject: '',     // Subject filter (extendable)
  student: ''      // Student filter (extendable)
});
```

### Data Refresh
The component automatically refreshes data when filters change. For real-time updates, add:
```jsx
useEffect(() => {
  const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
  return () => clearInterval(interval);
}, []);
```

## 🔌 API Endpoints Used

1. **Dashboard Overview**: `GET /api/reports/dashboard`
2. **Session Reports**: `GET /api/reports/sessions?days={days}`
3. **Student Performance**: `GET /api/reports/students?days={days}`
4. **Question Analytics**: `GET /api/reports/questions`

## 📱 Mobile Responsive
The dashboard is fully responsive with:
- Mobile-first CSS Grid layouts
- Flexible chart containers
- Collapsible navigation
- Touch-friendly interactions

## 🚨 Error Handling
- Network error handling with user-friendly messages
- Loading states for better UX
- Retry functionality for failed requests
- Graceful fallbacks for missing data

## 🧪 Testing
Test the component with:
```bash
# Start your Django server
python manage.py runserver

# Open the test dashboard
# Navigate to http://localhost:3000/reports (if using React dev server)
```

## 🔍 Troubleshooting

### Common Issues:

1. **CORS Errors**: Add your React app's URL to Django CORS settings
2. **API Not Found**: Ensure Django server is running and reports API is registered
3. **Charts Not Rendering**: Check that Recharts is properly installed
4. **Data Not Loading**: Verify API endpoints return expected JSON structure

### Debug Mode:
Add console logging to see API responses:
```jsx
const fetchDashboardData = async () => {
  try {
    const response = await fetch(`${API_BASE}/dashboard`);
    const data = await response.json();
    console.log('Dashboard Data:', data); // Debug logging
    setDashboardData(data);
  } catch (err) {
    console.error('Error:', err);
  }
};
```

## 🎯 Next Steps
1. Add real-time updates with WebSockets
2. Implement data export functionality
3. Add more filter options (date ranges, specific students)
4. Create printable report views
5. Add admin-only analytics views

## 📞 Support
If you need help integrating this component:
1. Check that all API endpoints are working
2. Verify Recharts installation
3. Ensure proper CSS imports
4. Test with sample data first

Happy coding! 🚀
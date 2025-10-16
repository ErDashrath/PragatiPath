# Practice History Integration Fix for Adaptive Learning

## Problem Identified
The user reported: "we have to work on showing the same details as practice history to adaptive learning some fetching problem is ther ig"

The issue is that the frontend adaptive learning section tries to display practice history data, but there are two separate systems:
1. **Practice System** - SM-2 spaced repetition (`Backend/practice/api.py`)  
2. **Adaptive Learning System** - BKT/DKT system (`Backend/simple_frontend_api.py`)

Both have different data formats and endpoints, causing fetching problems.

## Root Cause Analysis
- Frontend `assessment-history.tsx` uses `AdaptiveLearningAPI.getSessionHistory()` for adaptive learning tab
- This API calls `/simple/session-history/<userId>/` which only shows adaptive learning sessions
- Practice history from SM-2 system is stored separately and uses different endpoints
- The practice system has its own API at `/api/v1/practice/` with different data structures

## Solution: Unified Practice History API

### 1. Create Practice History API Endpoint

Create a new endpoint that combines both practice and adaptive learning session data:

```python
# Backend/practice/practice_history_api.py
from ninja import Router
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import SRSCard
from assessment.models import StudentSession
import json

router = Router()

@csrf_exempt
def get_unified_practice_history(request, student_id):
    """
    Get unified practice history combining SM-2 and adaptive learning data
    """
    try:
        student = get_object_or_404(User, id=student_id)
        
        # Get SM-2 practice sessions
        sm2_cards = SRSCard.objects.filter(
            student=student
        ).select_related('question').order_by('-last_reviewed')
        
        # Get adaptive learning sessions
        adaptive_sessions = StudentSession.objects.filter(
            student=student,
            status='COMPLETED'
        ).order_by('-session_end_time')
        
        # Combine and format data
        unified_history = {
            'success': True,
            'student_id': str(student_id),
            'student_name': student.get_full_name() or student.username,
            'total_sessions': len(sm2_cards) + len(adaptive_sessions),
            'practice_sessions': [],
            'adaptive_sessions': [],
            'combined_sessions': []
        }
        
        # Add SM-2 practice sessions
        for card in sm2_cards[:20]:  # Last 20 cards
            practice_data = {
                'session_id': f'practice_{card.id}',
                'type': 'practice',
                'subject': card.question.subject if card.question else 'Mixed',
                'session_date': card.last_reviewed.strftime('%Y-%m-%d %H:%M') if card.last_reviewed else 'Never',
                'stage': card.stage,
                'ease_factor': card.ease_factor,
                'interval_days': card.interval,
                'repetitions': card.repetition,
                'success_rate': card.success_rate,
                'total_reviews': card.total_reviews,
                'mastery_level': get_practice_mastery_level(card),
                'question_text': card.question.question_text[:100] + '...' if card.question else 'N/A'
            }
            unified_history['practice_sessions'].append(practice_data)
            unified_history['combined_sessions'].append(practice_data)
        
        # Add adaptive learning sessions (existing logic)
        for session in adaptive_sessions[:20]:
            session_config = session.session_config or {}
            adaptive_data = {
                'session_id': str(session.id),
                'type': 'adaptive',
                'subject': session_config.get('subject', 'Mixed'),
                'session_date': session.session_end_time.strftime('%Y-%m-%d %H:%M') if session.session_end_time else 'Unknown',
                'duration_minutes': round(session.session_duration_seconds / 60, 1) if session.session_duration_seconds else 0,
                'questions_attempted': session.questions_attempted,
                'accuracy': f"{session.percentage_score:.1f}%" if session.percentage_score else "0%",
                'mastery_scores': {
                    'bkt_mastery': f"{session_config.get('final_bkt_mastery', 0.0):.1%}",
                    'dkt_prediction': f"{session_config.get('final_dkt_prediction', 0.0):.1%}",
                    'mastery_level': get_adaptive_mastery_level(session_config.get('final_bkt_mastery', 0.0))
                }
            }
            unified_history['adaptive_sessions'].append(adaptive_data)
            unified_history['combined_sessions'].append(adaptive_data)
        
        # Sort combined sessions by date
        unified_history['combined_sessions'].sort(
            key=lambda x: x['session_date'], 
            reverse=True
        )
        
        return JsonResponse(unified_history)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_practice_mastery_level(card):
    """Calculate mastery level for SM-2 practice card"""
    if card.success_rate >= 0.9 and card.stage in ['graduated', 'review']:
        return 'expert'
    elif card.success_rate >= 0.8:
        return 'advanced'
    elif card.success_rate >= 0.6:
        return 'proficient'
    elif card.success_rate >= 0.4:
        return 'developing'
    else:
        return 'novice'
```

### 2. Update Frontend API Client

Add unified practice history method to `adaptive-api.ts`:

```typescript
// frontend/client/src/lib/adaptive-api.ts

export interface UnifiedPracticeHistory {
  success: boolean;
  student_id: string;
  student_name: string;
  total_sessions: number;
  practice_sessions: Array<{
    session_id: string;
    type: 'practice';
    subject: string;
    session_date: string;
    stage: string;
    ease_factor: number;
    interval_days: number;
    repetitions: number;
    success_rate: number;
    total_reviews: number;
    mastery_level: string;
    question_text: string;
  }>;
  adaptive_sessions: Array<{
    session_id: string;
    type: 'adaptive';
    subject: string;
    session_date: string;
    duration_minutes: number;
    questions_attempted: number;
    accuracy: string;
    mastery_scores: {
      bkt_mastery: string;
      dkt_prediction: string;
      mastery_level: string;
    };
  }>;
  combined_sessions: Array<any>;
}

export class AdaptiveLearningAPI {
  // ... existing methods ...
  
  /**
   * Get unified practice history (SM-2 + Adaptive Learning)
   */
  static async getUnifiedPracticeHistory(userId: number): Promise<UnifiedPracticeHistory> {
    const response = await fetch(`${ADAPTIVE_API_BASE}/practice-history/${userId}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get unified practice history');
    }
    
    return response.json();
  }
}
```

### 3. Update Frontend Component

Modify `assessment-history.tsx` to use unified data:

```tsx
// frontend/client/src/components/student/assessment-history.tsx

// Add state for unified practice history
const [unifiedPracticeHistory, setUnifiedPracticeHistory] = useState<any>(null);

// Update loadData function
const loadData = async () => {
  // ... existing code ...
  
  // Load unified practice history
  try {
    if (userId) {
      const unifiedData = await AdaptiveLearningAPI.getUnifiedPracticeHistory(userId);
      console.log('🔄 Unified practice history loaded:', unifiedData);
      setUnifiedPracticeHistory(unifiedData);
    }
  } catch (unifiedErr) {
    console.warn('Unified practice history not available:', unifiedErr);
  }
};

// Add new tab for unified practice history
<TabsContent value="practice" className="space-y-4">
  {unifiedPracticeHistory && unifiedPracticeHistory.success ? (
    <div className="space-y-4">
      {/* Practice Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="h-5 w-5 mr-2 text-green-600" />
            SM-2 Practice Sessions ({unifiedPracticeHistory.practice_sessions.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {unifiedPracticeHistory.practice_sessions.map((session: any) => (
              <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge className={`${getMasteryColor(session.mastery_level)} text-white`}>
                      {session.mastery_level}
                    </Badge>
                    <span className="font-medium">{session.subject}</span>
                    <Badge variant="outline">
                      Stage: {session.stage}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Success Rate: {(session.success_rate * 100).toFixed(1)}% • 
                    Reviews: {session.total_reviews} • 
                    Interval: {session.interval_days} days
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {session.question_text}
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => onViewDetails(session.session_id)}>
                  <Eye className="h-4 w-4 mr-1" />
                  Details
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Combined Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Combined Learning Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {unifiedPracticeHistory.combined_sessions.slice(0, 10).map((session: any, index: number) => (
              <div key={`${session.type}_${session.session_id}`} className="flex items-center gap-3 p-2 rounded">
                <div className={`w-3 h-3 rounded-full ${session.type === 'practice' ? 'bg-green-500' : 'bg-purple-500'}`}></div>
                <div className="flex-1">
                  <span className="font-medium">{session.subject}</span>
                  <span className="text-sm text-muted-foreground ml-2">
                    {session.type === 'practice' ? 'Practice' : 'Adaptive'} • {session.session_date}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  ) : (
    <Card>
      <CardContent className="p-8 text-center">
        <Target className="h-12 w-12 text-green-400 mx-auto mb-4" />
        <p className="text-muted-foreground">No practice sessions found</p>
        <p className="text-sm text-muted-foreground">Start practicing to see your spaced repetition progress here</p>
      </CardContent>
    </Card>
  )}
</TabsContent>
```

### 4. Add URL Routing

Update `Backend/adaptive_learning/urls.py`:

```python
# Add to urlpatterns
path('simple/practice-history/<str:student_id>/', practice_history_api.get_unified_practice_history, name='get_unified_practice_history'),
```

## Implementation Steps

1. **Create the unified API** - Implement `practice_history_api.py`
2. **Update frontend API client** - Add `getUnifiedPracticeHistory` method
3. **Modify assessment history component** - Add unified practice history tab
4. **Add URL routing** - Connect the new endpoint
5. **Test integration** - Verify data flows correctly

## Expected Result
- ✅ Practice history will show in adaptive learning section
- ✅ Both SM-2 spaced repetition and adaptive learning sessions visible
- ✅ Unified timeline showing all learning activities
- ✅ Consistent data format between practice and adaptive systems
- ✅ No more fetching problems between systems

This fix creates a bridge between the two learning systems and provides the unified practice history display that the user requested.
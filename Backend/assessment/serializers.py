from rest_framework import serializers
from django.utils import timezone
from .models import AdaptiveQuestion, Interaction, ExamSession
from .user_session_models import UserSession, UserQuestionHistory, UserSubjectProgress, UserDailyStats

class QuestionOptionSerializer(serializers.Serializer):
    """Serializer for question options"""
    a = serializers.CharField()
    b = serializers.CharField() 
    c = serializers.CharField()
    d = serializers.CharField()

class QuestionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for questions with all options"""
    options = serializers.SerializerMethodField()
    correct_option_text = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = AdaptiveQuestion
        fields = [
            'id', 'question_text', 'question_type', 'subject', 
            'topic', 'subtopic', 'difficulty_level', 'level',
            'options', 'answer', 'correct_option_text', 
            'estimated_time_seconds', 'tags', 'success_rate',
            'times_attempted', 'times_correct'
        ]
    
    def get_options(self, obj):
        return obj.formatted_options

class QuestionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for question lists (no correct answer exposed)"""
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = AdaptiveQuestion
        fields = [
            'id', 'question_text', 'question_type', 'subject',
            'topic', 'subtopic', 'difficulty_level', 'level', 
            'options', 'estimated_time_seconds', 'tags'
        ]
    
    def get_options(self, obj):
        return obj.formatted_options

class ChapterQuestionSerializer(serializers.ModelSerializer):
    """Serializer for chapter-specific questions"""
    options = serializers.SerializerMethodField()
    chapter = serializers.SerializerMethodField()
    
    class Meta:
        model = AdaptiveQuestion
        fields = [
            'id', 'question_text', 'question_type', 'subject',
            'chapter', 'topic', 'subtopic', 'difficulty_level', 
            'level', 'options', 'estimated_time_seconds', 'tags'
        ]
    
    def get_options(self, obj):
        return obj.formatted_options
    
    def get_chapter(self, obj):
        """Map topic to chapter names based on CSV structure"""
        chapter_mapping = {
            # Quantitative Aptitude
            'percentages': 'Percentages',
            'ratios_and_proportions': 'Ratios and Proportions', 
            'profit_and_loss': 'Profit and Loss',
            
            # Logical Reasoning
            'pattern_recognition': 'Pattern Recognition',
            'syllogisms': 'Syllogisms',
            'data_interpretation_general': 'Data Interpretation General',
            
            # Verbal Ability
            'vocabulary': 'Vocabulary',
            'grammar': 'Grammar', 
            'reading_comprehension': 'Reading Comprehension',
            
            # Data Interpretation
            'bar_charts': 'Bar Charts',
            'line_graphs': 'Line Graphs',
            'pie_charts': 'Pie Charts'
        }
        
        # Try to match from tags or topic
        tags = obj.tags.lower().split(',') if obj.tags else []
        topic = obj.topic.lower().replace(' ', '_') if obj.topic else ''
        
        for tag in tags:
            if tag.strip() in chapter_mapping:
                return chapter_mapping[tag.strip()]
        
        if topic in chapter_mapping:
            return chapter_mapping[topic]
            
        return obj.topic or 'General'

class InteractionSerializer(serializers.ModelSerializer):
    """Serializer for student interactions"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    subject = serializers.CharField(source='question.subject', read_only=True)
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'student', 'question', 'question_text', 'subject',
            'is_correct', 'student_answer', 'response_time',
            'confidence_level', 'session_id', 'assessment_mode',
            'timestamp'
        ]

class ExamSessionSerializer(serializers.ModelSerializer):
    """Serializer for exam sessions"""
    accuracy_rate = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'student', 'subject', 'assessment_mode', 'status',
            'questions_attempted', 'questions_correct', 'accuracy_rate',
            'total_time_spent', 'duration_minutes', 'current_difficulty',
            'initial_mastery_score', 'final_mastery_score', 'mastery_improvement',
            'started_at', 'completed_at'
        ]

class SubjectStatsSerializer(serializers.Serializer):
    """Serializer for subject statistics"""
    subject_code = serializers.CharField()
    subject_name = serializers.CharField()
    total_questions = serializers.IntegerField()
    difficulty_breakdown = serializers.DictField()
    chapter_breakdown = serializers.DictField()
    avg_difficulty = serializers.FloatField()

class ChapterStatsSerializer(serializers.Serializer):
    """Serializer for chapter statistics"""
    chapter_name = serializers.CharField()
    question_count = serializers.IntegerField()
    difficulty_levels = serializers.DictField()
    avg_success_rate = serializers.FloatField()


# User Session Management Serializers

class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user study sessions"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    accuracy_percentage = serializers.FloatField(read_only=True)
    average_time_per_question = serializers.FloatField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'username', 'session_type', 'subject', 'chapter_number',
            'status', 'current_question_index', 'session_start_time', 'session_end_time',
            'total_duration_seconds', 'questions_attempted', 'questions_correct',
            'current_score', 'accuracy_percentage', 'average_time_per_question',
            'current_difficulty_level', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'session_start_time']


class UserSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new user sessions"""
    
    class Meta:
        model = UserSession
        fields = [
            'user', 'session_type', 'subject', 'chapter_number'
        ]
    
    def create(self, validated_data):
        """Create a new session with proper initialization"""
        return UserSession.objects.create(**validated_data)


class UserQuestionHistorySerializer(serializers.ModelSerializer):
    """Serializer for user question interaction history"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_subject = serializers.CharField(source='question.subject', read_only=True)
    session_type = serializers.CharField(source='session.session_type', read_only=True)
    is_correct = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserQuestionHistory
        fields = [
            'id', 'user', 'username', 'session', 'session_type', 'question',
            'question_text', 'question_subject', 'user_answer', 'correct_answer',
            'answer_status', 'is_correct', 'question_start_time', 'question_end_time',
            'time_spent_seconds', 'question_order_in_session', 'difficulty_when_presented',
            'hints_requested', 'explanation_viewed', 'confidence_level',
            'attempt_number', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'question_start_time']


class SubmitAnswerSerializer(serializers.ModelSerializer):
    """Serializer for submitting answers to questions"""
    
    class Meta:
        model = UserQuestionHistory
        fields = [
            'session', 'question', 'user_answer', 'confidence_level',
            'hints_requested', 'explanation_viewed'
        ]
    
    def create(self, validated_data):
        """Create question history with proper calculations"""
        # Auto-populate fields
        question = validated_data['question']
        validated_data['correct_answer'] = question.answer
        validated_data['user'] = validated_data['session'].user
        validated_data['question_order_in_session'] = validated_data['session'].current_question_index + 1
        validated_data['difficulty_when_presented'] = question.difficulty_level
        validated_data['question_end_time'] = timezone.now()
        
        return super().create(validated_data)


class UserSubjectProgressSerializer(serializers.ModelSerializer):
    """Serializer for user subject progress tracking"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    overall_accuracy_percentage = serializers.FloatField(read_only=True)
    average_session_duration_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserSubjectProgress
        fields = [
            'id', 'user', 'username', 'subject', 'total_questions_attempted',
            'total_questions_correct', 'overall_accuracy_percentage', 'current_mastery_level',
            'total_study_time_seconds', 'average_time_per_question', 'total_sessions',
            'average_session_duration_minutes', 'current_correct_streak', 'longest_correct_streak',
            'current_study_streak_days', 'longest_study_streak_days', 'last_session_date',
            'last_question_answered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDailyStatsSerializer(serializers.ModelSerializer):
    """Serializer for daily user statistics"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    accuracy_percentage = serializers.FloatField(read_only=True)
    study_time_hours = serializers.FloatField(read_only=True)
    
    class Meta:
        model = UserDailyStats
        fields = [
            'id', 'user', 'username', 'date', 'total_study_time_seconds',
            'study_time_hours', 'questions_attempted', 'questions_correct',
            'accuracy_percentage', 'sessions_completed', 'subject_time_distribution',
            'subject_question_counts', 'new_topics_attempted', 'difficulty_levels_unlocked',
            'personal_bests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDashboardSerializer(serializers.Serializer):
    """Combined serializer for user dashboard data"""
    
    user_info = serializers.DictField()
    active_sessions = UserSessionSerializer(many=True)
    subject_progress = UserSubjectProgressSerializer(many=True)
    recent_activity = UserQuestionHistorySerializer(many=True)
    daily_stats = UserDailyStatsSerializer()
    overall_stats = serializers.DictField()
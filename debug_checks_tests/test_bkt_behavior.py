#!/usr/bin/env python3
"""
Test BKT Behavior - Correct vs Wrong Answers
This test shows that BKT should behave differently for correct vs wrong answers
"""
import os
import sys

# Setup Django
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adaptive_learning.settings')

import django
django.setup()

from student_model.bkt import initialize_bkt_skill, update_bkt

def test_bkt_comparison():
    """Compare BKT behavior for correct vs wrong answers"""
    print("🔬 BKT BEHAVIOR COMPARISON TEST")
    print("="*60)
    
    # Test multiple scenarios
    scenarios = [
        {"name": "Low Initial Mastery", "P_L0": 0.1},
        {"name": "Medium Initial Mastery", "P_L0": 0.5},
        {"name": "High Initial Mastery", "P_L0": 0.8}
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']} (P_L0 = {scenario['P_L0']}):")
        print("-" * 50)
        
        # Initialize with custom P_L0
        initial_params = initialize_bkt_skill("test", P_L0=scenario['P_L0'])
        print(f"   Initial Mastery: {initial_params.P_L:.6f}")
        
        # Test wrong answer
        after_wrong = update_bkt(initial_params, is_correct=False)
        wrong_change = after_wrong.P_L - initial_params.P_L
        
        # Test correct answer
        after_correct = update_bkt(initial_params, is_correct=True)
        correct_change = after_correct.P_L - initial_params.P_L
        
        print(f"   After Wrong Answer:   {after_wrong.P_L:.6f} (change: {wrong_change:+.6f})")
        print(f"   After Correct Answer: {after_correct.P_L:.6f} (change: {correct_change:+.6f})")
        
        # Analysis
        if correct_change > wrong_change:
            print(f"   ✅ CORRECT: Right answers increase mastery MORE than wrong answers")
            mastery_advantage = correct_change - wrong_change
            print(f"   📈 Mastery advantage for correct: +{mastery_advantage:.6f}")
        elif correct_change == wrong_change:
            print(f"   ⚠️ ISSUE: Right and wrong answers have same effect")
        else:
            print(f"   ❌ BUG: Wrong answers increase mastery more than right answers!")

def test_sequence_behavior():
    """Test how sequences of answers affect mastery"""
    print(f"\n\n🔄 SEQUENCE BEHAVIOR TEST")
    print("="*60)
    
    print(f"\n📉 Sequence of 5 Wrong Answers:")
    params = initialize_bkt_skill("test")
    mastery_progression = [params.P_L]
    
    for i in range(5):
        params = update_bkt(params, is_correct=False)
        mastery_progression.append(params.P_L)
        print(f"   Wrong {i+1}: {params.P_L:.6f} (change: {params.P_L - mastery_progression[-2]:+.6f})")
    
    print(f"\n📈 Sequence of 5 Correct Answers:")
    params = initialize_bkt_skill("test")
    mastery_progression = [params.P_L]
    
    for i in range(5):
        params = update_bkt(params, is_correct=True)
        mastery_progression.append(params.P_L)
        print(f"   Correct {i+1}: {params.P_L:.6f} (change: {params.P_L - mastery_progression[-2]:+.6f})")

def test_realistic_parameters():
    """Test with different BKT parameter sets"""
    print(f"\n\n⚙️ PARAMETER SENSITIVITY TEST")
    print("="*60)
    
    param_sets = [
        {"name": "Standard", "P_T": 0.3, "P_G": 0.2, "P_S": 0.1},
        {"name": "High Slip", "P_T": 0.3, "P_G": 0.2, "P_S": 0.4},  # Students make mistakes even when they know
        {"name": "Low Guess", "P_T": 0.3, "P_G": 0.05, "P_S": 0.1}, # Students rarely guess correctly
        {"name": "Conservative Learning", "P_T": 0.1, "P_G": 0.2, "P_S": 0.1}, # Lower learning rate
    ]
    
    for params in param_sets:
        print(f"\n🧪 {params['name']} Parameters:")
        print(f"   P_T={params['P_T']}, P_G={params['P_G']}, P_S={params['P_S']}")
        
        # Create BKT with custom parameters
        from student_model.bkt import BKTParameters
        bkt_params = BKTParameters(
            P_L0=0.1, P_T=params['P_T'], P_G=params['P_G'], 
            P_S=params['P_S'], P_L=0.1
        )
        
        # Test wrong vs correct
        after_wrong = update_bkt(bkt_params, is_correct=False)
        after_correct = update_bkt(bkt_params, is_correct=True)
        
        wrong_change = after_wrong.P_L - bkt_params.P_L
        correct_change = after_correct.P_L - bkt_params.P_L
        
        print(f"   Wrong change: {wrong_change:+.6f}")
        print(f"   Correct change: {correct_change:+.6f}")
        print(f"   Advantage for correct: {correct_change - wrong_change:+.6f}")

if __name__ == "__main__":
    try:
        test_bkt_comparison()
        test_sequence_behavior() 
        test_realistic_parameters()
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   • BKT should show MORE mastery gain for correct answers")
        print(f"   • Wrong answers can still increase mastery due to learning (P_T)")
        print(f"   • The key is that correct answers increase mastery MORE")
        print(f"   • For true mastery decrease with wrong answers, need negative learning")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
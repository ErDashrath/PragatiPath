#!/usr/bin/env python3
"""
Direct BKT Algorithm Test
Test the BKT update function directly to see if it's working correctly.
"""

import sys
import os

# Add the Backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)

from student_model.bkt import initialize_bkt_skill, update_bkt, BKTParameters

def test_bkt_direct():
    """Test BKT algorithm directly"""
    
    print("🧪 DIRECT BKT ALGORITHM TEST")
    print("="*60)
    
    # Initialize BKT parameters
    print("📊 Initializing BKT parameters...")
    bkt_params = initialize_bkt_skill("test_skill")
    
    print(f"Initial BKT Parameters:")
    print(f"  P_L0 (Initial Mastery): {bkt_params.P_L0:.3f}")
    print(f"  P_T (Learning Rate): {bkt_params.P_T:.3f}")
    print(f"  P_G (Guess Rate): {bkt_params.P_G:.3f}")
    print(f"  P_S (Slip Rate): {bkt_params.P_S:.3f}")
    print(f"  P_L (Current Mastery): {bkt_params.P_L:.3f}")
    
    print("\n" + "="*60)
    print("❌ TESTING WRONG ANSWERS (Should decrease mastery)")
    print("="*60)
    
    # Test sequence of wrong answers
    current_params = bkt_params
    
    for i in range(5):
        print(f"\n🔸 Wrong Answer {i+1}:")
        print(f"   Before: P_L = {current_params.P_L:.6f}")
        
        # Update with wrong answer
        updated_params = update_bkt(current_params, is_correct=False)
        
        print(f"   After:  P_L = {updated_params.P_L:.6f}")
        change = updated_params.P_L - current_params.P_L
        print(f"   Change: {change:+.6f}")
        
        if change < 0:
            print("   ✅ CORRECT: Mastery decreased")
        elif change == 0:
            print("   ⚠️ CONCERN: Mastery unchanged")
        else:
            print("   ❌ ERROR: Mastery increased!")
        
        current_params = updated_params
    
    print("\n" + "="*60)
    print("✅ TESTING CORRECT ANSWERS (Should increase mastery)")
    print("="*60)
    
    # Test sequence of correct answers
    for i in range(3):
        print(f"\n🔸 Correct Answer {i+1}:")
        print(f"   Before: P_L = {current_params.P_L:.6f}")
        
        # Update with correct answer
        updated_params = update_bkt(current_params, is_correct=True)
        
        print(f"   After:  P_L = {updated_params.P_L:.6f}")
        change = updated_params.P_L - current_params.P_L
        print(f"   Change: {change:+.6f}")
        
        if change > 0:
            print("   ✅ CORRECT: Mastery increased")
        elif change == 0:
            print("   ⚠️ CONCERN: Mastery unchanged")
        else:
            print("   ❌ ERROR: Mastery decreased!")
        
        current_params = updated_params
    
    print("\n" + "="*60)
    print("🎯 BKT DIRECT TEST SUMMARY")
    print("="*60)
    
    final_mastery = current_params.P_L
    total_change = final_mastery - bkt_params.P_L
    
    print(f"Initial Mastery: {bkt_params.P_L:.6f}")
    print(f"Final Mastery:   {final_mastery:.6f}")
    print(f"Total Change:    {total_change:+.6f}")
    
    if abs(total_change) > 0.001:  # Some change should occur
        print("✅ BKT Algorithm is responsive to answers")
    else:
        print("❌ BKT Algorithm may have issues")

def test_bkt_parameters():
    """Test different BKT parameter combinations"""
    
    print("\n\n🔬 BKT PARAMETER SENSITIVITY TEST")
    print("="*60)
    
    # Test with different parameter sets
    test_params = [
        {"name": "Default", "P_L0": 0.1, "P_T": 0.3, "P_G": 0.2, "P_S": 0.1},
        {"name": "High Slip", "P_L0": 0.1, "P_T": 0.3, "P_G": 0.2, "P_S": 0.4},
        {"name": "Low Guess", "P_L0": 0.1, "P_T": 0.3, "P_G": 0.05, "P_S": 0.1},
        {"name": "High Learning", "P_L0": 0.1, "P_T": 0.6, "P_G": 0.2, "P_S": 0.1},
    ]
    
    for params in test_params:
        print(f"\n🧪 Testing {params['name']} Parameters:")
        print(f"   P_L0={params['P_L0']}, P_T={params['P_T']}, P_G={params['P_G']}, P_S={params['P_S']}")
        
        # Create BKT parameters
        bkt_params = BKTParameters(
            P_L0=params['P_L0'],
            P_T=params['P_T'], 
            P_G=params['P_G'],
            P_S=params['P_S'],
            P_L=params['P_L0']
        )
        
        # Test one wrong answer
        before = bkt_params.P_L
        after_wrong = update_bkt(bkt_params, is_correct=False)
        change_wrong = after_wrong.P_L - before
        
        # Test one correct answer from initial state  
        after_correct = update_bkt(bkt_params, is_correct=True)
        change_correct = after_correct.P_L - before
        
        print(f"   Wrong answer change: {change_wrong:+.6f}")
        print(f"   Correct answer change: {change_correct:+.6f}")
        
        if change_wrong < 0 and change_correct > 0:
            print("   ✅ Parameters work correctly")
        elif change_wrong >= 0:
            print("   ❌ Wrong answers don't decrease mastery")
        elif change_correct <= 0:
            print("   ❌ Correct answers don't increase mastery")

if __name__ == "__main__":
    test_bkt_direct()
    test_bkt_parameters()
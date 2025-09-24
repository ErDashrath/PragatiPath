"""
Quick test to verify AI imports work
"""
try:
    print("Testing imports...")
    
    from langchain_google_genai import GoogleGenerativeAI
    print("✅ langchain_google_genai imported successfully")
    
    from langgraph.graph import Graph
    print("✅ langgraph imported successfully")
    
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
    
    print("\n🎉 All AI dependencies are working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
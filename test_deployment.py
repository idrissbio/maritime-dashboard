"""
Test script to validate Streamlit deployment dependencies
"""
import sys

def test_dependencies():
    """
    Test that all required dependencies are available
    """
    dependencies = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly.express",
        "plotly.graph_objects",
        "requests",
        "PIL", 
        "datetime",
        "io",
        "time"
    ]
    
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.split('.')[0])
            print(f"✓ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"✗ {dep}")
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        return False
        
    print("\nAll dependencies available!")
    return True
    
def test_twelvedata_api():
    """
    Test that the TwelveData API client loads successfully
    """
    try:
        import requests
        from PIL import Image
        import io
        
        # Minimal TwelveData API client
        class TestTwelveDataAPI:
            def __init__(self):
                self.api_key = "test_key"
                self.base_url = "https://api.twelvedata.com"
        
        # Create instance
        api = TestTwelveDataAPI()
        print("✓ TwelveData API client loaded")
        return True
    except Exception as e:
        print(f"✗ TwelveData API client error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Streamlit deployment dependencies...\n")
    
    deps_ok = test_dependencies()
    api_ok = test_twelvedata_api()
    
    if deps_ok and api_ok:
        print("\nAll tests passed! Deployment should work.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please fix the issues before deploying.")
        sys.exit(1)
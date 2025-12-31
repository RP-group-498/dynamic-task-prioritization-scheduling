"""
API Test Client
Test the Flask API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{{BASE_URL}}/health")
    print(f"Status: {{response.status_code}}")
    print(f"Response: {{response.json()}}")
    print()

def test_predict():
    """Test single prediction"""
    print("Testing /predict...")
    
    data = {{
        "subtask": "Create login page in React",
        "user_id": "student_123",
        "difficulty": 3
    }}
    
    response = requests.post(
        f"{{BASE_URL}}/predict",
        json=data
    )
    
    print(f"Status: {{response.status_code}}")
    result = response.json()
    print(f"Predicted time: {{result['predicted_time']}} minutes")
    print(f"Method: {{result['method']}}")
    print(f"Confidence: {{result['confidence']}}")
    print()

def test_batch_predict():
    """Test batch prediction"""
    print("Testing /predict-batch...")
    
    data = {{
        "user_id": "student_123",
        "main_task": {{
            "name": "Database Homework",
            "difficulty": 3
        }},
        "subtasks": [
            "Find all users with age > 25",
            "Sort records by name",
            "Count active users"
        ]
    }}
    
    response = requests.post(
        f"{{BASE_URL}}/predict-batch",
        json=data
    )
    
    print(f"Status: {{response.status_code}}")
    result = response.json()
    print(f"Total time: {{result['total_time']}} minutes")
    print(f"Task count: {{result['task_count']}}")
    print(f"Average: {{result['average_time']:.1f}} minutes")
    print()

if __name__ == "__main__":
    print("="*60)
    print("API Test Client")
    print("="*60)
    print("\nMake sure API is running at http://localhost:5000\n")
    print("="*60 + "\n")
    
    try:
        test_health()
        test_predict()
        test_batch_predict()
        
        print("="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        print("Make sure to run: python api.py")

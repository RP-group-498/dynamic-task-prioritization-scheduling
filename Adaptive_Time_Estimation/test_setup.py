import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'exports')

from adaptive_time_estimator import AdaptiveTimeEstimator

# Initialize
print("Initializing Adaptive Time Estimator...")
estimator = AdaptiveTimeEstimator(
    env_path='config/.env',
    model_path='models/sbert_model'
)

# Make prediction
print("\nMaking a test prediction...")
prediction = estimator.predict_time(
    subtask_text="Create login page in React",
    user_id="test_student_123",
    difficulty=3
)

# Display result
print("\n" + "="*50)
print("TEST RESULTS")
print("="*50)
print(f"Task: Create login page in React")
print(f"Predicted time: {prediction['predicted_time']} minutes")
print(f"Method: {prediction['method']}")
print(f"Confidence: {prediction['confidence']}")
print(f"Similar tasks found: {len(prediction.get('similar_tasks', []))}")
print("="*50)
print("\nSetup completed successfully!")

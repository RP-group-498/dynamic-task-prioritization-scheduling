# Adaptive Time Estimation - Local Setup Guide

## 📦 What You Need

This guide will help you use the Adaptive Time Estimation model on your local computer.

**Requirements:**
- Python 3.8 or higher
- Internet connection (for MongoDB)
- ~500MB disk space

---

## 🚀 Step-by-Step Setup

### Step 1: Download Files from Google Drive

1. Open Google Drive in your browser
2. Navigate to: `Adaptive_Time_Estimation/exports/`
3. Download these files:
   - `adaptive_time_estimator.py`
   - `requirements.txt`
   - `.env`
4. Also download: `Adaptive_Time_Estimation/models/` (entire folder)

### Step 2: Create Project Folder

Open terminal/command prompt:
```bash
# Create project folder
mkdir my-time-estimator
cd my-time-estimator

# Create folders
mkdir models
mkdir config
```

### Step 3: Copy Downloaded Files

Place files in your project:
```
my-time-estimator/
├── adaptive_time_estimator.py  (from exports/)
├── requirements.txt            (from exports/)
├── config/
│   └── .env                    (from exports/)
└── models/
    └── sbert_model/            (entire folder from Drive)
```

### Step 4: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- pymongo (MongoDB connection)
- sentence-transformers (SBERT)
- numpy, scikit-learn (ML tools)
- python-dotenv (Environment variables)

### Step 6: Configure MongoDB URL

1. Open `config/.env` in text editor
2. Update MongoDB URL if needed:
```
MONGODB_URI=mongodb+srv://YOUR_USER:YOUR_PASS@YOUR_CLUSTER.mongodb.net/
```

### Step 7: Test the Setup

Create `test.py`:
```python
from adaptive_time_estimator import AdaptiveTimeEstimator

# Initialize
estimator = AdaptiveTimeEstimator(
    env_path='config/.env',
    model_path='models/sbert_model'
)

# Make prediction
prediction = estimator.predict_time(
    subtask_text="Create login page in React",
    user_id="student_123",
    difficulty=3
)

# Display result
print(f"Predicted time: {{prediction['predicted_time']}} minutes")
print(f"Method: {{prediction['method']}}")
print(f"Confidence: {{prediction['confidence']}}")
```

Run it:
```bash
python test.py
```

Expected output:
```
🚀 Initializing Adaptive Time Estimator...
   Loading SBERT model...
✅ Estimator ready!

Predicted time: 14 minutes
Method: warm_start
Confidence: HIGH
```

---

## 💻 Using in Your Application

### Basic Usage
```python
from adaptive_time_estimator import AdaptiveTimeEstimator

# Initialize once
estimator = AdaptiveTimeEstimator('config/.env', 'models/sbert_model')

# Predict time for a task
prediction = estimator.predict_time(
    subtask_text="Sort database records by date",
    user_id="student_123",
    difficulty=2
)

print(f"Estimated: {{prediction['predicted_time']}} minutes")
```

### Process Multiple Subtasks
```python
main_task = {{
    "task_name": "Database Homework",
    "metrics": {{"difficulty_rating": 3}}
}}

subtasks = [
    "Find all users with age > 25",
    "Join users with orders table",
    "Calculate total sales"
]

predictions = []

for i, subtask in enumerate(subtasks, 1):
    pred = estimator.predict_time(subtask, "student_123", 3)
    pred['subtask_number'] = i
    pred['subtask_text'] = subtask
    predictions.append(pred)
    
    print(f"Subtask {{i}}: {{pred['predicted_time']}} min")

# Save to database
estimator.save_task(main_task, predictions, "student_123")
```

### Mark Task Complete (Important for Learning!)
```python
# After you finish the task
estimator.mark_complete(
    subtask_desc="Find all users with age > 25",
    user_id="student_123",
    actual_time=12  # How long it actually took
)
```

### Check Model Accuracy
```python
accuracy = estimator.get_accuracy("student_123")

if accuracy:
    print(f"Average error: {{accuracy['mae']:.1f}} minutes")
    print(f"Accuracy (±5 min): {{accuracy['accuracy_5min']:.1f}}%")
    print(f"Based on {{accuracy['training_size']}} tasks")
```

---

## 🔧 Troubleshooting

### Error: "No module named 'sentence_transformers'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Error: "Connection refused" or "MongoDB connection failed"

**Solution:** Check MongoDB URL
1. Open `config/.env`
2. Verify `MONGODB_URI` is correct
3. Check internet connection
4. Ensure MongoDB cluster is running

### Error: "Model not found"

**Solution:** Check model path
```python
# Make sure path is correct
estimator = AdaptiveTimeEstimator(
    env_path='config/.env',
    model_path='models/sbert_model'  # Check this path exists
)
```

### SBERT Downloads Slowly

**Solution:** First run downloads model (~80MB)
- Be patient, it's one-time
- Next runs will be instant
- Model cached locally

---

## 🌐 Creating a Web API (Optional)

Create `app.py`:
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from adaptive_time_estimator import AdaptiveTimeEstimator

app = Flask(__name__)
CORS(app)

# Initialize estimator
estimator = AdaptiveTimeEstimator('config/.env', 'models/sbert_model')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    prediction = estimator.predict_time(
        data['subtask'],
        data['user_id'],
        data['difficulty']
    )
    
    return jsonify(prediction)

@app.route('/complete', methods=['POST'])
def complete():
    data = request.json
    
    estimator.mark_complete(
        data['subtask'],
        data['user_id'],
        data['actual_time']
    )
    
    return jsonify({{"status": "completed"}})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Install Flask:
```bash
pip install flask flask-cors
```

Run API:
```bash
python app.py
```

Test it:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{{"subtask": "Create login page", "user_id": "student_123", "difficulty": 3}}'
```

---

## 📊 Understanding the Output

### Warm Start (Using History)
```python
{{
    'method': 'warm_start',
    'predicted_time': 14,
    'confidence': 'HIGH',
    'similar_tasks': [
        {{'similarity': 0.89, 'actual_time': 12}},
        {{'similarity': 0.85, 'actual_time': 15}}
    ]
}}
```

**Meaning:**
- Found similar tasks in your history
- Average of those tasks: 14 minutes
- High confidence (reliable prediction)

### Cold Start (No History)
```python
{{
    'method': 'cold_start',
    'predicted_time': 20,
    'confidence': 'LOW',
    'similar_tasks': []
}}
```

**Meaning:**
- No similar tasks found
- Using difficulty level (3 → 20 minutes)
- Low confidence (may be inaccurate)

---

## 🎯 Best Practices

1. **Always mark tasks complete** - This is how the model learns!
2. **Use realistic difficulty levels** - Be honest about task complexity
3. **Start with 20-30 tasks** - Model needs data to learn
4. **Review predictions** - Adjust if you know better
5. **Complete tasks promptly** - Don't let scheduled tasks pile up

---

## 🆘 Getting Help

If you're stuck:

1. Check this guide again
2. Verify all files are in correct locations
3. Check MongoDB connection
4. Ensure Python version is 3.8+

Common issues are usually:
- Wrong file paths
- MongoDB URL incorrect
- Missing dependencies

---

## 📈 Model Improvement

The model gets better as you use it:

**Week 1:** Mostly cold start, ~70% accuracy
**Week 2:** Mix of warm/cold, ~80% accuracy  
**Week 4:** Mostly warm start, ~90% accuracy

Keep completing tasks and marking them done!

---

## 🎓 Summary

1. Download files from Google Drive
2. Install Python dependencies
3. Configure MongoDB URL
4. Initialize estimator
5. Make predictions
6. Mark tasks complete
7. Watch accuracy improve!

**You're now ready to use Adaptive Time Estimation!** 🚀

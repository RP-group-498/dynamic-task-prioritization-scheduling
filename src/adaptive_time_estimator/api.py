"""
Adaptive Time Estimation API
Web API for making predictions

Run with: python api.py
Access at: http://localhost:5000
"""

import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, request, jsonify
from flask_cors import CORS
from adaptive_time_estimator import AdaptiveTimeEstimator
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize estimator (loads once at startup)
print("Initializing model...")
estimator = AdaptiveTimeEstimator('.env', 'models/sbert_model')
print("Model ready!")


@app.route('/', methods=['GET'])
def home():
    """API information endpoint"""
    return jsonify({
        "name": "Adaptive Time Estimation API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "POST /predict": "Get time prediction for a task",
            "POST /predict-batch": "Predict multiple tasks at once",
            "POST /complete": "Mark task as complete",
            "GET /accuracy/<user_id>": "Get model accuracy for user",
            "GET /tasks/<user_id>": "Get all tasks for a user",
            "POST /save-tasks": "Save tasks to database",
            "GET /health": "Check API health"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict time for a single task
    
    Request body:
    {
        "subtask": "Create login page",
        "user_id": "student_123",
        "difficulty": 3
    }
    
    Response:
    {
        "method": "warm_start",
        "predicted_time": 14,
        "confidence": "HIGH",
        "explanation": "Based on 5 similar tasks"
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data.get('subtask'):
            return jsonify({"error": "Missing 'subtask' field"}), 400
        if not data.get('user_id'):
            return jsonify({"error": "Missing 'user_id' field"}), 400
        if not data.get('difficulty'):
            return jsonify({"error": "Missing 'difficulty' field"}), 400
        
        # Make prediction
        prediction = estimator.predict_time(
            data['subtask'],
            data['user_id'],
            ai_suggested_time=None # Pass None for ai_suggested_time as it's not provided for single predictions
        )
        
        # Add timestamp
        prediction['timestamp'] = datetime.now().isoformat()
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """
    Predict time for multiple tasks
    
    Request body:
    {
        "user_id": "student_123",
        "main_task": {
            "name": "Database Homework",
            "difficulty": 3
        },
        "subtasks": [
            "Find all users",
            "Sort by name",
            "Count records"
        ]
    }
    
    Response:
    {
        "predictions": [...],
        "total_time": 45,
        "task_count": 3
    }
    """
    try:
        data = request.json
        
        user_id = data.get('user_id')
        main_task = data.get('main_task')
        subtasks = data.get('subtasks', [])
        difficulty = main_task.get('difficulty', 3)
        
        predictions = []
        total_time = 0
        
        for i, subtask_data in enumerate(subtasks, 1):
            subtask_text = subtask_data.get('name')
            ai_suggested_time = subtask_data.get('ai_suggested_time')
            
            if not subtask_text:
                continue

            pred = estimator.predict_time(subtask_text, user_id, ai_suggested_time)
            pred['subtask_number'] = i
            pred['subtask_text'] = subtask_text
            predictions.append(pred)
            total_time += pred.get('predicted_time', 0)
        
        return jsonify({
            "predictions": predictions,
            "total_time": total_time,
            "task_count": len(subtasks),
            "average_time": total_time / len(subtasks) if subtasks else 0,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/complete', methods=['POST'])
def complete():
    """
    Mark task as complete
    
    Request body:
    {
        "subtask": "Create login page",
        "user_id": "student_123",
        "actual_time": 15
    }
    
    Response:
    {
        "status": "completed",
        "message": "Task marked as complete"
    }
    """
    try:
        data = request.json
        
        estimator.mark_complete(
            data['subtask'],
            data['user_id'],
            data['actual_time']
        )
        
        return jsonify({
            "status": "completed",
            "message": "Task marked as complete and model updated",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/accuracy/<user_id>', methods=['GET'])
def get_accuracy(user_id):
    """
    Get model accuracy for a specific user
    
    Response:
    {
        "mae": 3.5,
        "accuracy_5min": 85.0,
        "training_size": 30
    }
    """
    try:
        accuracy = estimator.get_accuracy(user_id)
        
        if accuracy:
            return jsonify(accuracy)
        else:
            return jsonify({
                "message": "No training data found for this user"
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/save-tasks', methods=['POST'])
def save_tasks():
    """
    Save multiple tasks to database

    Request body:
    {
        "user_id": "student_123",
        "main_task": {...},
        "predictions": [...]
    }
    """
    try:
        data = request.json

        estimator.save_task(
            data['main_task'],
            data['predictions'],
            data['user_id']
        )

        return jsonify({
            "status": "saved",
            "task_count": len(data['predictions']),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<user_id>', methods=['GET'])
def get_user_tasks(user_id):
    """
    Get all tasks for a specific user

    Query parameters:
        status: Filter by status (scheduled, in_progress, completed) - optional
        limit: Maximum number of tasks to return - optional (default: all)

    Response:
    {
        "user_id": "student_123",
        "tasks": [
            {
                "task_id": "...",
                "main_task": {
                    "name": "Database Homework",
                    "difficulty": 3
                },
                "subtask": "Create login page",
                "predicted_time": 14,
                "actual_time": null,
                "status": "scheduled",
                "created_date": "2025-01-01T12:00:00",
                "confidence": "HIGH",
                "method": "warm_start"
            }
        ],
        "task_count": 5,
        "total_estimated_time": 120
    }
    """
    try:
        # Get query parameters
        status_filter = request.args.get('status')
        limit = request.args.get('limit', type=int)

        # Build query
        query = {"user_id": user_id}
        if status_filter:
            query["status"] = status_filter

        # Fetch tasks from database
        tasks_cursor = estimator.tasks.find(query).sort("created_date", -1)

        if limit:
            tasks_cursor = tasks_cursor.limit(limit)

        tasks = list(tasks_cursor)

        # Format response
        formatted_tasks = []
        total_estimated_time = 0

        for task in tasks:
            estimates = task.get('estimates', {})
            sub_task = task.get('sub_task', {})

            # Handle time_allocation_date
            time_alloc = task.get('time_allocation_date')
            time_allocation_str = None
            if time_alloc:
                if isinstance(time_alloc, datetime):
                    time_allocation_str = time_alloc.isoformat()
                else:
                    time_allocation_str = time_alloc

            formatted_task = {
                "task_id": str(task['_id']),
                "main_task": task.get('main_task', {}),
                "subtask": sub_task.get('description', 'Unknown'),
                "subtask_position": sub_task.get('position', 1),
                "category": sub_task.get('category', 'general'),
                "predicted_time": estimates.get('system_estimate', 0),
                "user_estimate": estimates.get('user_estimate'),
                "actual_time": estimates.get('actual_time'),
                "confidence": estimates.get('confidence', 'UNKNOWN'),
                "method": estimates.get('prediction_method', 'unknown'),
                "status": task.get('status', 'scheduled'),
                "created_date": task.get('created_date', datetime.now()).isoformat(),
                "completed_date": task.get('completed_date', '').isoformat() if task.get('completed_date') else None,
                "time_allocation_date": time_allocation_str
            }
            formatted_tasks.append(formatted_task)

            # Only count incomplete tasks
            if task.get('status') != 'completed':
                total_estimated_time += estimates.get('system_estimate', 0)

        return jsonify({
            "user_id": user_id,
            "tasks": formatted_tasks,
            "task_count": len(formatted_tasks),
            "total_estimated_time": total_estimated_time,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Adaptive Time Estimation API")
    print("="*60)
    print("\nAPI running at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /              - API info")
    print("  GET  /health        - Health check")
    print("  POST /predict       - Single prediction")
    print("  POST /predict-batch - Multiple predictions")
    print("  POST /complete      - Mark task complete")
    print("  GET  /accuracy/<id> - Get accuracy")
    print("  GET  /tasks/<id>    - Get all user tasks")
    print("  POST /save-tasks    - Save tasks")
    print("\n" + "="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)

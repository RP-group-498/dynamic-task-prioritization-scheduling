# 🕒 Active Time Sync Scheduler

This dedicated background service is responsible for performing daily synchronization tasks at **07:00 AM**.

## 🚀 Purpose
It fetches active study time predictions from the **Adaptive Time Estimation API** (`http://localhost:5000`) for specific users (`user_003` and `user_001`). This ensures the latest study window data is always available for task allocation.

## 🛠️ Setup & Running

1. **Prerequisites**: Ensure the main Flask API is running (use `python src/adaptive_time_estimator/api.py`).
2. **Setup**: Run `setup_service.bat` (Windows) or `bash setup_service.sh` (Linux/Mac).
3. **Run**: 
   ```bash
   cd services/scheduler
   python active_time_sync.py
   ```

## 📂 Structure
- `active_time_sync.py`: The core scheduling logic (runs every day at 07:00 AM).
- `scheduler.log`: Detailed history of all sync attempts (created on first run).
- `requirements.txt`: Python dependencies (`schedule`, `requests`).
- `setup_service.bat`: Automated environment setup for Windows.

## ⚙️ Configuration
The service connects to:
- **API URL**: `http://localhost:5000` (defaults from `.env` or script fallback)
- **Users**: `user_003`, `user_001` (can be updated in `active_time_sync.py`)
- **Daily Time**: `07:00` (can be updated in `active_time_sync.py`)

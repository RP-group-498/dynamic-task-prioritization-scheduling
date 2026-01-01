# Quick Start Guide - MCDM Task Priority System

## Overview

This project now has a desktop application frontend built with Electron.js that provides two main interfaces:

1. **PDF Analysis Interface** - Upload PDFs and analyze tasks with MCDM scoring
2. **Adaptive Time Estimator** - Calendar view with todo list and time tracking

## Setup Instructions

### 1. Backend Setup (Python)

First, ensure the Python backend is set up:

```bash
# From project root
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and MONGODB_URI
```

### 2. Frontend Setup (Electron)

```bash
# Navigate to frontend directory
cd frontend

# Windows
setup.bat

# Linux/Mac
./setup.sh

# Or manually
npm install
```

## Running the Application

### Start the Desktop App

```bash
cd frontend
npm start
```

For development mode with DevTools:
```bash
npm run dev
```

### Using the Application

#### PDF Analysis Interface (Default Page)

1. **Upload PDF**:
   - Click "Browse Files" or drag-drop your assignment PDF
   - File info will appear once selected

2. **Enter Details**:
   - Deadline: Select due date from calendar
   - Credits: Enter 1-4
   - Weight: Enter 0-100 (percentage)

3. **Analyze**:
   - Click "Analyze Task"
   - Wait for processing
   - View results with:
     - Task name and priority
     - MCDM scores (Urgency, Impact, Difficulty)
     - Subtasks breakdown
     - Task description

#### Time Estimator Interface

1. **Navigate**:
   - Click "Time Estimator" in the top navigation

2. **View Calendar**:
   - Use ◁ ▷ buttons to navigate months
   - Today is highlighted
   - Days with tasks show a dot indicator

3. **Add Tasks**:
   - Fill in task name
   - Select deadline date
   - Choose priority (High/Medium/Low)
   - Add description (optional)
   - Click "Add Task"

4. **Manage Tasks**:
   - Filter by: All / High / Medium / Low
   - View task details and deadlines
   - Delete tasks using "Delete" button
   - See statistics in cards

5. **Monitor Time**:
   - Total estimated time for next 7 days
   - Workload percentage bar
   - Task count by priority

## Project Structure

```
research-text-extraction/
├── frontend/                    # Electron.js desktop app
│   ├── main.js                 # Main process
│   ├── package.json            # Dependencies
│   ├── setup.bat               # Windows setup
│   ├── setup.sh                # Linux/Mac setup
│   └── src/
│       ├── pages/              # HTML pages
│       │   ├── pdf-analysis.html
│       │   └── time-estimator.html
│       └── assets/
│           ├── css/            # Stylesheets
│           └── js/             # JavaScript logic
│
├── src/                        # Python backend
│   ├── dynamic_task_prioritization/
│   └── adaptive_time_estimator/
│
├── data/                       # Data files
│   ├── raw/                    # Input PDFs
│   └── outputs/                # JSON results
│
├── main.py                     # Python entry point
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

## Features

### PDF Analysis
- ✅ Drag-and-drop PDF upload
- ✅ AI-powered text extraction (Google Gemini)
- ✅ MCDM priority calculation
- ✅ Visual score breakdown
- ✅ Subtask extraction
- ✅ Priority labeling

### Time Estimator
- ✅ Interactive calendar
- ✅ Todo list with filtering
- ✅ Task statistics dashboard
- ✅ Time estimation
- ✅ Workload tracking
- ✅ Add/delete tasks

## Keyboard Shortcuts

- `Ctrl+Shift+I` (Windows/Linux) - Open DevTools
- `Cmd+Option+I` (Mac) - Open DevTools
- `Ctrl+R` (Windows/Linux) - Reload
- `Cmd+R` (Mac) - Reload

## Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

### Backend connection issues
- Check `.env` file has valid API keys
- Ensure Python virtual environment is activated
- Verify MongoDB connection string

### PDF analysis fails
- Confirm GEMINI_API_KEY is valid
- Check PDF file is readable
- Ensure Python backend is accessible

## Next Steps

1. Test PDF analysis with sample assignments
2. Add tasks manually in Time Estimator
3. Customize colors in `frontend/src/assets/css/styles.css`
4. Configure MCDM weights in `src/dynamic_task_prioritization/config.py`

## Support

- Frontend README: `frontend/README.md`
- Backend README: `README.md`
- Check console logs for errors (F12 in app)

---

**Enjoy managing your academic tasks efficiently!** 🚀

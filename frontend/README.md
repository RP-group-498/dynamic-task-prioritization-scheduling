# MCDM Task Priority System - Electron Frontend

A modern desktop application built with Electron.js for the MCDM Task Priority Analysis System.

## Features

### 1. PDF Analysis Interface
- Drag-and-drop PDF upload
- Task details input (deadline, credits, weight)
- Real-time MCDM score calculation
- Visual score breakdown with progress bars
- Subtask display
- Priority labeling (High/Medium/Low)

### 2. Adaptive Time Estimator Interface
- Interactive calendar view with task markers
- Todo list with filtering (All/High/Medium/Low priority)
- Task statistics dashboard
- Time estimation and workload tracking
- Add/delete tasks functionality

## Project Structure

```
frontend/
├── main.js                          # Electron main process
├── package.json                     # Dependencies and scripts
├── README.md                        # This file
│
└── src/
    ├── pages/                       # HTML pages
    │   ├── pdf-analysis.html       # PDF analysis interface
    │   └── time-estimator.html     # Time estimator interface
    │
    └── assets/
        ├── css/                     # Stylesheets
        │   ├── styles.css          # Global styles
        │   ├── pdf-analysis.css    # PDF analysis styles
        │   └── time-estimator.css  # Time estimator styles
        │
        └── js/                      # JavaScript files
            ├── pdf-analysis.js     # PDF analysis logic
            └── time-estimator.js   # Time estimator logic
```

## Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Python backend must be set up (see main README.md)

### Setup Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## Usage

### Run the Application

```bash
npm start
```

Or in development mode with DevTools:
```bash
npm run dev
```

### Using the PDF Analysis Interface

1. **Upload PDF**:
   - Click "Browse Files" or drag and drop your PDF
   - Supported format: PDF only

2. **Enter Task Details**:
   - Deadline: Select assignment due date
   - Credits: Enter module credits (1-4)
   - Weight: Enter assignment weight percentage (0-100)

3. **Analyze**:
   - Click "Analyze Task" button
   - Wait for AI processing
   - View results with MCDM scores

### Using the Time Estimator Interface

1. **View Calendar**:
   - Navigate months using arrow buttons
   - Days with tasks are marked with a dot
   - Today's date is highlighted

2. **Add Tasks**:
   - Fill in task name and deadline
   - Select priority level
   - Optionally add description
   - Click "Add Task"

3. **Manage Tasks**:
   - Filter tasks by priority
   - View task details and deadlines
   - Delete tasks as needed
   - Monitor workload percentage

4. **View Statistics**:
   - See task count by priority
   - Track total estimated time
   - Monitor workload for next 7 days

## IPC Communication

The frontend communicates with the Python backend through Electron's IPC (Inter-Process Communication):

### Available IPC Channels

- `analyze-pdf`: Send PDF and task details for analysis
- `estimate-time`: Get time estimation for tasks
- `fetch-tasks`: Retrieve saved tasks from MongoDB
- `navigate`: Navigate between pages

## Customization

### Changing Colors

Edit `src/assets/css/styles.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
    --danger-color: #f44336;
    /* etc. */
}
```

### Adding New Pages

1. Create HTML file in `src/pages/`
2. Create corresponding CSS in `src/assets/css/`
3. Create JavaScript in `src/assets/js/`
4. Add navigation link in navbar
5. Update `main.js` if needed

## Technology Stack

- **Electron**: Desktop application framework
- **HTML5/CSS3**: User interface
- **JavaScript (ES6+)**: Application logic
- **Node.js**: Runtime environment
- **IPC**: Backend communication

## Troubleshooting

### Application won't start
- Ensure Node.js is installed: `node --version`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check if ports are available

### PDF analysis fails
- Verify Python backend is running
- Check if .env file has GEMINI_API_KEY
- Ensure PDF file is valid and readable

### Tasks not loading
- Check MongoDB connection in backend
- Verify output JSON file exists in `data/outputs/`
- Check console for error messages

### Navigation not working
- Clear Electron cache
- Restart the application
- Check browser console (F12 in dev mode)

## Development

### Enable Developer Tools

Run with the `--dev` flag:
```bash
npm run dev
```

Or press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) when app is running.

### Debugging

- Use `console.log()` in renderer JavaScript
- Check main process logs in terminal
- Use Chrome DevTools for debugging

## Building for Production

To package the application for distribution:

```bash
npm install electron-builder --save-dev
```

Add to `package.json`:
```json
"build": {
  "appId": "com.mcdm.taskpriority",
  "productName": "MCDM Task Priority",
  "directories": {
    "output": "dist"
  },
  "win": {
    "target": "nsis"
  },
  "mac": {
    "target": "dmg"
  },
  "linux": {
    "target": "AppImage"
  }
}
```

Build:
```bash
npx electron-builder
```

## Future Enhancements

- [ ] Add task completion tracking
- [ ] Export tasks to calendar formats (iCal, Google Calendar)
- [ ] Dark/Light theme toggle
- [ ] Notification system for upcoming deadlines
- [ ] Task notes and attachments
- [ ] Time tracking integration
- [ ] Multiple PDF batch processing
- [ ] Custom MCDM weight configuration

## License

[Add your license here]

## Support

For issues and questions:
- Check the main project README.md
- Review troubleshooting section above
- Check console logs for errors

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'src/assets/icon.png')
  });

  // Load the PDF Analysis page by default
  mainWindow.loadFile('src/pages/pdf-analysis.html');

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', function () {
    mainWindow = null;
    // Kill Python process when window closes
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC Handlers for Python Backend Communication

// Handle PDF Analysis Request
ipcMain.handle('analyze-pdf', async (event, data) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../main.py');
    const pythonExe = process.platform === 'win32'
      ? path.join(__dirname, '../venv/Scripts/python.exe')
      : path.join(__dirname, '../venv/bin/python');

    // Create input file for Python script
    const fs = require('fs');
    const inputData = {
      pdf_path: data.pdfPath,
      deadline: data.deadline,
      credits: data.credits,
      weight: data.weight
    };

    const tempInputFile = path.join(__dirname, '../temp_input.json');
    fs.writeFileSync(tempInputFile, JSON.stringify(inputData));

    // Spawn Python process
    pythonProcess = spawn(pythonExe, [pythonScript, '--input', tempInputFile]);

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
      pythonProcess = null;
      // Clean up temp file
      if (fs.existsSync(tempInputFile)) {
        fs.unlinkSync(tempInputFile);
      }

      if (code === 0) {
        try {
          // Read the output JSON file
          const outputFile = path.join(__dirname, '../data/outputs/mcdm_output.json');
          const result = JSON.parse(fs.readFileSync(outputFile, 'utf8'));
          resolve(result);
        } catch (error) {
          reject({ error: 'Failed to parse output', details: error.message });
        }
      } else {
        reject({ error: 'Python script failed', code, stderr: errorData });
      }
    });
  });
});

// Handle Time Estimation Request
ipcMain.handle('estimate-time', async (event, taskData) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../src/adaptive_time_estimator/api.py');
    const pythonExe = process.platform === 'win32'
      ? path.join(__dirname, '../venv/Scripts/python.exe')
      : path.join(__dirname, '../venv/bin/python');

    // For now, return mock data - you'll integrate with actual API later
    resolve({
      estimated_time: 120,
      confidence: 0.85,
      task_name: taskData.taskName
    });
  });
});

// Handle fetching tasks from MongoDB
ipcMain.handle('fetch-tasks', async (event) => {
  return new Promise((resolve, reject) => {
    const fs = require('fs');
    const outputFile = path.join(__dirname, '../data/outputs/mcdm_output.json');

    try {
      if (fs.existsSync(outputFile)) {
        const data = JSON.parse(fs.readFileSync(outputFile, 'utf8'));
        resolve(data.tasks || []);
      } else {
        resolve([]);
      }
    } catch (error) {
      reject({ error: 'Failed to fetch tasks', details: error.message });
    }
  });
});

// Navigation between pages
ipcMain.on('navigate', (event, page) => {
  const pagePath = path.join(__dirname, `src/pages/${page}.html`);
  mainWindow.loadFile(pagePath);
});

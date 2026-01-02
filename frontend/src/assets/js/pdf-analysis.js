const { ipcRenderer } = require('electron');
const path = require('path');

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const pdfInput = document.getElementById('pdfInput');
const browseBtn = document.getElementById('browseBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFileBtn');
const taskDetailsForm = document.getElementById('taskDetailsForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeText = document.getElementById('analyzeText');
const analyzeSpinner = document.getElementById('analyzeSpinner');
const resultsCard = document.getElementById('resultsCard');

let selectedFile = null;

// Format time in minutes to human-readable format
function formatTime(minutes) {
    if (minutes === 0 || !minutes) {
        return "0 minutes";
    }

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours > 0 && mins > 0) {
        const hourStr = hours === 1 ? "hour" : "hours";
        const minStr = mins === 1 ? "minute" : "minutes";
        return `${hours} ${hourStr} ${mins} ${minStr}`;
    } else if (hours > 0) {
        const hourStr = hours === 1 ? "hour" : "hours";
        return `${hours} ${hourStr}`;
    } else {
        const minStr = mins === 1 ? "minute" : "minutes";
        return `${mins} ${minStr}`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupNavigation();
    setMinDate();
});

// Set minimum date to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('deadline').setAttribute('min', today);
}

// Setup Navigation
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.getAttribute('data-page');
            ipcRenderer.send('navigate', page);
        });
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Browse button
    browseBtn.addEventListener('click', () => {
        pdfInput.click();
    });

    // File input change
    pdfInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // Upload area click
    uploadArea.addEventListener('click', () => {
        pdfInput.click();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handleFileSelect(file);
        } else {
            showNotification('Please select a valid PDF file', 'error');
        }
    });

    // Remove file button
    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFileSelection();
    });

    // Form submission
    taskDetailsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await analyzeTask();
    });
}

// Handle file selection
function handleFileSelect(file) {
    if (!file) return;

    if (file.type !== 'application/pdf') {
        showNotification('Please select a PDF file', 'error');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'flex';
}

// Clear file selection
function clearFileSelection() {
    selectedFile = null;
    pdfInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
}

// Analyze task
async function analyzeTask() {
    if (!selectedFile) {
        showNotification('Please select a PDF file', 'error');
        return;
    }

    const deadline = document.getElementById('deadline').value;
    const credits = parseInt(document.getElementById('credits').value);
    const weight = parseInt(document.getElementById('weight').value);

    // Validate inputs
    if (!deadline || !credits || !weight) {
        showNotification('Please fill in all fields', 'error');
        return;
    }

    if (credits < 1 || credits > 4) {
        showNotification('Credits must be between 1 and 4', 'error');
        return;
    }

    if (weight < 0 || weight > 100) {
        showNotification('Weight must be between 0 and 100', 'error');
        return;
    }

    // Show loading state
    setLoadingState(true);
    resultsCard.style.display = 'none';

    try {
        const result = await ipcRenderer.invoke('analyze-pdf', {
            pdfPath: selectedFile.path,
            deadline: deadline,
            credits: credits,
            weight: weight
        });

        if (result && result.tasks && result.tasks.length > 0) {
            displayResults(result.tasks[0]);
            showNotification('Analysis completed successfully!', 'success');
        } else {
            throw new Error('No results returned from analysis');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Failed to analyze PDF. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
}

// Display results
function displayResults(task) {
    // Task Information
    document.getElementById('resultTaskName').textContent = task.task_name || 'N/A';
    document.getElementById('resultDaysLeft').textContent = task.metrics.days_left + ' days';
    document.getElementById('resultDifficulty').textContent = task.metrics.difficulty_rating + '/5';

    // Priority badge
    const priorityElement = document.getElementById('resultPriority');
    priorityElement.textContent = task.priority;
    priorityElement.className = 'info-value priority-badge ' + task.priority;

    // MCDM Scores
    const urgencyScore = task.mcdm_calculation.urgency_score;
    const impactScore = task.mcdm_calculation.impact_score;
    const difficultyScore = task.mcdm_calculation.difficulty_score;
    const finalScore = task.mcdm_calculation.final_weighted_score;

    document.getElementById('urgencyScore').textContent = urgencyScore;
    document.getElementById('urgencyBar').style.width = urgencyScore + '%';

    document.getElementById('impactScore').textContent = impactScore;
    document.getElementById('impactBar').style.width = impactScore + '%';

    document.getElementById('difficultyScore').textContent = difficultyScore;
    document.getElementById('difficultyBar').style.width = difficultyScore + '%';

    document.getElementById('finalScore').textContent = finalScore.toFixed(1);

    // Subtasks
    const subtasksList = document.getElementById('subtasksList');
    subtasksList.innerHTML = '';

    if (task.sub_tasks && task.sub_tasks.length > 0) {
        let totalSubtaskMinutes = 0;
        task.sub_tasks.forEach(subtask => {
            const li = document.createElement('li');

            // Handle new format (object with name and estimated_minutes)
            if (typeof subtask === 'object' && subtask.name) {
                // Support both new (estimated_minutes) and old (estimated_hours) formats
                let minutes = subtask.estimated_minutes;
                if (minutes === undefined || minutes === null) {
                    // Fallback to old format (hours) and convert to minutes
                    const hours = subtask.estimated_hours || 0;
                    minutes = hours * 60;
                }
                totalSubtaskMinutes += minutes;
                const timeStr = formatTime(minutes);
                li.innerHTML = `<strong>${subtask.name}</strong> <span style="color: #7c3aed; font-weight: 600;">(${timeStr})</span>`;
            } else {
                // Handle old format (plain strings) for backward compatibility
                li.textContent = subtask;
            }

            subtasksList.appendChild(li);
        });

        // Display total subtask time if applicable
        if (totalSubtaskMinutes > 0) {
            const totalLi = document.createElement('li');
            const totalTimeStr = formatTime(totalSubtaskMinutes);
            totalLi.innerHTML = `<strong style="color: #7c3aed;">Total Subtask Time: ${totalTimeStr}</strong>`;
            totalLi.style.borderTop = '2px solid #7c3aed';
            totalLi.style.marginTop = '10px';
            totalLi.style.paddingTop = '10px';
            subtasksList.appendChild(totalLi);
        }
    } else {
        subtasksList.innerHTML = '<li>No subtasks available</li>';
    }

    // Task Description
    document.getElementById('taskDescription').textContent = task.task_description || 'No description available';

    // Show results card with animation
    resultsCard.style.display = 'block';
    setTimeout(() => {
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Set loading state
function setLoadingState(isLoading) {
    analyzeBtn.disabled = isLoading;
    if (isLoading) {
        analyzeText.style.display = 'none';
        analyzeSpinner.style.display = 'inline-block';
    } else {
        analyzeText.style.display = 'inline';
        analyzeSpinner.style.display = 'none';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now - you can enhance this with a toast notification
    if (type === 'error') {
        alert('Error: ' + message);
    } else if (type === 'success') {
        console.log('Success: ' + message);
    } else {
        console.log('Info: ' + message);
    }
}

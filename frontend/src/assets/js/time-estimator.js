const { ipcRenderer } = require('electron');

// Configuration
const API_BASE_URL = 'http://localhost:5000';
const USER_ID = 'student_123';

// State
let currentDate = new Date();
let tasks = [];
let currentFilter = 'all';

// DOM Elements
const calendarDays = document.getElementById('calendarDays');
const currentMonthElement = document.getElementById('currentMonth');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const todoList = document.getElementById('todoList');
const emptyState = document.getElementById('emptyState');
const filterButtons = document.querySelectorAll('.filter-btn');

// Statistics elements
const highPriorityCount = document.getElementById('highPriorityCount');
const mediumPriorityCount = document.getElementById('mediumPriorityCount');
const lowPriorityCount = document.getElementById('lowPriorityCount');
const totalTasksCount = document.getElementById('totalTasksCount');

// Time estimation elements
const totalEstimatedTime = document.getElementById('totalEstimatedTime');
const workloadFill = document.getElementById('workloadFill');
const workloadText = document.getElementById('workloadText');

// Modal elements
const taskModal = document.getElementById('taskModal');
const closeModalBtn = document.getElementById('closeModal');
const modalDate = document.getElementById('modalDate');
const modalTaskList = document.getElementById('modalTaskList');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupNavigation();
    loadTasksFromAPI();
    renderCalendar();

    // Set up real-time polling to refresh tasks every 5 seconds
    setInterval(() => {
        loadTasksFromAPI(true); // Silent mode to reduce console spam
    }, 5000); // Refresh every 5 seconds
});

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
    // Calendar navigation
    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // Filter buttons
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.getAttribute('data-filter');
            renderTodoList();
        });
    });

    // Modal close
    closeModalBtn.addEventListener('click', () => {
        taskModal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            taskModal.style.display = 'none';
        }
    });
}

// Load tasks from API
async function loadTasksFromAPI(silent = false) {
    try {
        if (!silent) console.log('Fetching tasks from API...');
        const response = await fetch(`${API_BASE_URL}/tasks/${USER_ID}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!silent) console.log('API Response:', data);

        // Transform API data to internal format
        tasks = data.tasks.map(task => {
            // Determine priority based on main task or default to Medium
            let priority = 'Medium';
            if (task.main_task && task.main_task.difficulty) {
                const difficulty = task.main_task.difficulty;
                if (difficulty >= 4) priority = 'High';
                else if (difficulty <= 2) priority = 'Low';
            }

            return {
                id: task.task_id,
                name: task.subtask || 'Unnamed Task',
                description: task.main_task ? task.main_task.name : '',
                category: task.category || 'general',
                predicted_time: task.predicted_time || 0,
                user_estimate: task.user_estimate,
                actual_time: task.actual_time,
                status: task.status || 'scheduled',
                time_allocation_date: task.time_allocation_date,
                created_date: task.created_date,
                completed_date: task.completed_date,
                confidence: task.confidence || 'UNKNOWN',
                method: task.method || 'unknown',
                priority: priority
            };
        });

        if (!silent) console.log(`Loaded ${tasks.length} tasks`);

        renderTodoList();
        updateStatistics();
        renderCalendar();
        updateTimeEstimation();

    } catch (error) {
        console.error('Failed to load tasks from API:', error);
        showNotification('Failed to load tasks. Make sure the API is running at ' + API_BASE_URL, 'error');
    }
}

// Render Calendar
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    currentMonthElement.textContent = `${monthNames[month]} ${year}`;

    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    // Clear calendar
    calendarDays.innerHTML = '';

    // Add previous month's days
    for (let i = firstDay - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i;
        const dayElement = createDayElement(day, year, month - 1, true);
        calendarDays.appendChild(dayElement);
    }

    // Add current month's days
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = day === today.getDate() &&
            month === today.getMonth() &&
            year === today.getFullYear();

        const dayElement = createDayElement(day, year, month, false, isToday);
        calendarDays.appendChild(dayElement);
    }

    // Add next month's days to fill grid
    const totalCells = calendarDays.children.length;
    const remainingCells = 42 - totalCells; // 6 rows × 7 days

    for (let day = 1; day <= remainingCells; day++) {
        const dayElement = createDayElement(day, year, month + 1, true);
        calendarDays.appendChild(dayElement);
    }
}

// Create day element
function createDayElement(day, year, month, isOtherMonth = false, isToday = false) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';

    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    }
    if (isToday) {
        dayElement.classList.add('today');
    }

    // Create date string
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

    // Find tasks for this date based on time_allocation_date
    const tasksForDay = tasks.filter(task => {
        if (!task.time_allocation_date) return false;
        const taskDate = task.time_allocation_date.split('T')[0]; // Get date part only
        return taskDate === dateStr;
    });

    if (tasksForDay.length > 0) {
        dayElement.classList.add('has-task');

        // Add click handler to show tasks
        dayElement.addEventListener('click', () => {
            showTasksForDate(dateStr, tasksForDay);
        });
    }

    const dayNumber = document.createElement('div');
    dayNumber.className = 'day-number';
    dayNumber.textContent = day;

    // Add task count indicator
    if (tasksForDay.length > 0) {
        const taskCount = document.createElement('div');
        taskCount.className = 'task-count';
        taskCount.textContent = tasksForDay.length;
        dayElement.appendChild(dayNumber);
        dayElement.appendChild(taskCount);
    } else {
        dayElement.appendChild(dayNumber);
    }

    return dayElement;
}

// Show tasks for a specific date in modal
function showTasksForDate(dateStr, tasksForDay) {
    const date = new Date(dateStr);
    const formattedDate = date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    modalDate.textContent = formattedDate;
    modalTaskList.innerHTML = '';

    tasksForDay.forEach(task => {
        const taskElement = createModalTaskElement(task);
        modalTaskList.appendChild(taskElement);
    });

    taskModal.style.display = 'block';
}

// Create modal task element
function createModalTaskElement(task) {
    const taskItem = document.createElement('div');
    taskItem.className = `modal-task-item ${task.priority}`;

    // Prioritize user_estimate over predicted_time (system_estimate)
    const estimatedTime = task.user_estimate || task.predicted_time;
    const timeStr = formatTime(estimatedTime);
    const statusBadge = getStatusBadge(task.status);

    taskItem.innerHTML = `
        <div class="modal-task-header">
            <div class="modal-task-title">${task.name}</div>
            ${statusBadge}
        </div>
        ${task.description ? `<div class="modal-task-description"><strong>Main Task:</strong> ${task.description}</div>` : ''}
        <div class="modal-task-meta">
            <div class="modal-meta-item">
                <span class="meta-label">Category:</span>
                <span class="meta-value">${task.category}</span>
            </div>
            <div class="modal-meta-item">
                <span class="meta-label">Estimated Time:</span>
                <span class="meta-value">${timeStr}</span>
            </div>
            <div class="modal-meta-item">
                <span class="meta-label">Confidence:</span>
                <span class="meta-value confidence-${task.confidence}">${task.confidence}</span>
            </div>
            <div class="modal-meta-item">
                <span class="meta-label">Method:</span>
                <span class="meta-value">${task.method}</span>
            </div>
            ${task.actual_time ? `
            <div class="modal-meta-item">
                <span class="meta-label">Actual Time:</span>
                <span class="meta-value">${formatTime(task.actual_time)}</span>
            </div>
            ` : ''}
        </div>
    `;

    return taskItem;
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'scheduled': '<span class="status-badge scheduled">Scheduled</span>',
        'in_progress': '<span class="status-badge in-progress">In Progress</span>',
        'completed': '<span class="status-badge completed">Completed</span>'
    };
    return badges[status] || '<span class="status-badge">Unknown</span>';
}

// Render Todo List
function renderTodoList() {
    let filteredTasks = tasks.filter(task => task.status !== 'completed');

    if (currentFilter !== 'all') {
        filteredTasks = filteredTasks.filter(task => task.priority === currentFilter);
    }

    // Sort by time_allocation_date
    filteredTasks.sort((a, b) => {
        if (!a.time_allocation_date) return 1;
        if (!b.time_allocation_date) return -1;
        return new Date(a.time_allocation_date) - new Date(b.time_allocation_date);
    });

    if (filteredTasks.length === 0) {
        todoList.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    todoList.innerHTML = '';

    filteredTasks.forEach(task => {
        const taskElement = createTodoElement(task);
        todoList.appendChild(taskElement);
    });
}

// Create todo element
function createTodoElement(task) {
    const todoItem = document.createElement('div');
    todoItem.className = `todo-item ${task.priority}`;

    // Prioritize user_estimate over predicted_time (system_estimate)
    const estimatedTime = task.user_estimate || task.predicted_time;
    const timeStr = formatTime(estimatedTime);
    const allocationDate = task.time_allocation_date
        ? formatDate(task.time_allocation_date.split('T')[0])
        : 'Not scheduled';

    todoItem.innerHTML = `
        <div class="todo-header">
            <div class="todo-title">${task.name}</div>
        </div>
        <div class="todo-meta">
            <div class="todo-meta-item">
                <span>📅</span>
                <span>${allocationDate}</span>
            </div>
            <div class="todo-meta-item">
                <span>⏱️</span>
                <span>${timeStr}</span>
            </div>
            <div class="todo-meta-item">
                <span class="priority-badge ${task.priority}">${task.priority}</span>
            </div>
            <div class="todo-meta-item">
                <span class="confidence-badge ${task.confidence}">${task.confidence}</span>
            </div>
        </div>
        ${task.description ? `<div class="todo-description"><strong>Main Task:</strong> ${task.description}</div>` : ''}
    `;

    return todoItem;
}

// Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Format time
function formatTime(minutes) {
    if (!minutes || minutes === 0) return '0m';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
}

// Update statistics
function updateStatistics() {
    const incompleteTasks = tasks.filter(t => t.status !== 'completed');
    const high = incompleteTasks.filter(t => t.priority === 'High').length;
    const medium = incompleteTasks.filter(t => t.priority === 'Medium').length;
    const low = incompleteTasks.filter(t => t.priority === 'Low').length;
    const total = incompleteTasks.length;

    highPriorityCount.textContent = high;
    mediumPriorityCount.textContent = medium;
    lowPriorityCount.textContent = low;
    totalTasksCount.textContent = total;
}

// Update time estimation
function updateTimeEstimation() {
    // Calculate total estimated time for incomplete tasks
    // Prioritize user_estimate over predicted_time (system_estimate)
    const incompleteTasks = tasks.filter(task => task.status !== 'completed');
    const totalMinutes = incompleteTasks.reduce((sum, task) => {
        const estimatedTime = task.user_estimate || task.predicted_time || 0;
        return sum + estimatedTime;
    }, 0);
    totalEstimatedTime.textContent = formatTime(totalMinutes);

    // Calculate workload (assuming 8 hours/day available for 7 days = 3360 minutes)
    const availableMinutes = 7 * 8 * 60;
    const workloadPercentage = Math.min((totalMinutes / availableMinutes) * 100, 100);

    workloadFill.style.width = workloadPercentage + '%';
    workloadText.textContent = `Workload: ${workloadPercentage.toFixed(0)}%`;
}

// Show notification
function showNotification(message, type = 'info') {
    console.log(`${type}: ${message}`);
    // You can implement a toast notification here if needed
}

// Refresh tasks button (optional - can be called manually)
window.refreshTasks = loadTasksFromAPI;

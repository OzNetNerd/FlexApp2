/**
 * js/pages/tasks/create.js
 * Functionality specific to the task creation/editing page
 */

import log from '/static/js/core/utils/logger.js';

const scriptName = "task.js";

// Only run this script on task pages
document.addEventListener('DOMContentLoaded', () => {
    const functionName = "DOMContentLoaded";

    // Check if we're on a task page
    const taskForm = document.getElementById('task-form');
    if (!taskForm) {
        log("debug", scriptName, functionName, "Not on a task page, exiting");
        return;
    }

    log("info", scriptName, functionName, "📋 Task page detected, initializing task-specific functionality");

    // Initialize task-specific functionality
    initializeDatePickers();
    initializeTaskForm();
    initializeTaskAssignees();

    log("info", scriptName, functionName, "✅ Task page initialization complete");
});

/**
 * Initialize date picker fields
 */
function initializeDatePickers() {
    const functionName = "initializeDatePickers";

    const datePickers = document.querySelectorAll('.date-picker');
    if (!datePickers.length) {
        log("debug", scriptName, functionName, "No date pickers found");
        return;
    }

    log("info", scriptName, functionName, `Initializing ${datePickers.length} date pickers`);

    // Set minimum date to today for all date pickers
    const today = new Date().toISOString().split('T')[0];

    datePickers.forEach(picker => {
        // Set min date to today for start dates
        if (picker.name.includes('start') || picker.name.includes('due')) {
            picker.min = today;
        }

        // Add change event listener
        picker.addEventListener('change', () => {
            log("debug", scriptName, functionName, `Date selected for ${picker.name}: ${picker.value}`);
            validateDates();
        });
    });
}

/**
 * Validate date ranges
 */
function validateDates() {
    const functionName = "validateDates";

    const startDate = document.querySelector('[name="start_date"]');
    const dueDate = document.querySelector('[name="due_date"]');

    if (!startDate || !dueDate) {
        return;
    }

    if (startDate.value && dueDate.value) {
        if (new Date(startDate.value) > new Date(dueDate.value)) {
            log("warn", scriptName, functionName, "⚠️ Invalid date range: start date is after due date");

            if (typeof window.showToast === 'function') {
                window.showToast("Due date cannot be earlier than start date", "warning");
            }

            // Reset due date to start date
            dueDate.value = startDate.value;
        }
    }
}

/**
 * Initialize the task form
 */
function initializeTaskForm() {
    const functionName = "initializeTaskForm";

    const taskForm = document.getElementById('task-form');

    taskForm.addEventListener('submit', (event) => {
        // Form validation
        if (!validateTaskForm()) {
            event.preventDefault();
            log("warn", scriptName, functionName, "❌ Form submission prevented due to validation errors");

            if (typeof window.showToast === 'function') {
                window.showToast("Please fix the errors in the form", "danger");
            }
        } else {
            log("info", scriptName, functionName, "✅ Form validated successfully, submitting");
        }
    });

    // Add auto-save functionality for draft tasks
    let autoSaveTimer;
    const autoSaveFields = taskForm.querySelectorAll('.auto-save');

    autoSaveFields.forEach(field => {
        field.addEventListener('input', () => {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(() => {
                saveTaskDraft();
            }, 2000); // Auto-save after 2 seconds of inactivity
        });
    });
}

/**
 * Validate the task form
 * @returns {boolean} - Whether the form is valid
 */
function validateTaskForm() {
    const functionName = "validateTaskForm";

    const taskName = document.querySelector('[name="task_name"]');
    const taskDescription = document.querySelector('[name="task_description"]');

    let valid = true;

    // Check required fields
    if (!taskName || !taskName.value.trim()) {
        log("warn", scriptName, functionName, "❌ Validation error: Task name is required");
        highlightError(taskName);
        valid = false;
    }

    if (!taskDescription || taskDescription.value.trim().length < 10) {
        log("warn", scriptName, functionName, "❌ Validation error: Task description should be at least 10 characters");
        highlightError(taskDescription);
        valid = false;
    }

    return valid;
}

/**
 * Highlight form field with error
 * @param {Element} field - The field with an error
 */
function highlightError(field) {
    field.classList.add('is-invalid');

    field.addEventListener('input', function removeError() {
        field.classList.remove('is-invalid');
        field.removeEventListener('input', removeError);
    });
}

/**
 * Save task draft to localStorage
 */
function saveTaskDraft() {
    const functionName = "saveTaskDraft";

    const taskForm = document.getElementById('task-form');
    const formData = new FormData(taskForm);
    const taskData = Object.fromEntries(formData.entries());

    // Add timestamp
    taskData.lastSaved = new Date().toISOString();

    // Save to localStorage
    try {
        localStorage.setItem('taskDraft', JSON.stringify(taskData));
        log("info", scriptName, functionName, "✅ Task draft saved automatically");
    } catch (error) {
        log("error", scriptName, functionName, "❌ Error saving task draft", { error });
    }
}

/**
 * Initialize task assignees functionality
 */
function initializeTaskAssignees() {
    const functionName = "initializeTaskAssignees";

    const assigneeContainer = document.querySelector('.task-assignees');
    if (!assigneeContainer) {
        log("debug", scriptName, functionName, "No assignee container found");
        return;
    }

    const addAssigneeBtn = document.querySelector('.add-assignee-btn');
    if (addAssigneeBtn) {
        addAssigneeBtn.addEventListener('click', () => {
            log("debug", scriptName, functionName, "Add assignee button clicked");
            // Open assignee selector or implement your assignee add logic
        });
    }

    // Setup existing assignee remove buttons
    const removeButtons = assigneeContainer.querySelectorAll('.remove-assignee-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const assigneeId = button.dataset.assigneeId;
            log("info", scriptName, functionName, `Removing assignee: ${assigneeId}`);

            // Remove the assignee element
            const assigneeElement = button.closest('.assignee-item');
            if (assigneeElement) {
                assigneeElement.remove();
            }
        });
    });
}
function toggleTask(taskId) {
    fetch(`/api/task/${taskId}/toggle`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const task = document.querySelector(`[data-task-id="${taskId}"] .task-text`);
                task.classList.toggle('completed', data.new_status === 1);
            }
        });
}

function deleteTask(taskId) {
    if (!confirm("Delete this task?")) return;
    fetch(`/api/task/${taskId}/delete`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                // Instead of reloading, just remove the task element
                document.querySelector(`[data-task-id="${taskId}"]`).remove();
            }
        });
}

function addTask(todoId) {
    const input = document.getElementById("newTaskInput");
    const text = input.value.trim();
    if (!text) return;
    
    fetch(`/api/todo/${todoId}/add-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            // Instead of reloading, dynamically add the new task to the DOM
            addTaskToDOM(data.task);
            input.value = ''; // Clear the input
        }
    });
}

function addTaskToDOM(task) {
    const tasksList = document.getElementById('tasksList');
    const taskDiv = document.createElement('div');
    taskDiv.className = 'task-item';
    taskDiv.setAttribute('data-task-id', task.id);
    
    taskDiv.innerHTML = `
        <input type="checkbox" onchange="toggleTask('${task.id}')">
        <span class="task-text">${escapeHtml(task.text_content)}</span>
        <div class="task-actions ms-auto">
            <button onclick="deleteTask('${task.id}')" type="button">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    tasksList.appendChild(taskDiv);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function deleteTodo(todoId) {
    if (!confirm("Delete this todo and all tasks?")) return;
    fetch(`/api/todo/${todoId}/delete`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) window.location.href = "/todos";
        });
}
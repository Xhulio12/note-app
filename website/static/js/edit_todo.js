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
        if (data.success) location.reload();
    });
}

function deleteTodo(todoId) {
    if (!confirm("Delete this todo and all tasks?")) return;
    fetch(`/api/todo/${todoId}/delete`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) window.location.href = "/todos";
        });
}
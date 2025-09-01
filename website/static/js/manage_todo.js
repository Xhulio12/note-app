document.addEventListener('DOMContentLoaded', function() {
    let draggedElement = null;
    let draggedType = null; // 'todo' or 'task'
    let originalOrder = [];
    let hasChanges = false;
    
    const todosContainer = document.getElementById('todosContainer');
    const reorderIndicator = document.getElementById('reorderIndicator');
    const saveOrderBtn = document.getElementById('saveOrderBtn');
    
    // Initialize drag and drop for todos
    initializeTodoDragDrop();
    initializeTaskDragDrop();
    
    // Set initial progress bar widths
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.getAttribute('data-width') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
    
    function initializeTodoDragDrop() {
        const todoCards = document.querySelectorAll('.todo-card');
        originalOrder = Array.from(todoCards).map(card => card.dataset.todoId);
        
        todoCards.forEach(card => {
            const header = card.querySelector('.todo-header');
            
            header.addEventListener('dragstart', function(e) {
                draggedElement = card;
                draggedType = 'todo';
                card.classList.add('dragging');
                reorderIndicator.style.display = 'block';
                e.dataTransfer.effectAllowed = 'move';
            });
            
            header.addEventListener('dragend', function(e) {
                card.classList.remove('dragging');
                draggedElement = null;
                draggedType = null;
                reorderIndicator.style.display = 'none';
                
                // Remove drag-over from all cards
                document.querySelectorAll('.todo-card').forEach(c => {
                    c.classList.remove('drag-over');
                });
                
                checkForChanges();
            });
            
            card.addEventListener('dragover', function(e) {
                e.preventDefault();
                if (draggedType === 'todo' && this !== draggedElement) {
                    this.classList.add('drag-over');
                }
            });
            
            card.addEventListener('dragleave', function(e) {
                this.classList.remove('drag-over');
            });
            
            card.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                if (draggedType === 'todo' && this !== draggedElement) {
                    const allCards = Array.from(todosContainer.children);
                    const draggedIndex = allCards.indexOf(draggedElement);
                    const targetIndex = allCards.indexOf(this);
                    
                    if (draggedIndex < targetIndex) {
                        this.parentNode.insertBefore(draggedElement, this.nextSibling);
                    } else {
                        this.parentNode.insertBefore(draggedElement, this);
                    }
                    
                    // Visual feedback
                    draggedElement.style.transform = 'scale(1.02)';
                    setTimeout(() => {
                        if (draggedElement) {
                            draggedElement.style.transform = '';
                        }
                    }, 200);
                }
            });
        });
    }
    
    function initializeTaskDragDrop() {
        const taskItems = document.querySelectorAll('.task-item');
        
        taskItems.forEach(task => {
            const dragHandle = task.querySelector('.task-drag-handle');
            
            dragHandle.addEventListener('mousedown', function() {
                task.draggable = true;
            });
            
            task.addEventListener('dragstart', function(e) {
                if (!task.draggable) return;
                
                draggedElement = task;
                draggedType = 'task';
                task.classList.add('dragging');
                reorderIndicator.style.display = 'block';
                e.dataTransfer.effectAllowed = 'move';
            });
            
            task.addEventListener('dragend', function(e) {
                task.classList.remove('dragging');
                task.draggable = false;
                draggedElement = null;
                draggedType = null;
                reorderIndicator.style.display = 'none';
                
                // Remove drag-over from all tasks
                document.querySelectorAll('.task-item').forEach(t => {
                    t.classList.remove('drag-over');
                });
                
                checkForChanges();
            });
            
            task.addEventListener('dragover', function(e) {
                e.preventDefault();
                if (draggedType === 'task' && this !== draggedElement) {
                    const draggedParent = draggedElement.closest('.tasks-list');
                    const thisParent = this.closest('.tasks-list');
                    
                    if (draggedParent === thisParent) {
                        this.classList.add('drag-over');
                    }
                }
            });
            
            task.addEventListener('dragleave', function(e) {
                this.classList.remove('drag-over');
            });
            
            task.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                
                if (draggedType === 'task' && this !== draggedElement) {
                    const draggedParent = draggedElement.closest('.tasks-list');
                    const thisParent = this.closest('.tasks-list');
                    
                    if (draggedParent === thisParent) {
                        const allTasks = Array.from(thisParent.children);
                        const draggedIndex = allTasks.indexOf(draggedElement);
                        const targetIndex = allTasks.indexOf(this);
                        
                        if (draggedIndex < targetIndex) {
                            this.parentNode.insertBefore(draggedElement, this.nextSibling);
                        } else {
                            this.parentNode.insertBefore(draggedElement, this);
                        }
                        
                        // Visual feedback
                        draggedElement.style.backgroundColor = 'rgba(40, 167, 69, 0.1)';
                        setTimeout(() => {
                            if (draggedElement) {
                                draggedElement.style.backgroundColor = '';
                            }
                        }, 500);
                    }
                }
            });
        });
    }
    
    function checkForChanges() {
        const currentOrder = Array.from(document.querySelectorAll('.todo-card')).map(card => card.dataset.todoId);
        hasChanges = !arraysEqual(originalOrder, currentOrder);
        
        if (hasChanges) {
            saveOrderBtn.style.display = 'flex';
        } else {
            saveOrderBtn.style.display = 'none';
        }
    }
    
    function arraysEqual(a, b) {
        return a.length === b.length && a.every((val, i) => val === b[i]);
    }
    
    // Global functions
    window.toggleTask = function(taskId) {
        fetch(`/api/task/${taskId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const checkbox = document.querySelector(`[data-task-id="${taskId}"] .task-checkbox`);
                const taskText = document.querySelector(`[data-task-id="${taskId}"] .task-text`);
                const todoCard = document.querySelector(`[data-task-id="${taskId}"]`).closest('.todo-card');
                
                if (data.new_status === 1) {
                    taskText.classList.add('completed');
                } else {
                    taskText.classList.remove('completed');
                }
                
                // Update progress bar
                updateProgressBar(todoCard);
                
                // Show success animation
                const taskItem = document.querySelector(`[data-task-id="${taskId}"]`);
                taskItem.style.backgroundColor = 'rgba(40, 167, 69, 0.2)';
                setTimeout(() => {
                    taskItem.style.backgroundColor = '';
                }, 300);
            }
        })
        .catch(error => {
            console.error('Error toggling task:', error);
            // Revert checkbox state
            const checkbox = document.querySelector(`[data-task-id="${taskId}"] .task-checkbox`);
            checkbox.checked = !checkbox.checked;
        });
    };
    
    function updateProgressBar(todoCard) {
        const tasks = todoCard.querySelectorAll('.task-item');
        const completedTasks = todoCard.querySelectorAll('.task-text.completed');
        const percentage = tasks.length > 0 ? (completedTasks.length / tasks.length) * 100 : 0;
        
        const progressBar = todoCard.querySelector('.progress-bar');
        const progressText = todoCard.querySelector('.progress-text');
        
        progressBar.style.width = percentage + '%';
        progressText.textContent = `${Math.round(percentage)}% Complete (${completedTasks.length} of ${tasks.length} tasks)`;
    }
    
    window.editTodo = function(todoId) {
        window.location.href = `/todo/${todoId}/edit`;
    };
    
    window.deleteTodo = function(todoId) {
        if (confirm('Are you sure you want to delete this todo? This action cannot be undone.')) {
            fetch(`/api/todo/${todoId}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const todoCard = document.querySelector(`[data-todo-id="${todoId}"]`);
                    todoCard.style.animation = 'slideOut 0.3s ease forwards';
                    setTimeout(() => {
                        todoCard.remove();
                        checkForChanges();
                    }, 300);
                } else {
                    alert('Error deleting todo: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error deleting todo:', error);
                alert('Error deleting todo. Please try again.');
            });
        }
    };
    
    window.saveOrder = function() {
        const todoOrder = Array.from(document.querySelectorAll('.todo-card')).map((card, index) => ({
            id: card.dataset.todoId,
            position: index
        }));
        
        const taskOrders = {};
        document.querySelectorAll('.tasks-list').forEach(tasksList => {
            const todoId = tasksList.id.replace('tasks-', '');
            taskOrders[todoId] = Array.from(tasksList.querySelectorAll('.task-item')).map((task, index) => ({
                id: task.dataset.taskId,
                position: index
            }));
        });
        
        fetch('/api/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({
                todos: todoOrder,
                tasks: taskOrders
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                hasChanges = false;
                saveOrderBtn.style.display = 'none';
                originalOrder = Array.from(document.querySelectorAll('.todo-card')).map(card => card.dataset.todoId);
                
                // Show success message
                const indicator = document.createElement('div');
                indicator.innerHTML = '<i class="fas fa-check me-2"></i>Order saved successfully!';
                indicator.style.cssText = `
                    position: fixed; top: 1rem; right: 1rem; z-index: 1060;
                    background: #28a745; color: white; padding: 0.75rem 1.5rem;
                    border-radius: 25px; font-weight: 600;
                    box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
                    animation: slideInRight 0.3s ease;
                `;
                document.body.appendChild(indicator);
                
                setTimeout(() => {
                    indicator.style.animation = 'slideOutRight 0.3s ease';
                    setTimeout(() => indicator.remove(), 300);
                }, 2000);
            } else {
                alert('Error saving order: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error saving order:', error);
            alert('Error saving order. Please try again.');
        });
    };
});

// Add some CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to { transform: translateX(100%); opacity: 0; }
    }
    @keyframes slideInRight {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    @keyframes slideOutRight {
        to { transform: translateX(100%); }
    }
`;
document.head.appendChild(style);
document.addEventListener('DOMContentLoaded', function() {
    let taskCount = 0;
    const tasksContainer = document.getElementById('tasksContainer');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskCounter = document.getElementById('taskCounter');
    const nameInput = document.getElementById('name');
    const nameCharCount = document.getElementById('nameCharCount');
    
    // Character counter for todo name
    nameInput.addEventListener('input', function() {
        const length = this.value.length;
        nameCharCount.textContent = `${length}/255 characters`;
        
        if (length > 200) {
            nameCharCount.classList.add('warning');
        } else {
            nameCharCount.classList.remove('warning');
        }
        
        if (length > 240) {
            nameCharCount.classList.add('danger');
            nameCharCount.classList.remove('warning');
        } else {
            nameCharCount.classList.remove('danger');
        }
    });
    
    // Add initial task
    addTask();
    
    // Add task button click handler
    addTaskBtn.addEventListener('click', function() {
        addTask();
    });
    
    function addTask(content = '') {
        taskCount++;
        const taskDiv = document.createElement('div');
        taskDiv.className = 'task-item';
        taskDiv.draggable = true;
        taskDiv.innerHTML = `
            <div class="task-number">${taskCount}</div>
            <div class="drag-handle" title="Drag to reorder">
                <i class="fas fa-grip-vertical"></i>
            </div>
            <div class="task-content">
                <textarea class="task-input" 
                          name="tasks[]" 
                          placeholder="Enter task description..."
                          rows="1"
                          maxlength="500">${content}</textarea>
            </div>
            <button type="button" class="remove-task" onclick="removeTask(this)">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        tasksContainer.appendChild(taskDiv);
        updateTaskCounter();
        updateTaskNumbers();
        
        // Add drag and drop event listeners
        addDragListeners(taskDiv);
        
        // Auto-resize textarea
        const textarea = taskDiv.querySelector('.task-input');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Focus on the new task
        textarea.focus();
    }
    
    window.removeTask = function(button) {
        if (tasksContainer.children.length > 1) {
            button.parentElement.remove();
            updateTaskCounter();
            updateTaskNumbers();
        } else {
            alert('You must have at least one task!');
        }
    };
    
    function updateTaskNumbers() {
        const taskItems = tasksContainer.querySelectorAll('.task-item');
        taskItems.forEach((item, index) => {
            const numberElement = item.querySelector('.task-number');
            if (numberElement) {
                numberElement.textContent = index + 1;
            }
        });
    }
    
    function updateTaskCounter() {
        const count = tasksContainer.children.length;
        taskCounter.textContent = `${count} task${count !== 1 ? 's' : ''}`;
    }
    
    // Drag and Drop Functionality
    let draggedElement = null;
    
    function addDragListeners(taskItem) {
        taskItem.addEventListener('dragstart', function(e) {
            draggedElement = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', this.outerHTML);
        });
        
        taskItem.addEventListener('dragend', function(e) {
            this.classList.remove('dragging');
            draggedElement = null;
            
            // Remove drag-over class from all items
            document.querySelectorAll('.task-item').forEach(item => {
                item.classList.remove('drag-over');
            });
        });
        
        taskItem.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            if (this !== draggedElement) {
                this.classList.add('drag-over');
            }
        });
        
        taskItem.addEventListener('dragenter', function(e) {
            e.preventDefault();
        });
        
        taskItem.addEventListener('dragleave', function(e) {
            this.classList.remove('drag-over');
        });
        
        taskItem.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            if (this !== draggedElement) {
                const allTasks = Array.from(tasksContainer.children);
                const draggedIndex = allTasks.indexOf(draggedElement);
                const targetIndex = allTasks.indexOf(this);
                
                if (draggedIndex < targetIndex) {
                    this.parentNode.insertBefore(draggedElement, this.nextSibling);
                } else {
                    this.parentNode.insertBefore(draggedElement, this);
                }
                
                updateTaskNumbers();
                
                // Show visual feedback
                draggedElement.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    if (draggedElement) {
                        draggedElement.style.transform = '';
                    }
                }, 200);
            }
        });
    }
    
    // Form validation
    document.getElementById('todoForm').addEventListener('submit', function(e) {
        const todoName = nameInput.value.trim();
        const tasks = Array.from(document.querySelectorAll('.task-input')).map(input => input.value.trim());
        const nonEmptyTasks = tasks.filter(task => task.length > 0);
        
        if (!todoName) {
            e.preventDefault();
            alert('Please enter a todo title!');
            nameInput.focus();
            return;
        }
        
        if (nonEmptyTasks.length === 0) {
            e.preventDefault();
            alert('Please add at least one task!');
            return;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Creating...';
        submitBtn.disabled = true;
        
        // If validation passes, the form will submit normally
        // In case of error, restore button state
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    });
    
    // Add some visual feedback
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('task-input') || e.target.closest('.task-item')) {
            const taskItems = document.querySelectorAll('.task-item');
            taskItems.forEach(item => item.style.borderColor = '#dee2e6');
            
            const currentTask = e.target.closest('.task-item');
            if (currentTask) {
                currentTask.style.borderColor = 'var(--orange)';
            }
        }
    });
});
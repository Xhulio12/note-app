from datetime import date, datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from sqlalchemy import and_
from .models import PaymentReminder, ToDo, Note, ToDoTask
from . import db

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    user_id = current_user.id
    payment_reminders = PaymentReminder.query.filter_by(user_id=user_id, is_active=True).order_by(
        PaymentReminder.pmt_date).all()
    todos = ToDo.query.filter_by(user_id=user_id, is_active=True).order_by(ToDo.due_date).all()
    notes = Note.query.filter_by(user_id=user_id, is_active=True).order_by(Note.last_modified_date.desc()).all()
    completed_todos = ToDo.query.filter_by(user_id=user_id, status=2, is_active=True).count()

    return render_template('home.html',
                           user=current_user,
                           payment_reminders=payment_reminders,
                           todos=todos,
                           notes=notes,
                           completed_todos=completed_todos,
                           today=date.today())

@views.route("/payments", methods=["GET", "POST"])
@login_required
def payments():
    payment_to_edit = None

    if request.method == "POST":
        payment_id = request.form.get("payment_id")
        name = request.form.get("name")
        pmt_date = request.form.get("pmt_date")
        pmt_amount = request.form.get("pmt_amount")
        notes = request.form.get("notes")
        is_active = True if request.form.get("is_active") == "on" else False

        if payment_id:  # Edit
            payment = PaymentReminder.query.get_or_404(payment_id)
            if payment.user_id != current_user.id:
                flash("Unauthorized access", "error")
                return redirect(url_for("views.payments"))
            payment.name = name
            payment.pmt_date = datetime.strptime(pmt_date, "%Y-%m-%d")
            payment.pmt_amount = pmt_amount
            payment.notes = notes
            payment.is_active = is_active
            flash("Payment updated successfully!", "success")
        else:  # Add new
            new_payment = PaymentReminder(
                user_id=current_user.id,
                name=name,
                pmt_date=datetime.strptime(pmt_date, "%Y-%m-%d"),
                pmt_amount=pmt_amount,
                notes=notes,
                is_active=is_active
            )
            db.session.add(new_payment)
            flash("Payment added successfully!", "success")

        db.session.commit()
        return redirect(url_for("views.payments"))

    # GET request
    payments = PaymentReminder.query.filter_by(user_id=current_user.id).order_by(PaymentReminder.pmt_date).all()

    # Preselect if payment_id in query string
    payment_id = request.args.get("payment_id")
    if payment_id:
        payment_to_edit = PaymentReminder.query.filter_by(id=payment_id, user_id=current_user.id).first()

    return render_template("payments.html", user=current_user, payments=payments, payment_to_edit=payment_to_edit)



@login_required
@views.route("/payments/delete/<int:id>", methods=["POST"])
def delete_payment(id):
    payment = PaymentReminder.query.get_or_404(id)
    if payment.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("views.payments"))

    db.session.delete(payment)
    db.session.commit()
    flash("Payment deleted successfully!", "success")
    return redirect(url_for("views.payments"))


@views.route('/todos')
@login_required
def manage_todos():
    """Display all todos for the current user with drag-and-drop management."""
    try:
        # Get all active todos for the current user, ordered by position or creation date
        todos = ToDo.query.filter(
            and_(
                ToDo.user_id == current_user.id,
                ToDo.is_active == True
            )
        ).order_by(ToDo.created_date.asc()).all()

        # Get today's date for due date calculations
        today = date.today()

        return render_template(
            'manage_todo.html',
            user=current_user,
            todos=todos,
            today=today,
            page_title='Manage Todos'
        )

    except Exception as e:
        flash(f'Error loading todos: {str(e)}', 'danger')
        return redirect(url_for('views.home'))


@views.route('/add-todo', methods=['GET', 'POST'])
@login_required
def add_todo():
    if request.method == 'GET':
        return render_template('add_todo.html',
                               user=current_user,  # Add this
                               today=date.today())

    elif request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            due_date_str = request.form.get('due_date')
            tasks = request.form.getlist('tasks[]')

            # Basic validation
            if not name:
                flash('Todo name is required!', 'error')
                return render_template('add_todo.html',
                                       user=current_user,  # Add this
                                       today=date.today())

            # Filter empty tasks
            valid_tasks = [task.strip() for task in tasks if task.strip()]
            if not valid_tasks:
                flash('At least one task is required!', 'error')
                return render_template('add_todo.html',
                                       user=current_user,  # Add this
                                       today=date.today())

            # Handle due date
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

            # Create todo
            new_todo = ToDo(
                name=name,
                user_id=current_user.id,
                due_date=due_date,
                status=0,
                is_active=True
            )

            db.session.add(new_todo)
            db.session.flush()

            # Create tasks
            for i, task_content in enumerate(valid_tasks):
                task = ToDoTask(
                    to_do_id=new_todo.id,
                    text_content=task_content,
                    status=0,
                    position=i
                )
                db.session.add(task)

            db.session.commit()
            flash(f'Todo "{name}" created with {len(valid_tasks)} tasks!', 'success')
            return redirect(url_for('views.manage_todos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return render_template('add_todo.html',
                                   user=current_user,
                                   today=date.today())
    return None


@views.route('/todo/<int:todo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    """Edit a todo (name, due date, priority)."""
    todo = ToDo.query.filter_by(id=todo_id, user_id=current_user.id, is_active=True).first_or_404()

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            due_date_str = request.form.get('due_date', '').strip()
            priority = request.form.get('priority', 'Medium')

            if not name:
                flash('Todo name cannot be empty.', 'error')
                return redirect(url_for('views.edit_todo', todo_id=todo.id))

            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            # Update todo fields
            todo.name = name
            todo.due_date = due_date
            todo.priority = priority
            todo.updated_date = datetime.utcnow()

            db.session.commit()

            flash('Todo updated successfully!', 'success')
            return redirect(url_for('views.manage_todos'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating todo: {str(e)}', 'error')
            return redirect(url_for('views.edit_todo', todo_id=todo.id))

    return render_template('edit_todo.html', todo=todo, user=current_user)



# API Routes for AJAX functionality
@views.route('/api/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle the completion status of a task."""
    try:
        # Find the task and verify ownership through the todo
        task = ToDoTask.query.join(ToDo).filter(
            and_(
                ToDoTask.id == task_id,
                ToDo.user_id == current_user.id
            )
        ).first()

        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        # Toggle the status (0 = pending, 1 = completed)
        task.status = 1 if task.status == 0 else 0
        task.updated_date = datetime.utcnow()

        # Update the parent todo's status and completion date
        todo = task.todo
        todo.update_status()

        if todo.status == 2:  # completed
            todo.completed_date = datetime.utcnow()
        else:
            todo.completed_date = None

        todo.updated_date = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'new_status': task.status,
            'todo_status': todo.status,
            'completion_percentage': todo.completion_percentage
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@views.route('/api/todo/<int:todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    """Delete a todo and all its tasks."""
    try:
        # Find the todo and verify ownership
        todo = ToDo.query.filter(
            and_(
                ToDo.id == todo_id,
                ToDo.user_id == current_user.id
            )
        ).first()

        if not todo:
            return jsonify({'success': False, 'error': 'Todo not found'}), 404

        # Soft delete by setting is_active to False
        todo.is_active = False
        todo.updated_date = datetime.utcnow()

        db.session.commit()

        return jsonify({'success': True, 'message': 'Todo deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@views.route('/api/reorder', methods=['POST'])
@login_required
def reorder_items():
    """Reorder todos and tasks based on drag-and-drop positions."""
    try:
        data = request.get_json()

        if not data or 'todos' not in data:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400

        # Update todo positions (using updated_date since there's no position field)
        todo_orders = data.get('todos', [])
        base_time = datetime.utcnow()

        for i, todo_data in enumerate(todo_orders):
            todo_id = todo_data.get('id')

            if todo_id:
                todo = ToDo.query.filter(
                    and_(
                        ToDo.id == todo_id,
                        ToDo.user_id == current_user.id
                    )
                ).first()

                if todo:
                    # Use updated_date with microsecond differences to maintain order
                    todo.updated_date = base_time.replace(microsecond=i * 1000)

        # Update task positions within their todos
        task_orders = data.get('tasks', {})
        for todo_id, task_list in task_orders.items():
            for task_data in task_list:
                task_id = task_data.get('id')
                position = task_data.get('position')

                if task_id and position is not None:
                    task = ToDoTask.query.join(ToDo).filter(
                        and_(
                            ToDoTask.id == task_id,
                            ToDo.user_id == current_user.id,
                            ToDo.id == todo_id
                        )
                    ).first()

                    if task:
                        task.position = position
                        task.updated_date = datetime.utcnow()

        db.session.commit()

        return jsonify({'success': True, 'message': 'Order saved successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ... keep everything above unchanged ...

@views.route('/api/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task from a todo."""
    try:
        # Find the task and verify ownership through the parent todo
        task = ToDoTask.query.join(ToDo).filter(
            and_(
                ToDoTask.id == task_id,
                ToDo.user_id == current_user.id
            )
        ).first()

        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        todo = task.todo

        # Soft delete by marking inactive OR hard delete
        db.session.delete(task)
        db.session.commit()

        # Update parent todo status
        todo.update_status()
        todo.updated_date = datetime.utcnow()
        db.session.commit()

        return jsonify({'success': True, 'message': 'Task deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@views.route('/api/todo/<int:todo_id>/add-task', methods=['POST'])
@login_required
def add_task(todo_id):
    """Add a new task to an existing todo."""
    try:
        todo = ToDo.query.filter(
            and_(
                ToDo.id == todo_id,
                ToDo.user_id == current_user.id,
                ToDo.is_active == True
            )
        ).first()

        if not todo:
            return jsonify({'success': False, 'error': 'Todo not found'}), 404

        data = request.get_json()
        text = data.get('text', '').strip() if data else ''

        if not text:
            return jsonify({'success': False, 'error': 'Task text is required'}), 400

        # Find the max position to place this new task at the end
        max_position = db.session.query(db.func.max(ToDoTask.position)).filter_by(to_do_id=todo.id).scalar()
        new_position = (max_position or 0) + 1

        new_task = ToDoTask(
            to_do_id=todo.id,
            text_content=text,
            status=0,
            position=new_position
        )

        db.session.add(new_task)
        db.session.commit()

        # Update parent todo
        todo.update_status()
        todo.updated_date = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task added successfully',
            'task_id': new_task.id,
            'position': new_task.position
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == "POST":
        title = request.form.get("title")
        text_content = request.form.get("text_content")

        if not title.strip():
            flash("Note title is required.", "danger")
        elif not text_content.strip():
            flash("Note content cannot be empty.", "danger")
        else:
            new_note = Note(
                user_id=current_user.id,
                title=title,
                text_content=text_content
            )
            db.session.add(new_note)
            db.session.commit()
            flash("Note added successfully!", "success")
            return redirect(url_for("views.notes"))

    user_notes = Note.query.filter_by(user_id=current_user.id, is_active=True).order_by(Note.last_modified_date.desc()).all()
    return render_template("notes.html", user=current_user, notes=user_notes)


@views.route('/notes/edit/<int:note_id>', methods=['POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("You are not allowed to edit this note.", "danger")
        return redirect(url_for("views.notes"))

    title = request.form.get("title")
    text_content = request.form.get("text_content")

    if not title.strip():
        flash("Note title is required.", "danger")
    elif not text_content.strip():
        flash("Note content cannot be empty.", "danger")
    else:
        note.title = title
        note.text_content = text_content
        db.session.commit()
        flash("Note updated successfully!", "success")

    return redirect(url_for("views.notes"))


@views.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("You are not allowed to delete this note.", "danger")
        return redirect(url_for("views.notes"))

    db.session.delete(note)
    db.session.commit()
    flash("Note deleted successfully!", "success")
    return redirect(url_for("views.notes"))



@views.route('/profile')
@login_required
def profile():
    pass
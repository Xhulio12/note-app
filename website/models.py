from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event
from datetime import datetime as dt

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    f_name = db.Column(db.String(100))
    l_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    user_role = db.Column(db.String(10), default='normal', nullable=False,)

    # Relationships
    payment_reminder = db.relationship("PaymentReminder", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    todo = db.relationship("ToDo", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    note = db.relationship("Note", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = func.now()
        db.session.commit()

    @property
    def full_name(self):
        """Return full name if both first and last name exist."""
        if self.f_name and self.l_name:
            return f"{self.f_name} {self.l_name}"
        elif self.f_name:
            return self.f_name
        elif self.l_name:
            return self.l_name
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"


class PaymentReminder(db.Model):
    __tablename__ = "payment_reminder"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    created_date = db.Column(db.DateTime, default=func.now())
    updated_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    name = db.Column(db.String(255), nullable=False)  # e.g., Netflix, Gym
    pmt_date = db.Column(db.Date, nullable=False)
    pmt_amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Add index for common queries
    __table_args__ = (
        db.Index("idx_user_payment_date", "user_id", "pmt_date"),
    )

    def __repr__(self):
        return f"<PaymentReminder {self.name} - {self.pmt_amount}>"


class ToDo(db.Model):
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.SmallInteger, default=0, nullable=False)  # 0=pending, 1=in_progress, 2=completed, 3=archived
    name = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    created_date = db.Column(db.DateTime, default=func.now())
    updated_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    due_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    completed_date = db.Column(db.DateTime)

    # Relationships
    tasks = db.relationship("ToDoTask", backref="todo", cascade="all, delete-orphan", lazy="dynamic")

    # Add index for common queries
    __table_args__ = (
        db.Index("idx_user_status", "user_id", "status"),
        db.Index("idx_user_due_date", "user_id", "due_date"),
    )

    def update_status(self):
        total_tasks = self.tasks.count()

        if total_tasks == 0:
            self.status = 0
            self.completed_date = None
            return

        completed_tasks = self.tasks.filter_by(status=1).count()

        if completed_tasks == total_tasks:
            self.status = 2
            self.completed_date = dt.utcnow()
        elif completed_tasks > 0:
            self.status = 1
            self.completed_date = None
        else:
            self.status = 0
            self.completed_date = None

    @property
    def completion_percentage(self):
        """Calculate completion percentage based on tasks."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter_by(status=1).count()
        return (completed_tasks / total_tasks) * 100

    def __repr__(self):
        return f"<ToDo {self.name} - Status {self.status}>"


class ToDoTask(db.Model):
    __tablename__ = "todo_task"

    id = db.Column(db.Integer, primary_key=True)
    to_do_id = db.Column(db.Integer, db.ForeignKey("todo.id", ondelete="CASCADE"), nullable=False, index=True)
    text_content = db.Column(db.Text, nullable=False)
    status = db.Column(db.SmallInteger, default=0, nullable=False)  # 0=pending, 1=completed
    position = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, default=func.now())
    updated_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ToDoTask {self.text_content[:20]}...>"


class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=func.now())
    last_modified_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    completed_date = db.Column(db.DateTime)

    # Add index for user searches
    __table_args__ = (
        db.Index("idx_user_modified", "user_id", "last_modified_date"),
    )

    def __repr__(self):
        return f"<Note {self.title or 'Untitled'}>"


class FieldHistory(db.Model):
    __tablename__ = "field_history"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)  # 'payment_reminder', 'todo', 'todo_task', 'note'
    entity_id = db.Column(db.Integer, nullable=False)
    field = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    changed_date = db.Column(db.DateTime, default=func.now())
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    __table_args__ = (
        db.Index("idx_entity_lookup", "entity_type", "entity_id"),
        db.Index("idx_changed_date", "changed_date"),
    )

    def __repr__(self):
        return f"<FieldHistory {self.entity_type}:{self.entity_id} {self.field}>"


# --- Event Listeners to auto-update ToDo status ---
@event.listens_for(ToDoTask, "after_insert")
@event.listens_for(ToDoTask, "after_update")
@event.listens_for(ToDoTask, "after_delete")
def update_todo_status(mapper, connection, target):
    """Automatically update ToDo status when tasks change."""
    session = db.session.object_session(target)
    if not session:
        return

    todo = session.get(ToDo, target.to_do_id)
    if todo:
        todo.update_status()
        session.add(todo)
        # Don't commit here as it might interfere with the main transaction
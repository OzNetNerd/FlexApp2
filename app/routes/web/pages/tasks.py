from flask import render_template, request
from flask_login import login_required
from datetime import datetime, timedelta
import random
from app.models.pages.task import Task
from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
from app.models.base import db

# Create the blueprint with the Task model
tasks_bp = create_crud_blueprint(BlueprintConfig(model_class=Task))


@tasks_bp.route("/", methods=["GET"])
@login_required
def tasks_dashboard():
    # Get basic statistics
    total_tasks = Task.query.count()

    # Get top tasks (those with highest priority or most recent)
    top_tasks = db.session.query(Task).order_by(Task.created_at.desc()).limit(5).all()

    # Overdue and due today stats needed by the template
    overdue_tasks = db.session.query(Task).filter(Task.due_date < datetime.now().date(), Task.status != "completed").count()

    due_today = db.session.query(Task).filter(Task.due_date == datetime.now().date()).count()

    # Calculate statistics
    completed_count = db.session.query(Task).filter(Task.status == "completed").count()
    in_progress_count = db.session.query(Task).filter(Task.status == "in_progress").count()
    not_started_count = db.session.query(Task).filter(Task.status == "pending").count()

    # Update stats dictionary to include all needed values
    stats = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "in_progress_tasks": in_progress_count,
        "pending_tasks": not_started_count,
        "overdue_tasks": overdue_tasks,
        "due_today": due_today,
    }

    # Convert segments to dictionary structure expected by template
    segments = {
        "completed": {"count": completed_count, "percentage": calculate_percentage(completed_count, total_tasks)},
        "in_progress": {"count": in_progress_count, "percentage": calculate_percentage(in_progress_count, total_tasks)},
        "not_started": {"count": not_started_count, "percentage": calculate_percentage(not_started_count, total_tasks)},
    }

    # Rename activity_data to completion_data to match template
    completion_data = prepare_activity_data()

    # Get upcoming tasks for the table section
    upcoming_tasks = db.session.query(Task).filter(Task.due_date >= datetime.now().date()).order_by(Task.due_date.asc()).limit(5).all()

    return render_template(
        "pages/tasks/dashboard.html",
        stats=stats,
        segments=segments,
        upcoming_tasks=upcoming_tasks,  # Changed from top_tasks to upcoming_tasks
        completion_data=completion_data,  # Changed from activity_data to completion_data
    )


# Helper functions
def calculate_percentage(count, total):
    if total == 0:
        return 0
    return round((count / total) * 100)


def prepare_activity_data():
    # Generate sample activity data for the chart
    days = []
    completed_tasks = []
    new_tasks = []

    today = datetime.now().date()

    for i in range(7):
        day = today - timedelta(days=i)
        day_name = day.strftime("%a %d")
        days.append(day_name)

        # Sample data - in a real app, these would be calculated from the database
        completed_tasks.append(random.randint(1, 10))
        new_tasks.append(random.randint(3, 15))

    # Reverse lists to display chronologically
    days.reverse()
    completed_tasks.reverse()
    new_tasks.reverse()

    return {"labels": days, "completed_tasks": completed_tasks, "new_tasks": new_tasks}


@tasks_bp.route("/filtered", methods=["GET"])
@login_required
def filtered_tasks():
    # Start with base query
    query = Task.query

    # Filter by status
    status = request.args.get("status")
    if status:
        query = query.filter(Task.status == status)

    # Filter by priority
    priority = request.args.get("priority")
    if priority:
        query = query.filter(Task.priority == priority)

    # Filter by due date
    due_date = request.args.get("due_date")
    if due_date == "today":
        query = query.filter(Task.due_date == datetime.now().date())
    elif due_date == "this_week":
        today = datetime.now().date()
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        query = query.filter(Task.due_date.between(today, end_of_week))
    elif due_date == "overdue":
        query = query.filter(Task.due_date < datetime.now().date(), Task.status != "completed")

    # Get tasks
    tasks = query.order_by(Task.due_date.asc()).all()

    return render_template("pages/tasks/filtered.html", tasks=tasks, filters={"status": status, "priority": priority, "due_date": due_date})


@tasks_bp.route("/statistics", methods=["GET"])
@login_required
def statistics():
    # Total tasks
    total_tasks = Task.query.count()

    # Tasks by status
    completed_tasks = db.session.query(Task).filter(Task.status == "completed").count()
    in_progress_tasks = db.session.query(Task).filter(Task.status == "in_progress").count()
    pending_tasks = db.session.query(Task).filter(Task.status == "pending").count()

    # Tasks by priority
    high_priority = db.session.query(Task).filter(Task.priority == "high").count()
    medium_priority = db.session.query(Task).filter(Task.priority == "medium").count()
    low_priority = db.session.query(Task).filter(Task.priority == "low").count()

    # Overdue tasks
    overdue_tasks = db.session.query(Task).filter(Task.due_date < datetime.now().date(), Task.status != "completed").count()

    return render_template(
        "pages/tasks/statistics.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        pending_tasks=pending_tasks,
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,
        overdue_tasks=overdue_tasks,
    )

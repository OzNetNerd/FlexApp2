# # app/routes/web/users.py
# from sqlalchemy import func, extract
# import random
# from datetime import datetime, timedelta
# from flask import render_template, request
# from flask_login import login_required
# from app.models import User, Note, Opportunity
# from app.routes.web.utils.blueprint_factory import create_crud_blueprint, BlueprintConfig
# from app.services.user import UserService
# from app.models.base import db
#
# # Create the blueprint with the factory
# users_config = BlueprintConfig(model_class=User, service=UserService(User))
# users_bp = create_crud_blueprint(users_config)
#
#
# # Users Dashboard route
# @users_bp.route("/", methods=["GET"])
# @login_required
# def users_dashboard():
#     # Get statistics for summary section
#     stats = {
#         "total_users": User.query.count(),
#         "admin_count": User.query.filter_by(is_admin=True).count(),
#         "regular_count": User.query.filter_by(is_admin=False).count(),
#         "new_users_month": User.query.filter(
#             User.created_at >= (datetime.now() - timedelta(days=30))
#         ).count(),
#         "avg_notes": calculate_avg_notes_per_user(),
#         "active_users": calculate_active_users(),
#         "top_user": get_top_user_name(),
#         "activity_increase": calculate_activity_increase(),
#         "inactive_count": calculate_inactive_users(),
#     }
#
#     # Get user categories data
#     user_categories = [
#         {
#             "count": User.query.filter_by(is_admin=False).count(),
#             "activity": db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == False).scalar() or 0,
#             "percentage": calculate_user_percentage(False),
#         },
#         {
#             "count": User.query.filter_by(is_admin=True).count(),
#             "activity": db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == True).scalar() or 0,
#             "percentage": calculate_user_percentage(True),
#         },
#         {
#             "count": User.query.filter(
#                 User.created_at >= (datetime.now() - timedelta(days=30))
#             ).count(),
#             "activity": db.session.query(func.count(Note.id)).join(User).filter(
#                 User.created_at >= (datetime.now() - timedelta(days=30))
#             ).scalar() or 0,
#             "percentage": calculate_new_user_percentage(),
#         },
#     ]
#
#     # Get top active users
#     top_users = get_top_users(5)
#
#     # Prepare activity data for chart
#     activity_data = prepare_activity_data()
#
#     return render_template(
#         "pages/users/dashboard.html",
#         stats=stats,
#         user_categories=user_categories,
#         top_users=top_users,
#         activity_data=activity_data,
#     )
#
#
# # Helper functions
# def calculate_avg_notes_per_user():
#     total_users = User.query.count()
#     if total_users == 0:
#         return 0
#     total_notes = db.session.query(func.count(Note.id)).scalar() or 0
#     return round(total_notes / total_users, 1)
#
#
# def calculate_active_users():
#     # Active users are those who have notes created in the last week
#     one_week_ago = datetime.now() - timedelta(days=7)
#     return db.session.query(func.count(func.distinct(Note.user_id))).filter(
#         Note.created_at >= one_week_ago
#     ).scalar() or 0
#
#
# def get_top_user_name():
#     # Get the user with most notes
#     result = db.session.query(
#         User.name,
#         func.count(Note.id).label('notes_count')
#     ).join(User.notes).group_by(User.id).order_by(
#         func.count(Note.id).desc()
#     ).first()
#
#     return result.name if result else "N/A"
#
#
# def calculate_activity_increase():
#     # Calculate activity increase for current month vs previous month
#     # This is a simplified example
#     return 8  # Placeholder value
#
#
# def calculate_inactive_users():
#     two_weeks_ago = datetime.now() - timedelta(days=14)
#
#     # Get users who haven't created notes in the last 14 days
#     active_user_ids = db.session.query(Note.user_id).filter(
#         Note.created_at >= two_weeks_ago
#     ).distinct().all()
#
#     active_user_ids = [user_id for (user_id,) in active_user_ids]
#
#     return User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()
#
#
# def calculate_user_percentage(is_admin):
#     total_count = User.query.count()
#     if total_count == 0:
#         return 0
#     admin_count = User.query.filter_by(is_admin=is_admin).count()
#     return round((admin_count / total_count) * 100)
#
#
# def calculate_new_user_percentage():
#     total_count = User.query.count()
#     if total_count == 0:
#         return 0
#     new_user_count = User.query.filter(
#         User.created_at >= (datetime.now() - timedelta(days=30))
#     ).count()
#     return round((new_user_count / total_count) * 100)
#
#
# def get_top_users(limit=5):
#     # Get users with most notes
#     users_with_counts = db.session.query(
#         User,
#         func.count(Note.id).label('notes_count')
#     ).outerjoin(User.notes).group_by(User.id).order_by(
#         func.count(Note.id).desc()
#     ).limit(limit).all()
#
#     result = []
#     for user, notes_count in users_with_counts:
#         # Count opportunities associated with user
#         opportunities_count = db.session.query(func.count(Opportunity.id)).filter(
#             Opportunity.created_by_id == user.id  # Changed from created_by to created_by_id
#         ).scalar() or 0
#
#         # Create a dictionary with user and additional attributes
#         user_dict = user.__dict__.copy()
#         user_dict['notes_count'] = notes_count
#         user_dict['opportunities_count'] = opportunities_count
#
#         result.append(user_dict)
#
#     return result
#
#
# def prepare_activity_data():
#     # Generate activity data for the past 6 months
#     labels = []
#     notes = []
#     opportunities = []
#     logins = []
#
#     current_month = datetime.now().month
#     current_year = datetime.now().year
#
#     for i in range(6):
#         month = (current_month - i) % 12
#         if month == 0:
#             month = 12
#         year = current_year - ((current_month - i) // 12)
#
#         # Month name for label
#         month_name = datetime(year, month, 1).strftime("%b %Y")
#         labels.append(month_name)
#
#         # Get actual notes count for this month
#         notes_count = db.session.query(func.count(Note.id)).filter(
#             extract('month', Note.created_at) == month,
#             extract('year', Note.created_at) == year
#         ).scalar() or 0
#         notes.append(notes_count)
#
#         # Get opportunities count for this month
#         opportunities_count = db.session.query(func.count(Opportunity.id)).filter(
#             extract('month', Opportunity.created_at) == month,
#             extract('year', Opportunity.created_at) == year
#         ).scalar() or 0
#         opportunities.append(opportunities_count)
#
#         # For logins, we'll use random sample data (in a real app, this would come from login logs)
#         logins.append(random.randint(20, 100))
#
#     # Reverse the lists to get chronological order
#     labels.reverse()
#     notes.reverse()
#     opportunities.reverse()
#     logins.reverse()
#
#     return {"labels": labels, "notes": notes, "opportunities": opportunities, "logins": logins}
#
#
# @users_bp.route("/filtered", methods=["GET"])
# @login_required
# def filtered_users():
#     # Get filter parameters
#     is_admin = request.args.get("is_admin")
#     period = request.args.get("period")
#     activity = request.args.get("activity")
#
#     # Start with base query
#     query = User.query
#
#     # Apply filters if provided
#     if is_admin:
#         is_admin_bool = is_admin.lower() == 'true'
#         query = query.filter_by(is_admin=is_admin_bool)
#
#     if period:
#         if period == 'month':
#             query = query.filter(User.created_at >= (datetime.now() - timedelta(days=30)))
#         elif period == 'quarter':
#             query = query.filter(User.created_at >= (datetime.now() - timedelta(days=90)))
#         elif period == 'year':
#             query = query.filter(User.created_at >= (datetime.now() - timedelta(days=365)))
#
#     # Base users
#     filtered_users = query.order_by(User.created_at.desc()).all()
#
#     # Apply activity filter - this is more complex and done after query execution
#     if activity:
#         # Get note counts for all users
#         user_notes = {}
#         for user in filtered_users:
#             note_count = Note.query.filter_by(user_id=user.id).count()
#             user_notes[user.id] = note_count
#
#         # Sort users by note count
#         all_note_counts = sorted(user_notes.values())
#
#         # Determine thresholds for high, medium, low activity
#         if all_note_counts:
#             max_notes = max(all_note_counts)
#             high_threshold = max_notes * 0.7
#             medium_threshold = max_notes * 0.3
#
#             # Filter users by activity level
#             if activity == 'high':
#                 filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) >= high_threshold]
#             elif activity == 'medium':
#                 filtered_users = [user for user in filtered_users
#                                   if medium_threshold <= user_notes.get(user.id, 0) < high_threshold]
#             elif activity == 'low':
#                 filtered_users = [user for user in filtered_users if user_notes.get(user.id, 0) < medium_threshold]
#
#     # Prepare user data with counts
#     users = []
#     for user in filtered_users:
#         user_dict = user.__dict__.copy()
#         user_dict['notes_count'] = Note.query.filter_by(user_id=user.id).count()
#         user_dict['opportunities_count'] = db.session.query(func.count(Opportunity.id)).filter(
#             Opportunity.created_by_id == user.id  # Changed from created_by to created_by_id
#         ).scalar() or 0
#         users.append(user_dict)
#
#     return render_template(
#         "pages/users/filtered.html",
#         users=users,
#         filters={"is_admin": is_admin, "period": period, "activity": activity}
#     )
#
#
# @users_bp.route("/statistics", methods=["GET"])
# @login_required
# def statistics():
#     # Get overall statistics
#     total_users = User.query.count()
#     regular_users = User.query.filter_by(is_admin=False).count()
#     admin_users = User.query.filter_by(is_admin=True).count()
#
#     # Calculate inactive users
#     two_weeks_ago = datetime.now() - timedelta(days=14)
#     active_user_ids = db.session.query(Note.user_id).filter(
#         Note.created_at >= two_weeks_ago
#     ).distinct().all()
#     active_user_ids = [user_id for (user_id,) in active_user_ids]
#     inactive_users = User.query.filter(~User.id.in_(active_user_ids)).count() if active_user_ids else User.query.count()
#
#     # Calculate average activity per user
#     total_notes = db.session.query(func.count(Note.id)).scalar() or 0
#     total_opportunities = db.session.query(func.count(Opportunity.id)).scalar() or 0
#     avg_activity_per_user = (total_notes + total_opportunities) / total_users if total_users > 0 else 0
#
#     # Calculate user activity by role
#     user_activity_by_role = []
#
#     # Admin users
#     admin_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == True).scalar() or 0
#     admin_opportunities = db.session.query(func.count(Opportunity.id)).join(
#         User, Opportunity.created_by_id == User.id  # Changed from created_by to created_by_id
#     ).filter(User.is_admin == True).scalar() or 0
#
#     user_activity_by_role.append({
#         "role": "admin",
#         "count": admin_users,
#         "notes": admin_notes,
#         "opportunities": admin_opportunities
#     })
#
#     # Regular users
#     regular_notes = db.session.query(func.count(Note.id)).join(User).filter(User.is_admin == False).scalar() or 0
#     regular_opportunities = db.session.query(func.count(Opportunity.id)).join(
#         User, Opportunity.created_by_id == User.id  # Changed from created_by to created_by_id
#     ).filter(User.is_admin == False).scalar() or 0
#
#     user_activity_by_role.append({
#         "role": "regular",
#         "count": regular_users,
#         "notes": regular_notes,
#         "opportunities": regular_opportunities
#     })
#
#     # Calculate monthly activity for the past 12 months
#     monthly_data = []
#     current_month = datetime.now().month
#     current_year = datetime.now().year
#
#     for i in range(12):
#         month = (current_month - i) % 12
#         if month == 0:
#             month = 12
#         year = current_year - ((current_month - i) // 12)
#
#         # Month name for label
#         month_name = datetime(year, month, 1).strftime("%b %Y")
#
#         # Count of new users for this month
#         new_users = User.query.filter(
#             extract('month', User.created_at) == month,
#             extract('year', User.created_at) == year
#         ).count()
#
#         # Count of notes created for this month
#         notes = db.session.query(func.count(Note.id)).filter(
#             extract('month', Note.created_at) == month,
#             extract('year', Note.created_at) == year
#         ).scalar() or 0
#
#         # Count of opportunities created for this month
#         opportunities = db.session.query(func.count(Opportunity.id)).filter(
#             extract('month', Opportunity.created_at) == month,
#             extract('year', Opportunity.created_at) == year
#         ).scalar() or 0
#
#         monthly_data.append({
#             "month": month_name,
#             "new_users": new_users,
#             "notes": notes,
#             "opportunities": opportunities
#         })
#
#     # Reverse the list to get chronological order
#     monthly_data.reverse()
#
#     return render_template(
#         "pages/users/statistics.html",
#         total_users=total_users,
#         regular_users=regular_users,
#         admin_users=admin_users,
#         inactive_users=inactive_users,
#         avg_activity_per_user=avg_activity_per_user,
#         user_activity_by_role=user_activity_by_role,
#         monthly_data=monthly_data,
#     )
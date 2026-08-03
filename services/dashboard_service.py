"""Business logic for the dashboard — aggregated stats and analytics."""

from datetime import date, timedelta

from bson import ObjectId

from app.database import get_database
from app.exceptions import AuthorizationError, InvalidIdError, NotFoundError
from app.logger import get_logger

logger = get_logger(__name__)


def _to_oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise InvalidIdError(value)
    return ObjectId(value)


async def _build_goal_dashboard(goal: dict) -> dict:
    """Build dashboard data for a single goal."""
    db = get_database()
    goal_id = goal["_id"]
    today = date.today()

    # Timeline info
    target_str = goal.get("timeline", {}).get("target_date")
    target_date = date.fromisoformat(target_str) if target_str else today
    days_remaining = max((target_date - today).days, 0)

    progress = goal.get("progress_percent", 0.0)
    hiker_position = round(progress / 100.0, 3)

    # ETA estimate based on current velocity
    eta = None
    if progress > 0:
        start_str = goal.get("timeline", {}).get("start_date")
        if start_str:
            start_date = date.fromisoformat(start_str)
            days_elapsed = max((today - start_date).days, 1)
            rate_per_day = progress / days_elapsed
            if rate_per_day > 0:
                days_to_finish = (100 - progress) / rate_per_day
                eta = (today + timedelta(days=int(days_to_finish))).isoformat()

    on_track = eta is None or (eta and eta <= target_date.isoformat())

    # Streak calculation
    streak = 0
    check_date = today
    log_dates_cursor = db["progress_logs"].find(
        {"goal_id": goal_id}, {"date": 1}
    )
    log_dates = set()
    async for doc in log_dates_cursor:
        log_dates.add(doc["date"])

    while check_date.isoformat() in log_dates:
        streak += 1
        check_date -= timedelta(days=1)

    # Current milestone (first non-completed one)
    current_milestone = None
    plan = await db["plans"].find_one({"goal_id": goal_id})
    if plan and plan.get("milestones"):
        for m in sorted(plan["milestones"], key=lambda x: x.get("order", 0)):
            if m.get("status") != "completed":
                current_milestone = {
                    "title": m["title"],
                    "progress_percent": m.get("progress_percent", 0.0),
                }
                break

    # Weekly hours (last 4 weeks)
    weekly_hours = []
    for i in range(4):
        week_end = today - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        total = 0.0
        async for log in db["progress_logs"].find({
            "goal_id": goal_id,
            "date": {
                "$gte": week_start.isoformat(),
                "$lte": week_end.isoformat(),
            },
        }):
            total += log["entries"].get("hours_spent", 0)
        weekly_hours.insert(0, round(total, 1))

    # Progress history (weekly snapshots)
    progress_history = []
    async for log in db["progress_logs"].find({"goal_id": goal_id}).sort("date", 1):
        progress_history.append({
            "date": log["date"],
            "percent": goal.get("progress_percent", 0.0),
        })

    return {
        "goal_id": str(goal_id),
        "title": goal["title"],
        "progress_percent": progress,
        "hiker_position": hiker_position,
        "days_remaining": days_remaining,
        "eta": eta,
        "deadline": target_date.isoformat(),
        "on_track": on_track,
        "streak_days": streak,
        "current_milestone": current_milestone,
        "weekly_hours": weekly_hours,
        "progress_history": progress_history,
    }


async def get_dashboard(user_id: str) -> dict:
    """Get the full dashboard for a user."""
    db = get_database()
    uid = ObjectId(user_id)

    # Active goals
    cursor = db["goals"].find({"user_id": uid, "status": "active"})
    goals = []
    goal_titles_needing_checkin = []
    today_str = date.today().isoformat()

    async for goal in cursor:
        dashboard = await _build_goal_dashboard(goal)
        goals.append(dashboard)

        # Check if today's check-in is pending
        today_log = await db["progress_logs"].find_one({
            "goal_id": goal["_id"],
            "date": today_str,
        })
        if not today_log:
            goal_titles_needing_checkin.append(goal["title"])

    # Today's tasks from plans
    tasks_due = []
    for goal_data in goals:
        if goal_data.get("current_milestone"):
            tasks_due.append(f"{goal_data['title']}: {goal_data['current_milestone']['title']}")

    return {
        "active_goals": len(goals),
        "goals": goals,
        "today": {
            "pending_checkins": goal_titles_needing_checkin,
            "tasks_due": tasks_due,
        },
    }


async def get_goal_dashboard(user_id: str, goal_id: str) -> dict:
    """Get detailed analytics for a single goal."""
    db = get_database()
    goid = _to_oid(goal_id)

    goal = await db["goals"].find_one({"_id": goid})
    if not goal:
        raise NotFoundError("Goal", goal_id)
    if str(goal["user_id"]) != user_id:
        raise AuthorizationError()

    return await _build_goal_dashboard(goal)

"""
Progress Manager for Adaptive Learning Coach
Utility functions for managing LEARNING_PROGRESS.json
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DEFAULT_PROGRESS = {
    "version": 1,
    "currentTrack": "backend",
    "currentLevel": 0,
    "currentPhase": 1,
    "currentTaskId": None,
    "completedTasks": [],
    "taughtTasks": [],
    "strugglingTasks": {},
    "masterySchedule": {},
    "confidenceRatings": {},
    "quizHistory": [],
    "attemptLog": {},
    "currentTeachingSession": None,
    "lastSessionDate": None,
    "sessionCount": 0,
    "totalMinutesLearned": 0,
    "consecutiveDays": 0,
    "lastSessionDuration": 0,
    "settings": {
        "sessionTargetMinutes": 30,
        "interleaveRatio": 0.25,
        "showHintsAfterAttempts": 2,
        "teachingDepth": "auto"
    }
}

SPACED_REPETITION_INTERVALS = [1, 3, 7, 14, 30, 60, 120]


def get_progress_path() -> Path:
    """Get path to LEARNING_PROGRESS.json"""
    return Path("docs/LEARNING_PROGRESS.json")


def load_progress() -> dict:
    """Load progress file, create if missing"""
    path = get_progress_path()
    
    if not path.exists():
        save_progress(DEFAULT_PROGRESS)
        return DEFAULT_PROGRESS.copy()
    
    with open(path, 'r') as f:
        data = json.load(f)
        if "taughtTasks" not in data:
            data["taughtTasks"] = []
        if "currentTeachingSession" not in data:
            data["currentTeachingSession"] = None
        return data


def save_progress(progress: dict) -> None:
    """Save progress file"""
    path = get_progress_path()
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(progress, f, indent=2)


def is_new_task(progress: dict, task_id: str) -> bool:
    """Check if task is NEW (never completed, not in mastery schedule)"""
    return task_id not in progress.get("completedTasks", []) and \
           task_id not in progress.get("masterySchedule", {})


def is_review_task(progress: dict, task_id: str) -> bool:
    """Check if task is REVIEW (already completed, due for spaced repetition)"""
    return task_id in progress.get("completedTasks", [])


def is_struggling_task(progress: dict, task_id: str) -> bool:
    """Check if task is STRUGGLING (marked as struggling, needs recovery)"""
    struggles = progress.get("strugglingTasks", {})
    return task_id in struggles and struggles[task_id].get("count", 0) >= 2


def get_task_type(progress: dict, task_id: str) -> str:
    """Determine task type: 'new', 'review', or 'struggling'"""
    if is_struggling_task(progress, task_id):
        return "struggling"
    elif is_review_task(progress, task_id):
        return "review"
    else:
        return "new"


def mark_task_taught(progress: dict, task_id: str) -> dict:
    """Mark task as having received teaching (may not be complete)"""
    taught = progress.get("taughtTasks", [])
    if task_id not in taught:
        taught.append(task_id)
    progress["taughtTasks"] = taught
    return progress


def start_teaching_session(progress: dict, task_id: str) -> dict:
    """Start a teaching session for a task"""
    progress["currentTeachingSession"] = {
        "taskId": task_id,
        "phase": "teaching",
        "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    progress["currentTaskId"] = task_id
    return progress


def update_teaching_phase(progress: dict, phase: str) -> dict:
    """Update current teaching session phase: 'teaching', 'qa', 'quiz'"""
    if progress.get("currentTeachingSession"):
        progress["currentTeachingSession"]["phase"] = phase
    return progress


def end_teaching_session(progress: dict) -> dict:
    """End current teaching session"""
    if progress.get("currentTeachingSession"):
        task_id = progress["currentTeachingSession"]["taskId"]
        mark_task_taught(progress, task_id)
        progress["currentTeachingSession"] = None
    return progress


def get_teaching_session_status(progress: dict) -> Optional[dict]:
    """Get current teaching session status"""
    return progress.get("currentTeachingSession")


def update_session_start(progress: dict) -> dict:
    """Update progress at session start"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if progress["lastSessionDate"]:
        last = datetime.strptime(progress["lastSessionDate"], "%Y-%m-%d")
        now = datetime.strptime(today, "%Y-%m-%d")
        days_diff = (now - last).days
        
        if days_diff == 1:
            progress["consecutiveDays"] += 1
        elif days_diff > 1:
            progress["consecutiveDays"] = 1
    else:
        progress["consecutiveDays"] = 1
    
    progress["lastSessionDate"] = today
    progress["sessionCount"] += 1
    
    return progress


def mark_task_completed(progress: dict, task_id: str) -> dict:
    """Mark task as completed (passed quiz)"""
    if task_id not in progress.get("completedTasks", []):
        progress["completedTasks"].append(task_id)
    
    if task_id in progress.get("strugglingTasks", {}):
        del progress["strugglingTasks"][task_id]
    
    return progress


def mark_task_struggling(progress: dict, task_id: str, reason: str = "quiz_failed") -> dict:
    """Mark task as struggling"""
    if task_id not in progress.get("strugglingTasks", {}):
        progress["strugglingTasks"][task_id] = {
            "count": 0,
            "lastFailed": None,
            "reasons": []
        }
    
    progress["strugglingTasks"][task_id]["count"] += 1
    progress["strugglingTasks"][task_id]["lastFailed"] = datetime.now().strftime("%Y-%m-%d")
    progress["strugglingTasks"][task_id]["reasons"].append(reason)
    
    return progress


def clear_task_struggle(progress: dict, task_id: str) -> dict:
    """Clear struggle status for task"""
    if task_id in progress.get("strugglingTasks", {}):
        del progress["strugglingTasks"][task_id]
    
    return progress


def get_struggle_count(progress: dict, task_id: str) -> int:
    """Get struggle count for a task"""
    struggles = progress.get("strugglingTasks", {})
    if task_id in struggles:
        return struggles[task_id].get("count", 0)
    return 0


def update_mastery_schedule(progress: dict, task_id: str, passed: bool, confidence: int) -> dict:
    """Update spaced repetition mastery schedule"""
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    if task_id not in progress.get("masterySchedule", {}):
        progress["masterySchedule"][task_id] = {
            "strength": 0.0,
            "nextReview": today_str,
            "interval": 0
        }
    
    mastery = progress["masterySchedule"][task_id]
    
    if passed and confidence >= 3:
        mastery["strength"] = min(1.0, mastery["strength"] + 0.15)
        
        current_interval = mastery["interval"]
        if current_interval in SPACED_REPETITION_INTERVALS:
            idx = SPACED_REPETITION_INTERVALS.index(current_interval)
            next_idx = min(idx + 1, len(SPACED_REPETITION_INTERVALS) - 1)
            mastery["interval"] = SPACED_REPETITION_INTERVALS[next_idx]
        else:
            mastery["interval"] = SPACED_REPETITION_INTERVALS[0]
        
        next_review = today + timedelta(days=mastery["interval"])
        mastery["nextReview"] = next_review.strftime("%Y-%m-%d")
    
    elif not passed:
        mastery["strength"] = max(0.0, mastery["strength"] - 0.2)
        mastery["interval"] = 1
        mastery["nextReview"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    return progress


def get_due_reviews(progress: dict) -> list:
    """Get tasks due for spaced repetition review"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    due = []
    for task_id, mastery in progress.get("masterySchedule", {}).items():
        if mastery["nextReview"] <= today:
            due.append(task_id)
    
    return due


def get_high_struggle_tasks(progress: dict) -> list:
    """Get tasks with high struggle count (>= 3)"""
    high = []
    for task_id, struggle in progress.get("strugglingTasks", {}).items():
        if struggle["count"] >= 3:
            high.append(task_id)
    
    return high


def get_medium_struggle_tasks(progress: dict) -> list:
    """Get tasks with medium struggle count (>= 2)"""
    medium = []
    for task_id, struggle in progress.get("strugglingTasks", {}).items():
        if struggle["count"] >= 2:
            medium.append(task_id)
    
    return medium


def record_confidence_rating(progress: dict, task_id: str, rating: int, passed: bool) -> dict:
    """Record confidence rating with quiz outcome"""
    if task_id not in progress.get("confidenceRatings", {}):
        progress["confidenceRatings"][task_id] = []
    
    entry = {
        "rating": rating,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "passed": passed,
        "gap": rating >= 4 and not passed
    }
    
    progress["confidenceRatings"][task_id].append(entry)
    
    return progress


def record_quiz_attempt(progress: dict, task_id: str, quiz_type: str, passed: bool, confidence: int) -> dict:
    """Record quiz attempt in history"""
    entry = {
        "taskId": task_id,
        "type": quiz_type,
        "passed": passed,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "confidenceBefore": confidence
    }
    
    progress["quizHistory"].append(entry)
    
    if task_id not in progress.get("attemptLog", {}):
        progress["attemptLog"][task_id] = []
    
    progress["attemptLog"][task_id].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": quiz_type,
        "outcome": "passed" if passed else "failed"
    })
    
    return progress


def get_next_task(progress: dict, plan_tasks: list) -> Optional[str]:
    """Determine next task based on priority algorithm"""
    high_struggle = get_high_struggle_tasks(progress)
    due_reviews = get_due_reviews(progress)
    
    if high_struggle:
        return high_struggle[0]
    
    if due_reviews:
        return due_reviews[0]
    
    completed = set(progress.get("completedTasks", []))
    for task in plan_tasks:
        if task not in completed:
            return task
    
    return None


def get_progress_summary(progress: dict) -> dict:
    """Generate progress summary stats"""
    struggle_count = len(progress.get("strugglingTasks", {}))
    due_reviews = len(get_due_reviews(progress))
    high_struggle = len(get_high_struggle_tasks(progress))
    taught_count = len(progress.get("taughtTasks", []))
    
    avg_mastery = 0
    if progress.get("masterySchedule"):
        strengths = [m["strength"] for m in progress["masterySchedule"].values()]
        avg_mastery = sum(strengths) / len(strengths)
    
    confidence_gaps = 0
    for ratings in progress.get("confidenceRatings", {}).values():
        for r in ratings:
            if r.get("gap"):
                confidence_gaps += 1
    
    return {
        "track": progress.get("currentTrack", "backend"),
        "level": progress.get("currentLevel", 0),
        "phase": progress.get("currentPhase", 1),
        "completed_count": len(progress.get("completedTasks", [])),
        "taught_count": taught_count,
        "struggle_count": struggle_count,
        "high_struggle_count": high_struggle,
        "due_reviews": due_reviews,
        "avg_mastery": round(avg_mastery, 2),
        "confidence_gaps": confidence_gaps,
        "session_count": progress.get("sessionCount", 0),
        "total_minutes": progress.get("totalMinutesLearned", 0),
        "streak": progress.get("consecutiveDays", 0),
        "current_task_type": get_task_type(progress, progress.get("currentTaskId", "")) if progress.get("currentTaskId") else None
    }


def reset_progress() -> dict:
    """Reset all progress to defaults"""
    progress = DEFAULT_PROGRESS.copy()
    save_progress(progress)
    return progress


def get_interleaved_topic(progress: dict, current_task_id: str, plan_tasks: list) -> Optional[str]:
    """Select an interleaved topic (random previous concept)"""
    completed = progress.get("completedTasks", [])
    mastered = list(progress.get("masterySchedule", {}).keys())
    
    candidates = [t for t in completed + mastered 
                  if t != current_task_id and t in plan_tasks]
    
    if not candidates:
        return None
    
    weak_mastery = []
    for t in candidates:
        mastery = progress.get("masterySchedule", {}).get(t, {})
        if mastery.get("strength", 0) < 0.7:
            weak_mastery.append(t)
    
    if weak_mastery:
        import random
        return random.choice(weak_mastery)
    
    import random
    return random.choice(candidates)


if __name__ == "__main__":
    print("Progress Manager - Adaptive Learning Coach")
    print("=" * 40)
    
    progress = load_progress()
    summary = get_progress_summary(progress)
    
    print(f"Track: {summary['track']}")
    print(f"Level: {summary['level']}")
    print(f"Phase: {summary['phase']}")
    print(f"Completed: {summary['completed_count']} tasks")
    print(f"Taught: {summary['taught_count']} topics")
    print(f"Struggling: {summary['struggle_count']} tasks")
    print(f"Due reviews: {summary['due_reviews']}")
    print(f"Average mastery: {summary['avg_mastery']}")
    print(f"Streak: {summary['streak']} days")
    print(f"Sessions: {summary['session_count']}")
    
    if summary['current_task_type']:
        print(f"Current task type: {summary['current_task_type']}")
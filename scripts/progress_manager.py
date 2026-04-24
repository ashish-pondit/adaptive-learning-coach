"""
Progress Manager for Adaptive Learning Coach
SQLite-based progress tracking with JSON export for git-friendly snapshots.
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from .schema import (
        get_connection,
        close_connection,
        get_db_path,
        get_export_path,
        SPACED_REPETITION_INTERVALS,
    )
except ImportError:
    from schema import (
        get_connection,
        close_connection,
        get_db_path,
        get_export_path,
        SPACED_REPETITION_INTERVALS,
    )


class ProgressManager:
    """Manages learning progress using SQLite database."""
    
    def __init__(self, skill_dir: Optional[Path] = None):
        self.skill_dir = skill_dir or Path(__file__).parent.parent
        self.db_path = get_db_path(self.skill_dir)
        self.export_path = get_export_path(self.skill_dir)
        self._conn = None
    
    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = get_connection(self.db_path)
        return self._conn
    
    def _close(self) -> None:
        if self._conn:
            close_connection(self._conn)
            self._conn = None
    
    def _row_to_dict(self, row: sqlite3.Row, columns: List[str]) -> Dict:
        return {col: row[i] for i, col in enumerate(columns)}
    
    def export_to_json(self) -> Dict:
        """Export database to JSON for git-friendly snapshot."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export = {
            "version": 1,
            "exported_at": datetime.now().isoformat(),
            "repos": [],
            "learning_plans": [],
            "topics": [],
            "mastery": [],
            "struggles": [],
            "sessions": [],
            "quiz_history": [],
            "confidence_ratings": [],
            "module_cache": [],
        }
        
        cursor.execute("SELECT * FROM repos")
        for row in cursor.fetchall():
            export["repos"].append(dict(row))
        
        cursor.execute("SELECT * FROM learning_plans")
        for row in cursor.fetchall():
            export["learning_plans"].append(dict(row))
        
        cursor.execute("SELECT * FROM topics")
        for row in cursor.fetchall():
            export["topics"].append(dict(row))
        
        cursor.execute("SELECT * FROM mastery")
        for row in cursor.fetchall():
            export["mastery"].append(dict(row))
        
        cursor.execute("SELECT * FROM struggles")
        for row in cursor.fetchall():
            export["struggles"].append(dict(row))
        
        cursor.execute("SELECT * FROM sessions ORDER BY started_at DESC LIMIT 50")
        for row in cursor.fetchall():
            export["sessions"].append(dict(row))
        
        cursor.execute("SELECT * FROM quiz_history ORDER BY date DESC LIMIT 100")
        for row in cursor.fetchall():
            export["quiz_history"].append(dict(row))
        
        cursor.execute("SELECT * FROM confidence_ratings ORDER BY date DESC LIMIT 100")
        for row in cursor.fetchall():
            export["confidence_ratings"].append(dict(row))
        
        cursor.execute("SELECT * FROM module_cache")
        for row in cursor.fetchall():
            export["module_cache"].append(dict(row))
        
        with open(self.export_path, 'w') as f:
            json.dump(export, f, indent=2)
        
        return export
    
    def import_from_json(self, json_path: Optional[Path] = None) -> bool:
        """Import from JSON export (backward compatibility)."""
        if json_path is None:
            json_path = self.export_path
        
        if not json_path.exists():
            return False
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if "repos" in data:
            for repo in data["repos"]:
                cursor.execute(
                    """INSERT OR IGNORE INTO repos 
                    (id, path, name, context, primary_language, created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        repo.get("id"),
                        repo.get("path"),
                        repo.get("name"),
                        repo.get("context", "existing"),
                        repo.get("primary_language"),
                        repo.get("created_at"),
                        repo.get("last_accessed"),
                    )
                )
        
        if "learning_plans" in data:
            for plan in data["learning_plans"]:
                cursor.execute(
                    """INSERT OR IGNORE INTO learning_plans
                    (id, repo_id, name, plan_type, source, experience_level, timeline, goals, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        plan.get("id"),
                        plan.get("repo_id"),
                        plan.get("name"),
                        plan.get("plan_type"),
                        plan.get("source", "generated"),
                        plan.get("experience_level", "intermediate"),
                        plan.get("timeline"),
                        plan.get("goals"),
                        plan.get("created_at"),
                        plan.get("is_active", 1),
                    )
                )
        
        conn.commit()
        return True
    
    def register_repo(self, path: str, name: str, context: str = "existing", 
                      primary_language: Optional[str] = None) -> int:
        """Register a repo/project for learning tracking."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT OR REPLACE INTO repos 
            (path, name, context, primary_language, last_accessed)
            VALUES (?, ?, ?, ?, ?)""",
            (path, name, context, primary_language, datetime.now().isoformat())
        )
        
        cursor.execute("SELECT id FROM repos WHERE path = ?", (path,))
        repo_id = cursor.fetchone()[0]
        conn.commit()
        self.export_to_json()
        return repo_id
    
    def get_repo(self, path: str) -> Optional[Dict]:
        """Get repo by path."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM repos WHERE path = ?", (path,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_repo(self) -> Optional[Dict]:
        """Get most recently accessed repo."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM repos ORDER BY last_accessed DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_repo_access(self, repo_id: int) -> None:
        """Update repo last_accessed timestamp."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE repos SET last_accessed = ? WHERE id = ?",
            (datetime.now().isoformat(), repo_id)
        )
        conn.commit()
    
    def create_learning_plan(self, repo_id: int, name: str, plan_type: str,
                             source: str = "generated", experience_level: str = "intermediate",
                             timeline: Optional[str] = None, goals: Optional[List[str]] = None) -> int:
        """Create a new learning plan for a repo."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE learning_plans SET is_active = 0 WHERE repo_id = ?", (repo_id,))
        
        goals_json = json.dumps(goals) if goals else None
        
        cursor.execute(
            """INSERT INTO learning_plans
            (repo_id, name, plan_type, source, experience_level, timeline, goals, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (repo_id, name, plan_type, source, experience_level, timeline, goals_json)
        )
        
        plan_id = cursor.lastrowid
        conn.commit()
        self.export_to_json()
        return plan_id
    
    def get_active_plan(self, repo_id: int) -> Optional[Dict]:
        """Get active learning plan for a repo."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM learning_plans WHERE repo_id = ? AND is_active = 1",
            (repo_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_topic(self, plan_id: int, task_id: str, title: str, description: Optional[str] = None,
                  category: str = "core", order_index: int = 0, estimated_minutes: int = 15) -> int:
        """Add a topic/task to a learning plan."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO topics
            (plan_id, task_id, title, description, category, order_index, estimated_minutes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'new')""",
            (plan_id, task_id, title, description, category, order_index, estimated_minutes)
        )
        
        topic_id = cursor.lastrowid
        conn.commit()
        self.export_to_json()
        return topic_id
    
    def get_topic(self, plan_id: int, task_id: str) -> Optional[Dict]:
        """Get topic by plan_id and task_id."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM topics WHERE plan_id = ? AND task_id = ?",
            (plan_id, task_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_topics_by_plan(self, plan_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all topics for a plan, optionally filtered by status."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM topics WHERE plan_id = ? AND status = ? ORDER BY order_index",
                (plan_id, status)
            )
        else:
            cursor.execute(
                "SELECT * FROM topics WHERE plan_id = ? ORDER BY order_index",
                (plan_id,)
            )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_topic_status(self, topic_id: int, status: str) -> None:
        """Update topic status: new, in_progress, completed, struggling."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE topics SET status = ? WHERE id = ?",
            (status, topic_id)
        )
        conn.commit()
        self.export_to_json()
    
    def get_next_topic(self, plan_id: int) -> Optional[Dict]:
        """Get next topic to work on based on priority algorithm."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT t.id, t.plan_id, t.task_id, t.title, t.status,
                      s.count as struggle_count
               FROM topics t
               LEFT JOIN struggles s ON t.id = s.topic_id
               WHERE t.plan_id = ? AND t.status IN ('new', 'in_progress', 'struggling')
               ORDER BY 
                 CASE WHEN s.count >= 3 THEN 0 ELSE 1 END,
                 CASE WHEN t.status = 'struggling' THEN 0 ELSE 1 END,
                 CASE WHEN t.status = 'in_progress' THEN 0 ELSE 1 END,
                 t.order_index
               LIMIT 1""",
            (plan_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_due_reviews(self, plan_id: int) -> List[Dict]:
        """Get topics due for spaced repetition review."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute(
            """SELECT t.id, t.plan_id, t.task_id, t.title, 
                      m.strength, m.next_review, m.interval
               FROM topics t
               JOIN mastery m ON t.id = m.topic_id
               WHERE t.plan_id = ? AND t.status = 'completed' 
                     AND m.next_review <= ?
               ORDER BY m.next_review ASC""",
            (plan_id, today)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_high_struggle_topics(self, plan_id: int, min_count: int = 3) -> List[Dict]:
        """Get topics with high struggle count."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT t.id, t.plan_id, t.task_id, t.title, s.count, s.last_failed, s.reasons
               FROM topics t
               JOIN struggles s ON t.id = s.topic_id
               WHERE t.plan_id = ? AND s.count >= ?
               ORDER BY s.count DESC""",
            (plan_id, min_count)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_interleaved_topic(self, plan_id: int, current_task_id: str) -> Optional[Dict]:
        """Select an interleaved topic (random previous with weak mastery)."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT t.id, t.plan_id, t.task_id, t.title, m.strength
               FROM topics t
               JOIN mastery m ON t.id = m.topic_id
               WHERE t.plan_id = ? AND t.task_id != ? 
                     AND t.status = 'completed' AND m.strength < 0.7
               ORDER BY RANDOM() LIMIT 1""",
            (plan_id, current_task_id)
        )
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        cursor.execute(
            """SELECT t.id, t.plan_id, t.task_id, t.title, m.strength
               FROM topics t
               JOIN mastery m ON t.id = m.topic_id
               WHERE t.plan_id = ? AND t.task_id != ? AND t.status = 'completed'
               ORDER BY RANDOM() LIMIT 1""",
            (plan_id, current_task_id)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def record_struggle(self, topic_id: int, reason: str = "quiz_failed") -> None:
        """Record a struggle event for a topic."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT OR IGNORE INTO struggles (topic_id, count, last_failed, reasons)
            VALUES (?, 0, NULL, '[]')""",
            (topic_id,)
        )
        
        cursor.execute(
            """SELECT reasons FROM struggles WHERE topic_id = ?""",
            (topic_id,)
        )
        reasons_json = cursor.fetchone()[0]
        reasons = json.loads(reasons_json) if reasons_json else []
        reasons.append({"reason": reason, "date": datetime.now().isoformat()})
        
        cursor.execute(
            """UPDATE struggles SET 
            count = count + 1, 
            last_failed = ?, 
            reasons = ?
            WHERE topic_id = ?""",
            (datetime.now().strftime("%Y-%m-%d"), json.dumps(reasons), topic_id)
        )
        
        cursor.execute(
            "UPDATE topics SET status = 'struggling' WHERE id = ?",
            (topic_id,)
        )
        
        conn.commit()
        self.export_to_json()
    
    def clear_struggle(self, topic_id: int) -> None:
        """Clear struggle status for a topic."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM struggles WHERE topic_id = ?", (topic_id,))
        conn.commit()
        self.export_to_json()
    
    def get_struggle_count(self, topic_id: int) -> int:
        """Get struggle count for a topic."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT count FROM struggles WHERE topic_id = ?",
            (topic_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def update_mastery(self, topic_id: int, passed: bool, confidence: int = 3) -> None:
        """Update mastery schedule for spaced repetition."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        
        cursor.execute(
            """INSERT OR IGNORE INTO mastery (topic_id, strength, interval, next_review, last_review)
            VALUES (?, 0.0, 0, ?, NULL)""",
            (topic_id, today_str)
        )
        
        if passed and confidence >= 3:
            cursor.execute(
                """SELECT strength, interval FROM mastery WHERE topic_id = ?""",
                (topic_id,)
            )
            result = cursor.fetchone()
            current_strength = result[0]
            current_interval = result[1]
            
            new_strength = min(1.0, current_strength + 0.15)
            
            if current_interval in SPACED_REPETITION_INTERVALS:
                idx = SPACED_REPETITION_INTERVALS.index(current_interval)
                next_idx = min(idx + 1, len(SPACED_REPETITION_INTERVALS) - 1)
                new_interval = SPACED_REPETITION_INTERVALS[next_idx]
            else:
                new_interval = SPACED_REPETITION_INTERVALS[0]
            
            next_review = today + timedelta(days=new_interval)
            
            cursor.execute(
                """UPDATE mastery SET 
                strength = ?, 
                interval = ?, 
                next_review = ?, 
                last_review = ?
                WHERE topic_id = ?""",
                (new_strength, new_interval, next_review.strftime("%Y-%m-%d"), 
                 today_str, topic_id)
            )
        
        elif not passed:
            cursor.execute(
                """UPDATE mastery SET 
                strength = MAX(0.0, strength - 0.2), 
                interval = 1, 
                next_review = ?
                WHERE topic_id = ?""",
                ((today + timedelta(days=1)).strftime("%Y-%m-%d"), topic_id)
            )
        
        conn.commit()
        self.export_to_json()
    
    def start_session(self, repo_id: int, plan_id: int) -> int:
        """Start a new learning session."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        self.update_repo_access(repo_id)
        
        cursor.execute(
            """INSERT INTO sessions (repo_id, plan_id, started_at)
            VALUES (?, ?, ?)""",
            (repo_id, plan_id, datetime.now().isoformat())
        )
        
        session_id = cursor.lastrowid
        conn.commit()
        return session_id
    
    def end_session(self, session_id: int, topics_covered: Optional[List[int]] = None,
                    confidence_avg: Optional[float] = None) -> None:
        """End a learning session."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT started_at FROM sessions WHERE id = ?",
            (session_id,)
        )
        started_at = cursor.fetchone()[0]
        
        started_dt = datetime.fromisoformat(started_at)
        duration = int((datetime.now() - started_dt).total_seconds() / 60)
        
        topics_json = json.dumps(topics_covered) if topics_covered else None
        
        cursor.execute(
            """UPDATE sessions SET 
            ended_at = ?, 
            duration_minutes = ?, 
            topics_covered = ?, 
            confidence_avg = ?
            WHERE id = ?""",
            (datetime.now().isoformat(), duration, topics_json, confidence_avg, session_id)
        )
        
        conn.commit()
        self.export_to_json()
    
    def record_quiz(self, session_id: int, topic_id: int, quiz_type: str,
                    passed: bool, confidence_before: Optional[int] = None) -> int:
        """Record a quiz attempt."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO quiz_history 
            (session_id, topic_id, quiz_type, passed, confidence_before)
            VALUES (?, ?, ?, ?, ?)""",
            (session_id, topic_id, quiz_type, int(passed), confidence_before)
        )
        
        quiz_id = cursor.lastrowid
        
        if confidence_before:
            gap_detected = 1 if confidence_before >= 4 and not passed else 0
            cursor.execute(
                """INSERT INTO confidence_ratings 
                (topic_id, rating, passed, gap_detected)
                VALUES (?, ?, ?, ?)""",
                (topic_id, confidence_before, int(passed), gap_detected)
            )
        
        conn.commit()
        self.export_to_json()
        return quiz_id
    
    def mark_topic_completed(self, topic_id: int) -> None:
        """Mark topic as completed (passed quiz)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE topics SET status = 'completed' WHERE id = ?",
            (topic_id,)
        )
        
        cursor.execute("DELETE FROM struggles WHERE topic_id = ?", (topic_id,))
        
        conn.commit()
        self.export_to_json()
    
    def get_progress_summary(self, plan_id: int) -> Dict:
        """Generate progress summary for a plan."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) as total FROM topics WHERE plan_id = ?",
            (plan_id,)
        )
        total_topics = cursor.fetchone()["total"]
        
        cursor.execute(
            "SELECT COUNT(*) as count FROM topics WHERE plan_id = ? AND status = 'completed'",
            (plan_id,)
        )
        completed_count = cursor.fetchone()["count"]
        
        cursor.execute(
            "SELECT COUNT(*) as count FROM topics WHERE plan_id = ? AND status = 'struggling'",
            (plan_id,)
        )
        struggling_count = cursor.fetchone()["count"]
        
        cursor.execute(
            """SELECT COUNT(*) as count FROM mastery m
            JOIN topics t ON m.topic_id = t.id
            WHERE t.plan_id = ? AND m.next_review <= ?""",
            (plan_id, datetime.now().strftime("%Y-%m-%d"))
        )
        due_reviews = cursor.fetchone()["count"]
        
        cursor.execute(
            """SELECT AVG(strength) as avg FROM mastery m
            JOIN topics t ON m.topic_id = t.id
            WHERE t.plan_id = ?""",
            (plan_id,)
        )
        avg_strength = cursor.fetchone()["avg"] or 0.0
        
        cursor.execute(
            """SELECT COUNT(*) as count FROM confidence_ratings cr
            JOIN topics t ON cr.topic_id = t.id
            WHERE t.plan_id = ? AND cr.gap_detected = 1""",
            (plan_id,)
        )
        confidence_gaps = cursor.fetchone()["count"]
        
        cursor.execute(
            """SELECT COUNT(*) as count, SUM(duration_minutes) as total_minutes
            FROM sessions WHERE plan_id = ?""",
            (plan_id,)
        )
        session_stats = cursor.fetchone()
        session_count = session_stats["count"]
        total_minutes = session_stats["total_minutes"] or 0
        
        return {
            "plan_id": plan_id,
            "total_topics": total_topics,
            "completed_count": completed_count,
            "completion_percent": round(completed_count / total_topics * 100, 1) if total_topics > 0 else 0,
            "struggling_count": struggling_count,
            "due_reviews": due_reviews,
            "avg_mastery_strength": round(avg_strength, 2),
            "confidence_gaps": confidence_gaps,
            "session_count": session_count,
            "total_minutes": total_minutes,
        }
    
    def write_plan_to_file(self, plan_id: int, output_path: Optional[Path] = None,
                           repo_path: Optional[str] = None) -> Path:
        """
        Write learning plan to a markdown file.
        
        Args:
            plan_id: The plan ID to write
            output_path: Optional custom output path (default: .agents/LEARNING_PLAN.md)
            repo_path: Optional repo path to determine default location
        
        Returns:
            Path to the written file
        """
        if output_path is None:
            if repo_path:
                output_path = Path(repo_path) / ".agents" / "LEARNING_PLAN.md"
            else:
                output_path = self.skill_dir / "storage" / "LEARNING_PLAN.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT lp.*, r.name as repo_name, r.path as repo_path
               FROM learning_plans lp
               JOIN repos r ON lp.repo_id = r.id
               WHERE lp.id = ?""",
            (plan_id,)
        )
        plan = cursor.fetchone()
        
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        topics = self.get_topics_by_plan(plan_id)
        
        goals = json.loads(plan["goals"]) if plan["goals"] else []
        
        content = self._generate_plan_markdown(plan, topics, goals)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_plan_markdown(self, plan: Dict, topics: List[Dict], goals: List[str]) -> str:
        """Generate markdown content for a learning plan."""
        lines = [
            f"# Learning Plan: {plan['name']}",
            "",
            "## Metadata",
            "",
            f"- **Plan ID**: {plan['id']}",
            f"- **Repo**: {plan['repo_name']}",
            f"- **Type**: {plan['plan_type']}",
            f"- **Experience Level**: {plan['experience_level']}",
            f"- **Timeline**: {plan['timeline'] or 'Flexible'}",
            f"- **Created**: {plan['created_at']}",
            "",
        ]
        
        if goals:
            lines.append("## Goals")
            lines.append("")
            for goal in goals:
                lines.append(f"- {goal}")
            lines.append("")
        
        lines.append("## Learning Topics")
        lines.append("")
        
        current_phase = None
        phase_totals = {}
        
        for topic in topics:
            category = topic.get("category", "core")
            if category != current_phase:
                if current_phase:
                    lines.append("")
                phase_name = category.capitalize()
                phase_totals[phase_name] = 0
                lines.append(f"### Phase: {phase_name}")
                lines.append("")
                current_phase = category
            
            task_id = topic["task_id"]
            title = topic["title"]
            est_min = topic.get("estimated_minutes", 20)
            status = topic.get("status", "new")
            
            status_icon = {"new": "⬜", "in_progress": "🔄", "completed": "✅", "struggling": "❌"}
            icon = status_icon.get(status, "⬜")
            
            lines.append(f"{icon} **{task_id}** - {title} (_{est_min} min_)")
            phase_totals[phase_name] += est_min
        
        lines.append("")
        lines.append("## Time Estimates")
        lines.append("")
        
        total_time = sum(t.get("estimated_minutes", 20) for t in topics)
        lines.append(f"- **Total**: ~{total_time} minutes ({round(total_time/60, 1)} hours)")
        
        for phase, mins in phase_totals.items():
            lines.append(f"- **{phase}**: ~{mins} minutes")
        
        lines.append("")
        lines.append("## Usage")
        lines.append("")
        lines.append("To use this plan with the Adaptive Learning Coach skill:")
        lines.append("")
        lines.append("``")
        lines.append("- \"give me a task\" - Get next task to work on")
        lines.append("- \"progress\" - Check your progress")
        lines.append("- \"explain [topic]\" - Get help with a specific topic")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"_Generated by Adaptive Learning Coach | Plan ID: {plan['id']}_")
        
        return "\n".join(lines)
    
    def verify_tracking_initialized(self, plan_id: int) -> Dict:
        """
        Verify that tracking is properly initialized for a plan.
        
        Returns dict with verification status and details.
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT lp.*, r.id as repo_id, r.name as repo_name
               FROM learning_plans lp
               JOIN repos r ON lp.repo_id = r.id
               WHERE lp.id = ?""",
            (plan_id,)
        )
        plan = cursor.fetchone()
        
        if not plan:
            return {"initialized": False, "error": "Plan not found"}
        
        cursor.execute(
            "SELECT COUNT(*) as count FROM topics WHERE plan_id = ?",
            (plan_id,)
        )
        topic_count = cursor.fetchone()["count"]
        
        return {
            "initialized": True,
            "repo_id": plan["repo_id"],
            "repo_name": plan["repo_name"],
            "plan_id": plan_id,
            "plan_name": plan["name"],
            "topic_count": topic_count,
            "is_active": plan["is_active"],
        }
    
    def get_streak(self, repo_id: int) -> int:
        """Calculate consecutive days streak."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT DATE(started_at) as day FROM sessions 
            WHERE repo_id = ? ORDER BY started_at DESC""",
            (repo_id,)
        )
        days = [row[0] for row in cursor.fetchall()]
        
        if not days:
            return 0
        
        streak = 0
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        unique_days = sorted(set(days), reverse=True)
        
        if unique_days[0] == today or unique_days[0] == yesterday:
            streak = 1
            for i in range(1, len(unique_days)):
                prev_date = datetime.strptime(unique_days[i-1], "%Y-%m-%d")
                curr_date = datetime.strptime(unique_days[i], "%Y-%m-%d")
                if (prev_date - curr_date).days == 1:
                    streak += 1
                else:
                    break
        
        return streak
    
    def get_topic_type(self, topic_id: int) -> str:
        """Determine topic type: new, review, or struggling."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM topics WHERE id = ?", (topic_id,))
        result = cursor.fetchone()
        status = result[0] if result else "new"
        
        if status == "struggling":
            return "struggling"
        
        if status == "completed":
            return "review"
        
        return "new"
    
    def reset_progress(self, repo_id: Optional[int] = None, plan_id: Optional[int] = None) -> None:
        """Reset progress for a repo or plan."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if plan_id:
            cursor.execute("UPDATE topics SET status = 'new' WHERE plan_id = ?", (plan_id,))
            cursor.execute(
                """DELETE FROM mastery WHERE topic_id IN 
                (SELECT id FROM topics WHERE plan_id = ?)""",
                (plan_id,)
            )
            cursor.execute(
                """DELETE FROM struggles WHERE topic_id IN 
                (SELECT id FROM topics WHERE plan_id = ?)""",
                (plan_id,)
            )
            cursor.execute(
                """DELETE FROM quiz_history WHERE topic_id IN 
                (SELECT id FROM topics WHERE plan_id = ?)""",
                (plan_id,)
            )
            cursor.execute(
                """DELETE FROM confidence_ratings WHERE topic_id IN 
                (SELECT id FROM topics WHERE plan_id = ?)""",
                (plan_id,)
            )
        elif repo_id:
            cursor.execute(
                """DELETE FROM mastery WHERE topic_id IN 
                (SELECT t.id FROM topics t JOIN learning_plans lp ON t.plan_id = lp.id 
                WHERE lp.repo_id = ?)""",
                (repo_id,)
            )
            cursor.execute(
                """DELETE FROM struggles WHERE topic_id IN 
                (SELECT t.id FROM topics t JOIN learning_plans lp ON t.plan_id = lp.id 
                WHERE lp.repo_id = ?)""",
                (repo_id,)
            )
            cursor.execute(
                """UPDATE topics SET status = 'new' WHERE plan_id IN 
                (SELECT id FROM learning_plans WHERE repo_id = ?)""",
                (repo_id,)
            )
        
        conn.commit()
        self.export_to_json()
    
    def delete_repo(self, repo_id: int) -> None:
        """Delete a repo and all its data."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM repos WHERE id = ?", (repo_id,))
        conn.commit()
        self.export_to_json()


_progress_manager_instance: Optional[ProgressManager] = None


def get_progress_manager(skill_dir: Optional[Path] = None) -> ProgressManager:
    """Get singleton ProgressManager instance."""
    global _progress_manager_instance
    if _progress_manager_instance is None:
        _progress_manager_instance = ProgressManager(skill_dir)
    return _progress_manager_instance


if __name__ == "__main__":
    print("Progress Manager Test")
    print("=" * 50)
    
    pm = ProgressManager()
    
    repo_id = pm.register_repo("/test/project", "test-project", "existing", "python")
    print(f"Registered repo: {repo_id}")
    
    plan_id = pm.create_learning_plan(
        repo_id, "Test Plan", "new_topic",
        experience_level="intermediate",
        timeline="2_weeks",
        goals=["Learn basics", "Build something"]
    )
    print(f"Created plan: {plan_id}")
    
    pm.add_topic(plan_id, "1.1", "Introduction", "Get started", "foundation", 0, 10)
    pm.add_topic(plan_id, "1.2", "Core Concepts", "Understand core", "core", 1, 20)
    pm.add_topic(plan_id, "2.1", "Advanced", "Deep dive", "advanced", 2, 30)
    print("Added 3 topics")
    
    session_id = pm.start_session(repo_id, plan_id)
    print(f"Started session: {session_id}")
    
    summary = pm.get_progress_summary(plan_id)
    print(f"\nProgress summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    export = pm.export_to_json()
    print(f"\nExported to JSON: {len(export['repos'])} repos, {len(export['topics'])} topics")
    
    print("\nAll tests passed!")
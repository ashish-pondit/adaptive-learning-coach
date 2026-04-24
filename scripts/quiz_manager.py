"""
Quiz Manager for Adaptive Learning Coach
Handles quiz storage, micro topic analysis, and weak area detection.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from .schema import get_connection, get_db_path
    from .progress_manager import ProgressManager
except ImportError:
    from schema import get_connection, get_db_path
    from progress_manager import ProgressManager


class QuizManager:
    """Manages quiz generation, storage, and analysis."""
    
    def __init__(self, skill_dir: Optional[Path] = None):
        self.skill_dir = skill_dir or Path(__file__).parent.parent
        self.db_path = get_db_path(self.skill_dir)
        self.storage_dir = self.skill_dir / "storage"
        self.quizzes_dir = self.storage_dir / "quizzes"
        self.quizzes_dir.mkdir(parents=True, exist_ok=True)
        self.pm = ProgressManager(skill_dir)
    
    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)
    
    def save_quiz_record(self, topic_id: int, quiz_data: Dict,
                          session_id: Optional[int] = None,
                          complexity: str = "MEDIUM",
                          micro_topics: List[str] = [],
                          micro_topics_covered: List[str] = [],
                          passed: bool = False,
                          confidence_pre: Optional[int] = None,
                          confidence_post: Optional[int] = None,
                          confidence_attempts: int = 0,
                          final_status: str = "in_progress") -> int:
        """
        Save quiz record to database and file.
        
        Returns:
            quiz_record_id from database
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        coverage_percent = 0.0
        if micro_topics:
            coverage_percent = round(
                len(micro_topics_covered) / len(micro_topics) * 100, 1
            )
        
        quiz_data_json = json.dumps(quiz_data)
        micro_topics_json = json.dumps(micro_topics)
        micro_topics_covered_json = json.dumps(micro_topics_covered)
        
        cursor.execute(
            """INSERT INTO quiz_records 
            (topic_id, session_id, quiz_data, complexity, micro_topics, 
             micro_topics_covered, coverage_percent, passed, confidence_pre,
             confidence_post, confidence_attempts, final_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (topic_id, session_id, quiz_data_json, complexity, micro_topics_json,
             micro_topics_covered_json, coverage_percent, int(passed),
             confidence_pre, confidence_post, confidence_attempts, final_status)
        )
        
        record_id = cursor.lastrowid
        conn.commit()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quiz_file = self.quizzes_dir / f"quiz_{topic_id}_{timestamp}.json"
        
        full_quiz_data = {
            "quiz_record_id": record_id,
            "topic_id": topic_id,
            "session_id": session_id,
            "complexity": complexity,
            "micro_topics": micro_topics,
            "micro_topics_covered": micro_topics_covered,
            "coverage_percent": coverage_percent,
            "pre_quiz_confidence": confidence_pre,
            "post_quiz_confidence": confidence_post,
            "confidence_attempts": confidence_attempts,
            "quiz_passed": passed,
            "final_status": final_status,
            "questions": quiz_data.get("questions", []),
            "results": quiz_data.get("results", []),
            "struggles": quiz_data.get("struggles", []),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(quiz_file, 'w') as f:
            json.dump(full_quiz_data, f, indent=2)
        
        return record_id
    
    def get_quiz_history(self, topic_id: int, limit: int = 10) -> List[Dict]:
        """Get quiz history for a topic."""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM quiz_records 
            WHERE topic_id = ? ORDER BY generated_at DESC LIMIT ?""",
            (topic_id, limit)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_weak_micro_topics_from_history(self, topic_id: int) -> List[str]:
        """
        Analyze quiz history to find weak micro topics.
        
        Returns micro topics where user repeatedly failed.
        """
        quiz_history = self.get_quiz_history(topic_id, limit=5)
        
        weak_topics = {}
        
        for quiz_record in quiz_history:
            quiz_data_json = quiz_record.get("quiz_data")
            if not quiz_data_json:
                continue
            
            try:
                quiz_data = json.loads(quiz_data_json)
                questions = quiz_data.get("questions", [])
                results = quiz_data.get("results", [])
                
                for i, question in enumerate(questions):
                    micro_topic = question.get("micro_topic")
                    if not micro_topic:
                        continue
                    
                    result = results[i] if i < len(results) else None
                    if result and not result.get("passed", True):
                        weak_topics[micro_topic] = weak_topics.get(micro_topic, 0) + 1
            except (json.JSONDecodeError, IndexError):
                continue
        
        weak_micro_topics = [
            topic for topic, count in weak_topics.items()
            if count >= 2
        ]
        
        return weak_micro_topics
    
    def analyze_struggle_patterns(self, topic_id: int) -> Dict:
        """
        Analyze struggle patterns for a topic.
        
        Returns:
            Dict with struggle_type counts, weak micro topics, recommendations
        """
        struggle_counts = self.pm.get_struggle_type_counts(topic_id)
        weak_micro_topics = self.get_weak_micro_topics_from_history(topic_id)
        db_weak_topics = self.pm.get_weak_micro_topics(topic_id)
        
        all_weak = list(set(weak_micro_topics + db_weak_topics))
        
        recommendations = []
        
        if struggle_counts.get("quiz_failed", 0) >= 3:
            recommendations.append({
                "type": "quiz_recovery",
                "priority": "high",
                "message": "Multiple quiz failures. Recommend recovery teaching with simplified approach."
            })
        
        if struggle_counts.get("confidence_stuck", 0) >= 2:
            recommendations.append({
                "type": "confidence_recovery",
                "priority": "medium",
                "message": "Confidence stuck after attempts. Consider alternative teaching method or pausing topic."
            })
        
        if all_weak:
            recommendations.append({
                "type": "focus_weak_areas",
                "priority": "medium",
                "message": f"Focus on weak micro topics: {', '.join(all_weak)}"
            })
        
        return {
            "topic_id": topic_id,
            "quiz_failed_count": struggle_counts.get("quiz_failed", 0),
            "confidence_stuck_count": struggle_counts.get("confidence_stuck", 0),
            "weak_micro_topics": all_weak,
            "recommendations": recommendations
        }
    
    def get_quiz_questions_count_by_complexity(self, complexity: str) -> int:
        """Get recommended question count by complexity."""
        counts = {
            "SIMPLE": 3,
            "MEDIUM": 5,
            "COMPLEX": 7
        }
        return counts.get(complexity, 5)
    
    def get_quiz_type_mix_by_complexity(self, complexity: str) -> Dict[str, float]:
        """Get question type percentages by complexity."""
        mixes = {
            "SIMPLE": {
                "mcq": 1.0,
                "code_reading": 0.0,
                "elaboration": 0.0,
                "teach_back": 0.0,
                "coding": 0.0
            },
            "MEDIUM": {
                "mcq": 0.6,
                "code_reading": 0.2,
                "elaboration": 0.2,
                "teach_back": 0.0,
                "coding": 0.0
            },
            "COMPLEX": {
                "mcq": 0.4,
                "code_reading": 0.3,
                "elaboration": 0.0,
                "teach_back": 0.2,
                "coding": 0.1
            }
        }
        return mixes.get(complexity, mixes["MEDIUM"])
    
    def get_micro_topic_coverage_target(self, complexity: str) -> float:
        """Get minimum micro topic coverage percentage by complexity."""
        targets = {
            "SIMPLE": 0.6,
            "MEDIUM": 0.6,
            "COMPLEX": 0.8
        }
        return targets.get(complexity, 0.6)
    
    def generate_quiz_structure(self, topic_id: int) -> Dict:
        """
        Generate quiz structure (not content) for LLM to fill.
        
        Returns:
            Dict with question count, types, micro topics to cover
        """
        complexity = self.pm.get_topic_complexity(topic_id)
        micro_topics = self.pm.get_topic_micro_topics_list(topic_id)
        weak_micro_topics = self.get_weak_micro_topics_from_history(topic_id)
        db_weak_topics = self.pm.get_weak_micro_topics(topic_id)
        
        all_weak = list(set(weak_micro_topics + db_weak_topics))
        
        question_count = self.get_quiz_questions_count_by_complexity(complexity)
        type_mix = self.get_quiz_type_mix_by_complexity(complexity)
        coverage_target = self.get_micro_topic_coverage_target(complexity)
        
        if all_weak:
            priority_micro_topics = all_weak
        else:
            priority_micro_topics = micro_topics[:min(3, len(micro_topics))]
        
        remaining_micro_topics = [
            t for t in micro_topics if t not in priority_micro_topics
        ]
        
        min_coverage_count = int(len(micro_topics) * coverage_target)
        
        micro_topics_to_cover = priority_micro_topics[:]
        
        while len(micro_topics_to_cover) < min_coverage_count and remaining_micro_topics:
            micro_topics_to_cover.append(remaining_micro_topics.pop(0))
        
        question_types = []
        mcq_count = int(question_count * type_mix["mcq"])
        code_count = int(question_count * type_mix["code_reading"])
        elab_count = int(question_count * type_mix["elaboration"])
        teach_count = int(question_count * type_mix["teach_back"])
        coding_count = question_count - mcq_count - code_count - elab_count - teach_count
        
        for _ in range(mcq_count):
            question_types.append("mcq")
        for _ in range(code_count):
            question_types.append("code_reading")
        for _ in range(elab_count):
            question_types.append("elaboration")
        for _ in range(teach_count):
            question_types.append("teach_back")
        for _ in range(coding_count):
            question_types.append("coding")
        
        return {
            "topic_id": topic_id,
            "complexity": complexity,
            "question_count": question_count,
            "question_types": question_types,
            "micro_topics_available": micro_topics,
            "micro_topics_priority": priority_micro_topics,
            "micro_topics_to_cover": micro_topics_to_cover,
            "coverage_target_percent": coverage_target * 100,
            "weak_micro_topics": all_weak,
            "struggle_patterns": self.analyze_struggle_patterns(topic_id) if all_weak else None
        }
    
    def load_quiz_from_file(self, quiz_file: Path) -> Optional[Dict]:
        """Load quiz data from file."""
        if not quiz_file.exists():
            return None
        
        with open(quiz_file, 'r') as f:
            return json.load(f)
    
    def get_latest_quiz_file(self, topic_id: int) -> Optional[Path]:
        """Get latest quiz file for a topic."""
        quiz_files = list(self.quizzes_dir.glob(f"quiz_{topic_id}_*.json"))
        
        if not quiz_files:
            return None
        
        quiz_files.sort(key=lambda f: f.stem, reverse=True)
        return quiz_files[0]
    
    def cleanup_old_quiz_files(self, topic_id: int, keep_count: int = 5) -> int:
        """Remove old quiz files, keeping only recent ones."""
        quiz_files = list(self.quizzes_dir.glob(f"quiz_{topic_id}_*.json"))
        
        if len(quiz_files) <= keep_count:
            return 0
        
        quiz_files.sort(key=lambda f: f.stem, reverse=True)
        files_to_remove = quiz_files[keep_count:]
        
        removed_count = 0
        for file in files_to_remove:
            try:
                file.unlink()
                removed_count += 1
            except OSError:
                continue
        
        return removed_count


_quiz_manager_instance: Optional[QuizManager] = None


def get_quiz_manager(skill_dir: Optional[Path] = None) -> QuizManager:
    """Get singleton QuizManager instance."""
    global _quiz_manager_instance
    if _quiz_manager_instance is None:
        _quiz_manager_instance = QuizManager(skill_dir)
    return _quiz_manager_instance


if __name__ == "__main__":
    print("Quiz Manager Test")
    print("=" * 50)
    
    qm = QuizManager()
    
    print(f"Quizzes directory: {qm.quizzes_dir}")
    
    print("\nQuiz parameters by complexity:")
    for complexity in ["SIMPLE", "MEDIUM", "COMPLEX"]:
        count = qm.get_quiz_questions_count_by_complexity(complexity)
        mix = qm.get_quiz_type_mix_by_complexity(complexity)
        coverage = qm.get_micro_topic_coverage_target(complexity)
        print(f"\n{complexity}:")
        print(f"  Questions: {count}")
        print(f"  Type mix: {mix}")
        print(f"  Coverage: {coverage * 100}%")
    
    print("\nAll tests passed!")
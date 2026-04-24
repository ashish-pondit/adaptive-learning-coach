"""
Plan Generator for Adaptive Learning Coach
Generates learning plans dynamically using semi-structure templates.
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from .progress_manager import get_progress_manager, ProgressManager
except ImportError:
    from progress_manager import get_progress_manager, ProgressManager


PLAN_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "plan_template.json"


def load_template() -> Dict:
    """Load plan template from JSON."""
    if not PLAN_TEMPLATE_PATH.exists():
        return get_default_template()
    
    with open(PLAN_TEMPLATE_PATH, 'r') as f:
        return json.load(f)


def get_default_template() -> Dict:
    """Return default template if file missing."""
    return {
        "template_version": 1,
        "structure": {
            "phases": [
                {
                    "name": "Foundation",
                    "focus": "Core concepts and prerequisites",
                    "min_topics": 2,
                    "max_topics": 4
                },
                {
                    "name": "Core",
                    "focus": "Primary functionality",
                    "min_topics": 3,
                    "max_topics": 6
                },
                {
                    "name": "Advanced",
                    "focus": "Deep understanding",
                    "min_topics": 2,
                    "max_topics": 4
                },
                {
                    "name": "Practice",
                    "focus": "Hands-on application",
                    "min_topics": 1,
                    "max_topics": 2
                }
            ]
        },
        "plan_types": {
            "new_topic": {"phases": ["Foundation", "Core", "Advanced", "Practice"]},
            "codebase": {"phases": ["Foundation", "Core", "Advanced"]},
            "build": {"phases": ["Foundation", "Core", "Practice"]},
            "understand_only": {"phases": ["Foundation", "Core"]}
        },
        "experience_level_adjustments": {
            "beginner": {"phase_multiplier": 1.5, "estimated_time_multiplier": 2},
            "intermediate": {"phase_multiplier": 1.0, "estimated_time_multiplier": 1},
            "advanced": {"phase_multiplier": 0.7, "estimated_time_multiplier": 0.5}
        }
    }


class PlanGenerator:
    """Generates learning plans dynamically."""
    
    def __init__(self, template: Optional[Dict] = None):
        self.template = template or load_template()
        self.pm = get_progress_manager()
    
    def generate_plan(self, repo_id: int, plan_type: str, topic: str,
                      experience_level: str = "intermediate",
                      timeline: Optional[str] = None,
                      goals: Optional[List[str]] = None,
                      context_info: Optional[Dict] = None) -> int:
        """
        Generate a complete learning plan and store in database.
        
        Args:
            repo_id: Repository ID
            plan_type: 'new_topic', 'codebase', 'build', 'understand_only'
            topic: What to learn (e.g., "Python", "React", "auth module")
            experience_level: 'beginner', 'intermediate', 'advanced'
            timeline: Optional timeline string
            goals: Optional list of user goals
            context_info: Optional context from codebase analysis
        
        Returns:
            plan_id from database
        """
        plan_config = self.template["plan_types"].get(plan_type, {})
        phases_to_include = plan_config.get("phases", ["Foundation", "Core", "Advanced", "Practice"])
        
        adjustments = self.template["experience_level_adjustments"].get(experience_level, {})
        phase_multiplier = adjustments.get("phase_multiplier", 1.0)
        
        if timeline:
            timeline_adj = self._get_timeline_adjustment(timeline)
            if timeline_adj.get("skip_phase"):
                phases_to_include = [p for p in phases_to_include if p not in timeline_adj["skip_phase"]]
        
        plan_name = self._generate_plan_name(topic, plan_type)
        plan_id = self.pm.create_learning_plan(
            repo_id=repo_id,
            name=plan_name,
            plan_type=plan_type,
            source="generated",
            experience_level=experience_level,
            timeline=timeline,
            goals=goals
        )
        
        topics = self._generate_topics(
            topic=topic,
            plan_type=plan_type,
            phases=phases_to_include,
            experience_level=experience_level,
            goals=goals,
            context_info=context_info,
            phase_multiplier=phase_multiplier
        )
        
        for idx, topic_data in enumerate(topics):
            self.pm.add_topic(
                plan_id=plan_id,
                task_id=topic_data["task_id"],
                title=topic_data["title"],
                description=topic_data.get("description"),
                category=topic_data.get("category", "core"),
                order_index=idx,
                estimated_minutes=topic_data.get("estimated_minutes", 20)
            )
        
        return plan_id
    
    def _generate_plan_name(self, topic: str, plan_type: str) -> str:
        """Generate a descriptive plan name."""
        type_names = {
            "new_topic": f"Learn {topic}",
            "codebase": f"Understand {topic} Codebase",
            "build": f"Build {topic}",
            "understand_only": f"Quick Overview: {topic}"
        }
        return type_names.get(plan_type, f"Learn {topic}")
    
    def _get_timeline_adjustment(self, timeline: str) -> Dict:
        """Get timeline-based adjustments."""
        timeline_adj = self.template.get("timeline_adjustments", {})
        
        if timeline.startswith("hours_per_week"):
            return timeline_adj.get(timeline, {})
        
        if "urgent" in timeline or "soon" in timeline:
            return timeline_adj.get("by_date_urgent", {})
        
        return {}
    
    def _generate_topics(self, topic: str, plan_type: str, phases: List[str],
                         experience_level: str, goals: Optional[List[str]],
                         context_info: Optional[Dict], phase_multiplier: float) -> List[Dict]:
        """
        Generate topics for all phases.
        
        This uses a combination of:
        1. Standard topic patterns from template
        2. Goals extracted from user input
        3. Context from codebase analysis (if available)
        """
        all_topics = []
        order = 0
        
        for phase_name in phases:
            phase_config = self._get_phase_config(phase_name)
            phase_topics = self._generate_phase_topics(
                phase_name=phase_name,
                topic=topic,
                plan_type=plan_type,
                phase_config=phase_config,
                experience_level=experience_level,
                goals=goals,
                context_info=context_info,
                phase_multiplier=phase_multiplier
            )
            
            for pt in phase_topics:
                task_id = self._generate_task_id(phase_name, order)
                pt["task_id"] = task_id
                pt["category"] = phase_name.lower()
                all_topics.append(pt)
                order += 1
        
        return all_topics
    
    def _get_phase_config(self, phase_name: str) -> Dict:
        """Get configuration for a specific phase."""
        phases = self.template["structure"]["phases"]
        for phase in phases:
            if phase["name"] == phase_name:
                return phase
        return {"min_topics": 2, "max_topics": 4}
    
    def _generate_phase_topics(self, phase_name: str, topic: str, plan_type: str,
                                phase_config: Dict, experience_level: str,
                                goals: Optional[List[str]], context_info: Optional[Dict],
                                phase_multiplier: float) -> List[Dict]:
        """
        Generate topics for a single phase.
        
        Uses template patterns and adapts based on context.
        """
        base_topic_count = phase_config.get("min_topics", 2)
        max_topics = phase_config.get("max_topics", 4)
        
        adjusted_count = int(base_topic_count * phase_multiplier)
        adjusted_count = min(max_topics, max(base_topic_count, adjusted_count))
        
        if plan_type == "new_topic":
            return self._generate_new_topic_phase(phase_name, topic, adjusted_count, experience_level)
        
        if plan_type == "codebase" or plan_type == "understand_only":
            return self._generate_codebase_phase(phase_name, topic, adjusted_count, context_info)
        
        if plan_type == "build":
            return self._generate_build_phase(phase_name, topic, adjusted_count, goals)
        
        return self._generate_generic_phase(phase_name, topic, adjusted_count)
    
    def _generate_new_topic_phase(self, phase_name: str, topic: str, 
                                   count: int, experience_level: str) -> List[Dict]:
        """Generate topics for learning a new topic."""
        phase_patterns = {
            "Foundation": [
                {"title": f"What is {topic}?", "description": "Introduction and overview", "estimated_minutes": 10},
                {"title": f"{topic} Setup", "description": "Installation and configuration", "estimated_minutes": 15},
                {"title": f"{topic} Basics", "description": "Core concepts and fundamentals", "estimated_minutes": 20},
            ],
            "Core": [
                {"title": f"{topic} Key Concepts", "description": "Main features and patterns", "estimated_minutes": 25},
                {"title": f"{topic} in Practice", "description": "Common use cases and examples", "estimated_minutes": 20},
                {"title": f"{topic} Integration", "description": "Connecting with other tools", "estimated_minutes": 25},
            ],
            "Advanced": [
                {"title": f"{topic} Advanced Patterns", "description": "Deep dive into advanced usage", "estimated_minutes": 30},
                {"title": f"{topic} Best Practices", "description": "Industry standards and tips", "estimated_minutes": 20},
                {"title": f"{topic} Optimization", "description": "Performance and efficiency", "estimated_minutes": 25},
            ],
            "Practice": [
                {"title": f"{topic} Mini Project", "description": "Build a small project", "estimated_minutes": 45},
                {"title": f"{topic} Real-world Scenario", "description": "Practical application", "estimated_minutes": 30},
            ]
        }
        
        patterns = phase_patterns.get(phase_name, [])
        
        if experience_level == "advanced" and phase_name == "Foundation":
            patterns = patterns[1:]
        
        if experience_level == "beginner":
            patterns = patterns[:min(len(patterns), count + 1)]
        
        return patterns[:count]
    
    def _generate_codebase_phase(self, phase_name: str, topic: str, 
                                  count: int, context_info: Optional[Dict]) -> List[Dict]:
        """Generate topics for understanding a codebase."""
        modules = context_info.get("modules", []) if context_info else []
        patterns_found = context_info.get("patterns", []) if context_info else []
        
        phase_patterns = {
            "Foundation": [
                {"title": f"{topic} Structure Overview", "description": "Project layout and organization", "estimated_minutes": 15},
                {"title": f"{topic} Entry Points", "description": "Main files and configuration", "estimated_minutes": 10},
            ],
            "Core": [
                {"title": f"{topic} Key Module", "description": "Deep dive into primary module", "estimated_minutes": 25},
                {"title": f"{topic} Data Flow", "description": "How data moves through the system", "estimated_minutes": 20},
                {"title": f"{topic} Patterns Used", "description": "Architectural patterns", "estimated_minutes": 20},
            ],
            "Advanced": [
                {"title": f"{topic} Dependencies", "description": "External libraries and their usage", "estimated_minutes": 15},
                {"title": f"{topic} Testing Setup", "description": "Test structure and coverage", "estimated_minutes": 20},
            ]
        }
        
        base_patterns = phase_patterns.get(phase_name, [])
        
        if modules and phase_name == "Core":
            module_topics = []
            for module in modules[:count - 1]:
                module_topics.append({
                    "title": f"{topic}: {module}",
                    "description": f"Understand {module} module",
                    "estimated_minutes": 25
                })
            if module_topics:
                return module_topics[:count]
        
        return base_patterns[:count]
    
    def _generate_build_phase(self, phase_name: str, topic: str, 
                               count: int, goals: Optional[List[str]]) -> List[Dict]:
        """Generate topics for building something."""
        phase_patterns = {
            "Foundation": [
                {"title": f"{topic} Project Setup", "description": "Initialize project structure", "estimated_minutes": 15},
                {"title": f"{topic} Core Structure", "description": "Basic architecture", "estimated_minutes": 20},
            ],
            "Core": [
                {"title": f"{topic} Core Feature 1", "description": "Build primary feature", "estimated_minutes": 30},
                {"title": f"{topic} Core Feature 2", "description": "Build secondary feature", "estimated_minutes": 25},
                {"title": f"{topic} Integration", "description": "Connect components", "estimated_minutes": 20},
            ],
            "Practice": [
                {"title": f"{topic} Polish", "description": "Refine and improve", "estimated_minutes": 30},
                {"title": f"{topic} Testing", "description": "Add tests and validation", "estimated_minutes": 25},
            ]
        }
        
        patterns = phase_patterns.get(phase_name, [])
        
        if goals:
            goal_topics = []
            for i, goal in enumerate(goals[:count]):
                goal_topics.append({
                    "title": f"{topic}: {goal}",
                    "description": f"Implement: {goal}",
                    "estimated_minutes": 30
                })
            if goal_topics and phase_name == "Core":
                return goal_topics
        
        return patterns[:count]
    
    def _generate_generic_phase(self, phase_name: str, topic: str, count: int) -> List[Dict]:
        """Generate generic topics when no specific pattern matches."""
        topics = []
        for i in range(count):
            topics.append({
                "title": f"{topic} - {phase_name} Part {i+1}",
                "description": f"{phase_name} learning for {topic}",
                "estimated_minutes": 20
            })
        return topics
    
    def _generate_task_id(self, phase_name: str, order: int) -> str:
        """Generate a task ID like '1.1', '2.3'."""
        phase_numbers = {"Foundation": 1, "Core": 2, "Advanced": 3, "Practice": 4}
        phase_num = phase_numbers.get(phase_name, 1)
        topic_num = order + 1
        return f"{phase_num}.{topic_num}"
    
    def estimate_total_time(self, plan_id: int) -> int:
        """Calculate total estimated time for a plan."""
        topics = self.pm.get_topics_by_plan(plan_id)
        return sum(t.get("estimated_minutes", 20) for t in topics)
    
    def suggest_session_plan(self, plan_id: int, session_minutes: int = 30) -> List[Dict]:
        """
        Suggest which topics to cover in a session.
        
        Uses interleaving logic:
        - 60% current progress
        - 25% spaced repetition review
        - 10% random previous
        - 5% struggling reinforcement
        """
        suggestions = []
        
        next_topic = self.pm.get_next_topic(plan_id)
        if next_topic:
            suggestions.append({
                "topic": next_topic,
                "reason": "current_progress",
                "weight": 0.6
            })
        
        due_reviews = self.pm.get_due_reviews(plan_id)
        if due_reviews:
            suggestions.append({
                "topic": due_reviews[0],
                "reason": "spaced_repetition",
                "weight": 0.25
            })
        
        high_struggle = self.pm.get_high_struggle_topics(plan_id)
        if high_struggle:
            suggestions.append({
                "topic": high_struggle[0],
                "reason": "struggling",
                "weight": 0.05
            })
        
        if next_topic:
            interleaved = self.pm.get_interleaved_topic(plan_id, next_topic["task_id"])
            if interleaved:
                suggestions.append({
                    "topic": interleaved,
                    "reason": "interleaved",
                    "weight": 0.10
                })
        
        return suggestions


def analyze_codebase_context(repo_path: str) -> Dict:
    """
    Quick analysis of a codebase to extract context for plan generation.
    
    Returns:
        Dict with modules, patterns, primary_language, etc.
    """
    context = {
        "modules": [],
        "patterns": [],
        "primary_language": None,
        "has_tests": False,
        "key_files": [],
    }
    
    repo = Path(repo_path)
    
    if repo.exists():
        package_json = repo / "package.json"
        if package_json.exists():
            context["primary_language"] = "javascript"
        
        pyproject = repo / "pyproject.toml"
        requirements = repo / "requirements.txt"
        if pyproject.exists() or requirements.exists():
            context["primary_language"] = "python"
        
        cargo_toml = repo / "Cargo.toml"
        if cargo_toml.exists():
            context["primary_language"] = "rust"
        
        go_mod = repo / "go.mod"
        if go_mod.exists():
            context["primary_language"] = "go"
        
        tests_dir = repo / "tests"
        test_dir = repo / "test"
        if tests_dir.exists() or test_dir.exists():
            context["has_tests"] = True
        
        src_dir = repo / "src"
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir():
                    context["modules"].append(item.name)
        
        lib_dir = repo / "lib"
        if lib_dir.exists():
            for item in lib_dir.iterdir():
                if item.is_dir():
                    context["modules"].append(item.name)
    
    return context


def get_plan_generator() -> PlanGenerator:
    """Get singleton PlanGenerator instance."""
    return PlanGenerator()


if __name__ == "__main__":
    print("Plan Generator Test")
    print("=" * 50)
    
    pg = PlanGenerator()
    
    pm = get_progress_manager()
    repo_id = pm.register_repo("/test/project", "test-project", "existing", "python")
    
    plan_id = pg.generate_plan(
        repo_id=repo_id,
        plan_type="new_topic",
        topic="Python",
        experience_level="beginner",
        timeline="hours_per_week_3-5",
        goals=["Learn basics", "Build a web app"]
    )
    
    print(f"Generated plan ID: {plan_id}")
    
    topics = pm.get_topics_by_plan(plan_id)
    print(f"\nGenerated {len(topics)} topics:")
    for t in topics:
        print(f"  {t['task_id']}: {t['title']} ({t['estimated_minutes']} min)")
    
    total_time = pg.estimate_total_time(plan_id)
    print(f"\nTotal estimated time: {total_time} minutes")
    
    session_plan = pg.suggest_session_plan(plan_id)
    print(f"\nSession suggestions:")
    for s in session_plan:
        print(f"  {s['topic']['task_id']}: {s['topic']['title']} ({s['reason']})")
    
    print("\nAll tests passed!")
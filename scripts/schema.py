"""
SQLite Schema for Adaptive Learning Coach
Handles schema creation, migrations, and version management.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

SCHEMA_VERSION = 2

CREATE_REPOS = """
CREATE TABLE IF NOT EXISTS repos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    context TEXT DEFAULT 'existing',
    primary_language TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_LEARNING_PLANS = """
CREATE TABLE IF NOT EXISTS learning_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    source TEXT DEFAULT 'generated',
    experience_level TEXT DEFAULT 'intermediate',
    timeline TEXT,
    goals TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);
"""

CREATE_TOPICS = """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    task_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'core',
    order_index INTEGER DEFAULT 0,
    estimated_minutes INTEGER DEFAULT 15,
    complexity TEXT DEFAULT 'MEDIUM',
    micro_topics TEXT,
    status TEXT DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, task_id)
);
"""

CREATE_MASTERY = """
CREATE TABLE IF NOT EXISTS mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    strength REAL DEFAULT 0.0,
    interval INTEGER DEFAULT 0,
    next_review DATE,
    last_review DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(topic_id)
);
CREATE INDEX IF NOT EXISTS idx_mastery_review ON mastery(next_review);
CREATE INDEX IF NOT EXISTS idx_mastery_strength ON mastery(strength);
"""

CREATE_STRUGGLES = """
CREATE TABLE IF NOT EXISTS struggles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    count INTEGER DEFAULT 0,
    last_failed DATE,
    reasons TEXT,
    struggle_type TEXT DEFAULT 'quiz_failed',
    micro_topic TEXT,
    attempts INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(topic_id)
);
CREATE INDEX IF NOT EXISTS idx_struggles_count ON struggles(count);
CREATE INDEX IF NOT EXISTS idx_struggles_type ON struggles(struggle_type);
"""

CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    duration_minutes INTEGER,
    topics_covered TEXT,
    confidence_avg REAL
);
"""

CREATE_QUIZ_HISTORY = """
CREATE TABLE IF NOT EXISTS quiz_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    quiz_type TEXT DEFAULT 'concept',
    passed INTEGER DEFAULT 0,
    confidence_before INTEGER,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_quiz_topic ON quiz_history(topic_id);
CREATE INDEX IF NOT EXISTS idx_quiz_date ON quiz_history(date);
"""

CREATE_CONFIDENCE_RATINGS = """
CREATE TABLE IF NOT EXISTS confidence_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    passed INTEGER,
    gap_detected INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_confidence_topic ON confidence_ratings(topic_id);
"""

CREATE_MODULE_CACHE = """
CREATE TABLE IF NOT EXISTS module_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    module_path TEXT NOT NULL,
    analysis_highlevel TEXT,
    analysis_detailed TEXT,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repo_id, module_path)
);
CREATE INDEX IF NOT EXISTS idx_module_path ON module_cache(module_path);
CREATE INDEX IF NOT EXISTS idx_module_analyzed ON module_cache(analyzed_at);
"""

CREATE_CONFIDENCE_HISTORY = """
CREATE TABLE IF NOT EXISTS confidence_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    confidence_pre_quiz INTEGER,
    confidence_post_quiz INTEGER,
    confidence_final INTEGER,
    attempts INTEGER DEFAULT 1,
    improved BOOLEAN DEFAULT 0,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_confidence_history_topic ON confidence_history(topic_id);
CREATE INDEX IF NOT EXISTS idx_confidence_history_improved ON confidence_history(improved);
"""

CREATE_QUIZ_RECORDS = """
CREATE TABLE IF NOT EXISTS quiz_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    quiz_data TEXT NOT NULL,
    complexity TEXT,
    micro_topics TEXT,
    micro_topics_covered TEXT,
    coverage_percent REAL,
    passed INTEGER DEFAULT 0,
    confidence_pre INTEGER,
    confidence_post INTEGER,
    confidence_attempts INTEGER DEFAULT 0,
    final_status TEXT DEFAULT 'in_progress',
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_quiz_records_topic ON quiz_records(topic_id);
CREATE INDEX IF NOT EXISTS idx_quiz_records_status ON quiz_records(final_status);
"""

CREATE_TOPIC_MICRO_TOPICS = """
CREATE TABLE IF NOT EXISTS topic_micro_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    micro_topic TEXT NOT NULL,
    importance INTEGER DEFAULT 1,
    is_weak INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(topic_id, micro_topic)
);
CREATE INDEX IF NOT EXISTS idx_topic_micro_topic ON topic_micro_topics(topic_id);
CREATE INDEX IF NOT EXISTS idx_weak_micro_topics ON topic_micro_topics(is_weak);
"""

CREATE_METADATA = """
CREATE TABLE IF NOT EXISTS schema_metadata (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

ALL_CREATE_STATEMENTS = [
    CREATE_REPOS,
    CREATE_LEARNING_PLANS,
    CREATE_TOPICS,
    CREATE_MASTERY,
    CREATE_STRUGGLES,
    CREATE_SESSIONS,
    CREATE_QUIZ_HISTORY,
    CREATE_CONFIDENCE_RATINGS,
    CREATE_MODULE_CACHE,
    CREATE_CONFIDENCE_HISTORY,
    CREATE_QUIZ_RECORDS,
    CREATE_TOPIC_MICRO_TOPICS,
    CREATE_METADATA,
]

SPACED_REPETITION_INTERVALS = [1, 3, 7, 14, 30, 60, 120]


def get_db_path(skill_dir: Optional[Path] = None) -> Path:
    """Get database path based on skill location."""
    if skill_dir is None:
        skill_dir = Path(__file__).parent.parent
    
    storage_dir = skill_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "learning.db"


def get_export_path(skill_dir: Optional[Path] = None) -> Path:
    """Get JSON export path for git-friendly snapshot."""
    if skill_dir is None:
        skill_dir = Path(__file__).parent.parent
    
    storage_dir = skill_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "progress_export.json"


def init_database(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize database with schema. Returns connection."""
    if db_path is None:
        db_path = get_db_path()
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    
    cursor = conn.cursor()
    
    for statement in ALL_CREATE_STATEMENTS:
        cursor.executescript(statement)
    
    cursor.execute(
        "INSERT OR IGNORE INTO schema_metadata (version) VALUES (?)",
        (SCHEMA_VERSION,)
    )
    
    conn.commit()
    return conn


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_metadata ORDER BY version DESC LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else 0


def needs_migration(conn: sqlite3.Connection) -> bool:
    """Check if database needs migration."""
    return get_schema_version(conn) < SCHEMA_VERSION


def apply_migration(conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
    """Apply migrations between versions."""
    migrations = get_migrations(from_version, to_version)
    
    cursor = conn.cursor()
    for migration in migrations:
        cursor.executescript(migration)
    
    cursor.execute(
        "INSERT OR REPLACE INTO schema_metadata (version, applied_at) VALUES (?, ?)",
        (to_version, datetime.now().isoformat())
    )
    conn.commit()


def get_migrations(from_version: int, to_version: int) -> list:
    """Get migration scripts between versions."""
    migrations = []
    
    if from_version < 1:
        pass
    
    if from_version < 2:
        migrations.extend([
            "ALTER TABLE struggles ADD COLUMN struggle_type TEXT DEFAULT 'quiz_failed'",
            "ALTER TABLE struggles ADD COLUMN micro_topic TEXT",
            "ALTER TABLE struggles ADD COLUMN attempts INTEGER DEFAULT 1",
            "ALTER TABLE topics ADD COLUMN complexity TEXT DEFAULT 'MEDIUM'",
            "ALTER TABLE topics ADD COLUMN micro_topics TEXT",
            CREATE_CONFIDENCE_HISTORY,
            CREATE_QUIZ_RECORDS,
            CREATE_TOPIC_MICRO_TOPICS,
            "CREATE INDEX IF NOT EXISTS idx_struggles_type ON struggles(struggle_type)",
            "CREATE INDEX IF NOT EXISTS idx_confidence_history_topic ON confidence_history(topic_id)",
            "CREATE INDEX IF NOT EXISTS idx_confidence_history_improved ON confidence_history(improved)",
            "CREATE INDEX IF NOT EXISTS idx_quiz_records_topic ON quiz_records(topic_id)",
            "CREATE INDEX IF NOT EXISTS idx_quiz_records_status ON quiz_records(final_status)",
            "CREATE INDEX IF NOT EXISTS idx_topic_micro_topic ON topic_micro_topics(topic_id)",
            "CREATE INDEX IF NOT EXISTS idx_weak_micro_topics ON topic_micro_topics(is_weak)",
        ])
    
    return migrations


def reset_database(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Reset database completely (delete and recreate)."""
    if db_path is None:
        db_path = get_db_path()
    
    if db_path.exists():
        db_path.unlink()
    
    export_path = get_export_path(db_path.parent)
    if export_path.exists():
        export_path.unlink()
    
    return init_database(db_path)


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get database connection, initializing if needed."""
    if db_path is None:
        db_path = get_db_path()
    
    if not db_path.exists():
        return init_database(db_path)
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    
    if needs_migration(conn):
        current_version = get_schema_version(conn)
        apply_migration(conn, current_version, SCHEMA_VERSION)
    
    return conn


def close_connection(conn: sqlite3.Connection) -> None:
    """Close database connection safely."""
    try:
        conn.close()
    except:
        pass


if __name__ == "__main__":
    print("Initializing Adaptive Learning Coach Database...")
    print("=" * 50)
    
    db_path = get_db_path()
    print(f"Database path: {db_path}")
    
    conn = init_database(db_path)
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\nCreated tables: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name
    """)
    indexes = cursor.fetchall()
    print(f"\nIndexes: {len(indexes)}")
    for idx in indexes:
        print(f"  - {idx[0]}")
    
    version = get_schema_version(conn)
    print(f"\nSchema version: {version}")
    
    close_connection(conn)
    print("\nDatabase initialized successfully!")

print("\nSchema Tables:")
print("  - repos: Track learning repos/projects")
print("  - learning_plans: Store generated/imported plans")
print("  - topics: Individual learning tasks (with complexity, micro_topics)")
print("  - mastery: Spaced repetition schedule")
print("  - struggles: Struggle tracking (quiz_failed, confidence_stuck)")
print("  - sessions: Learning session history")
print("  - quiz_history: Quiz attempts")
print("  - confidence_ratings: Pre-quiz metacognitive monitoring")
print("  - confidence_history: Post-quiz confidence tracking")
print("  - quiz_records: Saved quiz data for audit")
print("  - topic_micro_topics: Micro topic breakdown and weakness tracking")
print("  - module_cache: Explain mode analysis cache")
print("  - schema_metadata: Schema version tracking")
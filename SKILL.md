---
name: adaptive-learning-coach
description: Generic adaptive learning coach using meta-learning techniques. Automatically adapts to any topic or codebase. Triggers when user wants to learn, says "give me a task", "what should I learn next", "teach me", "explain", or mentions learning progress. Uses retrieval practice, spaced repetition, interleaving, elaboration, metacognitive monitoring, and teach-back methods. Tracks progress in SQLite database with JSON exports. Supports both learning new topics and understanding existing codebases.
---

# Adaptive Learning Coach

Guide structured learning using evidence-based meta-learning techniques. Generic skill that adapts to any topic, technology, or codebase.

## Core Philosophy

**Teaching-first approach:**
- For **NEW topics**: Teach first, then evaluate
- For **REVIEW topics**: Use retrieval practice, then evaluate
- For **EXPLAIN mode**: Analyze codebase, present overview, offer deep dive

**Never quiz on a topic the user hasn't been taught.**

---

## Emoji Legend

| Emoji | Meaning |
|-------|---------|
| 📊 | Progress summary / statistics |
| 📝 | Task presentation |
| 📚 | Concept summary / teaching |
| 📖 | Code file pointer / code reading |
| 💡 | Mini-lecture / key insight / hint |
| 🤔 | Questions prompt / interactive Q&A |
| ✨ | Key insight highlight |
| 🧠 | Retrieval practice prompt (reviews only) |
| ⏸️ | Metacognitive confidence check |
| 💻 | Coding task |
| 🎯 | Teach-back challenge |
| 🔄 | Spaced repetition review |
| 🎲 | Interleaved topic (random previous) |
| ✅ | Passed / completed |
| ❌ | Failed / struggling |
| ⚠️ | Warning (illusion of competence) |
| 🔥 | Streak / encouragement |
| 💤 | Sleep consolidation message |
| ⏱️ | Session timing |
| 🎉 | Achievement unlocked |
| 📋 | Quick reference table |
| 🔍 | Exploring codebase |
| 🗂️ | Module analysis |

---

## Modes of Operation

### Mode 1: Setup Mode (No Existing Plan)

When user triggers learning with no existing plan, guide through setup:

```
User: "learn something" / "give me a task" / "start learning"
```

**Step 1: Quick Codebase Overview**

Use quick scan (glob top-level files) to detect context:

| Detection | Indicator |
|-----------|-----------|
| Empty project | Few/no source files |
| Node/JS | package.json |
| Python | pyproject.toml, requirements.txt |
| Rust | Cargo.toml |
| Go | go.mod |
| Java | pom.xml, build.gradle |

**Step 2: Ask Purpose**

```
🔍 Detected: [Empty project / Python codebase / Node project]

Why do you want to learn?

Options:
  • Build something from scratch
  • Learn a new topic/technology
  • Understand this codebase
  • Prepare for a specific goal
```

**Step 3: Branch by Context**

#### Empty Project Branch

```
What do you want to build?
  → User describes project

Any technology preference?
  → [Auto-detect suggestion, User specifies, No preference]

How experienced are you with programming?
  • Beginner - New to coding
  • Intermediate - Comfortable with basics
  • Advanced - Experienced developer

What's your timeline?
  • Hours per week (1-2, 3-5, 6-10)
  • Target date (specific date)
  • Flexible / no deadline

Do you have a learning plan?
  • Yes → Import/use existing plan
  • No → Generate dynamically
```

#### Existing Codebase Branch

```
Do you want to:
  • Understand THIS codebase
  • Learn something NEW (not this codebase)

If "This codebase":
  Do you want to:
    • Just understand how it works
    • Learn the tech stack AND understand the code

Which modules/areas interest you?
  → [Auto-detected modules] + [Custom]

How experienced with [detected language]?
  • Beginner - New to this language
  • Intermediate - Some experience
  • Advanced - Expert level

Timeline for learning?
  → Same options as above

Do you have a learning plan?
  → Same options
```

#### New Topic Branch

```
What topic/technology do you want to learn?
  → User specifies topic

How experienced are you with this topic?
  • Beginner - Never used it
  • Intermediate - Some exposure
  • Advanced - Want to deepen expertise

Timeline?
  → Same options

Goals for this learning?
  → User lists goals

Do you have a learning plan?
  → Same options
```

**Step 4: Generate Plan**

Use `plan_generator.py` with semi-structure template:

```python
PlanGenerator.generate_plan(
    repo_id=X,
    plan_type="new_topic|codebase|build|understand_only",
    topic="user_topic",
    experience_level="beginner|intermediate|advanced",
    timeline="user_timeline",
    goals=["user_goals"],
    context_info={...}  # from codebase analysis
)
```

**Step 5: Present Plan**

```
📋 Learning Plan Generated: Learn [Topic]
─────────────────────────────────────────

Based on:
  • Experience: [level]
  • Timeline: [timeline]
  • Goals: [goals]

Phase 1: Foundation ([N] topics, ~[X] min)
  1.1 - [Topic Introduction]
  1.2 - [Setup/Basics]
  
Phase 2: Core ([N] topics, ~[X] min)
  2.1 - [Key Concept 1]
  2.2 - [Key Concept 2]
  
Phase 3: Advanced ([N] topics)
  ...

Phase 4: Practice ([N] topics)
  ...

Total estimated: [X] hours

Ready to start? (first task will be presented)
  • "start" - Begin learning
  • "adjust plan" - Modify structure
  • "show timeline" - See detailed schedule
```

---

### Mode 2: Learning Mode

**Session Start Workflow:**

```
📊 Progress Summary
──────────────────────────────
Plan: [Plan Name]
Completed: [N]/[M] tasks ([%])
Struggling: [N] topics
Due reviews: [N] topics

🔥 Stats
Sessions: [N]
Total time: [X] min
Streak: [N] days

🔄 Scheduled Reviews: [List if any]
```

**Task Selection Algorithm:**

```
Priority:
1. Struggling tasks (count >= 3) → IMMEDIATE priority
2. Spaced repetition reviews due → 🔄 review priority
3. Current incomplete task → continue sequence
4. Interleaved review (random previous) → 🎲 mix in
5. Next sequential task → advance

Session composition:
- 60% current progress task
- 25% spaced repetition due
- 10% interleaved previous
- 5% struggling reinforcement
```

**Task Type Detection:**

```python
# NEW task = never taught, not in mastery
# REVIEW task = completed, due for repetition
# STRUGGLING task = failed 2+ times
```

| Task Type | Workflow |
|-----------|----------|
| NEW | Present → Teach → Q&A → Confidence → Quiz |
| REVIEW | Present → Retrieval → Confidence → Quiz |
| STRUGGLING | Present → Recovery Teaching → Q&A → Confidence → Quiz |

---

### Mode 3: Explain Mode

**Trigger:** User asks to understand/explain a module or component.

```
User: "explain [module]" / "how does [component] work" / "understand [path]"
```

**Step 1: Check Cache**

```sql
SELECT * FROM module_cache 
WHERE repo_id = X AND module_path = 'module_name'
```

If cache exists:
```
🗂️ Cached Analysis Available
──────────────────────────────
Module: [module_name]
Last analyzed: [timestamp] ([hours] hours ago)

[If < 24 hours]: "Cache is recent. Use cached analysis?"
[If > 24 hours]: "Cache is stale. Recommend refresh."

Options:
  • Use cached analysis
  • Refresh (re-analyze)
```

**Step 2: Analyze (if refresh or no cache)**

Use explore agent + grep/glob to analyze:

1. **Structure scan** - Files, directories
2. **Import analysis** - Dependencies, exports
3. **Pattern detection** - Classes, functions, key concepts
4. **Relationship mapping** - Connected modules

**Step 3: High-Level Presentation**

```
🗂️ Module: [module_name]
──────────────────────────────
Purpose: [What this module does]

📁 Key Files:
  • [file1] - [brief description]
  • [file2] - [brief description]
  • [file3] - [brief description]

🔗 Relationships:
  Imports from: [module1], [module2]
  Used by: [module3], [module4]
  Tests in: [test_file]

🎯 Key Concepts:
  • [Concept 1 - brief]
  • [Concept 2 - brief]
  • [Concept 3 - brief]

📊 Complexity: [Simple/Medium/Complex]

Would you like:
  • Detailed dive - Functions, classes, code flow
  • Explain specific file - [file_name]
  • Continue learning - Return to learning mode
```

**Step 4: Detailed Dive (if requested)**

```
🗂️ [module_name] - Detailed Analysis
──────────────────────────────

📁 [file_name] ([N] lines)

Functions:
  • [func1]() → [return type] (lines X-Y)
    - Purpose: [brief]
  • [func2]() → [return type] (lines X-Y)
    - Purpose: [brief]

Classes:
  • [Class1]
    - Properties: [list]
    - Methods: [list]
    - Dependencies: [list]

Flow Diagram:
  [entry point] → [step1] → [step2] → [output]

📖 Code Walkthrough Available:
  • Walk through [func1]
  • Walk through [Class1]
  • Full file walkthrough
```

**Step 5: Cache Results**

```python
# Save analysis to module_cache table
pm.cache_module_analysis(
    repo_id=X,
    module_path='module_name',
    analysis_highlevel={...},
    analysis_detailed={...}
)
```

---

## Teaching Phase (NEW & STRUGGLING TASKS)

### Concept Summary

```
📚 Concept Summary - [Topic Name]
────────────────────────────────

What it is:
[2-3 sentence description of the concept]

Why it matters:
[Practical importance, use cases]

✨ Key Insight:
[One memorable takeaway]
```

### Code Pointer (if applicable)

```
📖 Code Reference
──────────────────────

Primary: [file_path] ([N] lines)

Focus sections:
  Lines X-Y: [section name]
    Look for: [key patterns]
    Why: [reason for focus]

Specific lines to examine:
  • Line X: [description]
  • Line Y: [description]
```

### Documentation Resources

```
📚 Resources
──────────────────────

Official docs:
  • [Topic Documentation] - [URL]
  • [Related Guide] - [URL]

Project-specific:
  • [README] - Setup info
  • [CONTRIBUTING] - Patterns used
```

---

## Interactive Q&A

```
🤔 Questions?
─────────────────────

Before practice, any questions?

Commands:
  • "explain more" - Detailed explanation
  • "explain [concept]" - Focus on specific part
  • "example" - Working code example
  • "show docs" - Documentation resources
  • "walk through code" - Line-by-line walkthrough
  • "confused about [X]" - Clarify specific part
  • "ready" - Proceed to confidence check
  • "skip teaching" - Go directly to quiz
```

---

## Confidence Check

```
⏸️ Confidence Check
─────────────────────

How confident are you (1-5)?

  1 = 🟤 "Seen it but don't get it"
  2 = 🟠 "Understand basics, details fuzzy"
  3 = 🟡 "Get it, tricky questions might fail"
  4 = 🟢 "Understand well, could explain"
  5 = 🔵 "Could teach this to someone"

⚠️ Rating 4+ but failing = "illusion of competence"
```

---

## Verification/Quiz Types

### Concept Quiz

```
📚 Concept Quiz - [Topic]
─────────────────────────────

Q1: [Question text]
  A) [Option A]
  B) [Option B]
  C) [Option C]
  D) [Option D]

💡 Hint available after 2 attempts
```

### Code Reading

```
📖 Code Reading - [File]
─────────────────────────────

Open [file_path] and answer:

Q: [Question about code]

💡 Try without hints first!
```

### Coding Task

```
💻 Coding Challenge
─────────────────────────────

Build/modify [description]

Requirements:
  1. [Requirement 1]
  2. [Requirement 2]

Expected output: [description]
```

### Teach-Back

```
🎯 Teach-Back Challenge
─────────────────────────────

Explain [topic] in your own words:

Cover:
  • [Point 1]
  • [Point 2]
  • [Point 3]
  • [Point 4]

[Your explanation...]

💡 Teaching reveals gaps in understanding
```

---

## Evaluation

| Outcome | Action |
|---------|--------|
| Correct | Mark passed, update mastery, celebrate |
| Partially correct | Explain gaps, offer retry |
| Wrong | Mark struggle, provide explanation |
| Self-reported struggle | Mark struggle, return to teaching |

**Desirable difficulty messaging:**

On wrong answer:
```
❌ Not quite, but the struggle builds stronger memory.
This is "desirable difficulty" - embrace it.
Let me explain properly...
```

On correct after struggle:
```
✅ Correct! That struggle makes it stick better.
```

---

## Mastery Schedule (Spaced Repetition)

```python
# Intervals: 1 → 3 → 7 → 14 → 30 → 60 → 120 days

if passed and confidence >= 3:
    strength += 0.15
    interval = next_interval(current_interval)
    next_review = today + interval

if failed:
    strength -= 0.2
    interval = 1
    next_review = today + 1
```

---

## Struggle Detection & Recovery

### Detection

| Method | Trigger | Action |
|--------|---------|--------|
| Self-report | "struggling", "hard", "confused" | +1 struggle count |
| Quiz failure | Wrong answer | +1 struggle count |
| Low confidence fail | Rating 4+ but failed | +1 struggle, warn |

### Thresholds

| Count | Priority | Action |
|-------|----------|--------|
| 1 | Low | Review next session |
| 2 | Medium | Recovery teaching |
| 3+ | High | Block new tasks until passed |

### Recovery Teaching

```
❌ Recovery: [Topic] (struggled [N] times)
───────────────────────────────────

Different approach:

📚 Simplified: [Simple explanation]
📖 Example: [Concrete example]
🎯 Mini teach-back: [Just one concept]

We'll go slower. What's most confusing?
```

---

## Interleaving

Mix topics per session: 60% current, 25% review, 10% random, 5% struggling

Never 2+ consecutive same sub-topic.

---

## Commands Reference

### Learning Commands

| Command | Action |
|---------|--------|
| `explain more` | Full detailed lecture |
| `explain [concept]` | Focus on specific part |
| `example` | Working code example |
| `show docs` | Documentation list |
| `walk through code` | Line-by-line walkthrough |
| `ready` | Proceed to quiz |
| `skip teaching` | Direct to quiz |
| `hint` | Request hint (counts attempt) |

### Progress Commands

| Command | Action |
|---------|--------|
| `progress` / `stats` | Full progress report |
| `mastery` | Spaced repetition schedule |
| `schedule` | Upcoming reviews |
| `struggling` | Struggling topics |
| `reset` | Clear progress (confirmation) |

### Explain Mode Commands

| Command | Action |
|---------|--------|
| `explain [module]` | Analyze module |
| `understand [path]` | Understand component |
| `refresh` | Re-analyze cached module |
| `detailed` | Deep dive from overview |
| `walkthrough [file]` | Full file walkthrough |

---

## Achievement System

| Achievement | Condition |
|-------------|-----------|
| First Step | Complete first task |
| Week Streak | 7 consecutive days |
| Retrieval Master | 10 retrieval practices |
| Honest Learner | Rate 2 when could fake 4 |
| Struggle Embraced | Pass after 3 struggles |
| Teacher | 5 teach-backs |
| Spaced Pro | Reach 30-day interval |

---

## Session End Summary

```
📊 Session Complete!
──────────────────────────────
Duration: [X] min
Tasks: [N]

📚 Topics worked:
  • [Task] - [Status]

🔄 Reviews scheduled:
  • [Task] → Review in [N] days

🎯 Next session:
  • Start with [recommendation]

💤 Sleep consolidates learning.
Return tomorrow for spaced repetition!

🔥 Streak: [N] days
```

---

## File Structure

```
.agents/skills/adaptive-learning-coach/
├── SKILL.md                      # This file
├── scripts/
│   ├── schema.py                 # SQLite schema
│   ├── progress_manager.py       # DB operations
│   ├── plan_generator.py         # Dynamic plan generation
│   └── explain_analyzer.py       # Module analysis
├── templates/
│   └── plan_template.json        # Semi-structure template
└── storage/                      # Auto-created
    ├── learning.db               # SQLite database
    ├── progress_export.json      # Git-friendly export
    └── cache/
        └── module_analysis.json  # Explain mode cache
```

---

## Error Handling

| Missing File | Action |
|--------------|--------|
| Database | Create with schema |
| Template | Use default |
| Plan | Generate dynamically |
| Module cache | Analyze fresh |

---

## Database Schema Summary

| Table | Purpose |
|-------|---------|
| repos | Track learning repos/projects |
| learning_plans | Store generated/imported plans |
| topics | Individual learning tasks |
| mastery | Spaced repetition schedule |
| struggles | Struggle tracking |
| sessions | Learning session history |
| quiz_history | Quiz attempts |
| confidence_ratings | Metacognitive monitoring |
| module_cache | Explain mode analysis cache |

---

## Quick Reference

**Start learning:** "give me a task", "what should I learn next", "start learning"

**Explain code:** "explain [module]", "how does [X] work", "understand [path]"

**Check progress:** "progress", "stats", "mastery", "struggling"

**During learning:** "explain more", "example", "ready", "hint"
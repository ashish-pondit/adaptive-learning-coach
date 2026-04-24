# Adaptive Learning Coach Skill

An AI-powered adaptive learning skill for structured learning through comprehensive learning plans, using evidence-based meta-learning techniques with a **teaching-first approach**.

## Features

### Meta-Learning Techniques
- 🧠 **Retrieval Practice** - Test before review (for spaced repetition reviews)
- 🔄 **Spaced Repetition** - Growing intervals: 1→3→7→14→30→60→120 days
- 🎲 **Interleaving** - Mix topics: 60% current, 25% review, 10% random, 5% elaboration
- 🔗 **Elaboration** - Connect to existing knowledge (Django/React comparisons)
- ⏸️ **Metacognitive Monitoring** - Confidence ratings, illusion-of-competence detection
- ❌ **Desirable Difficulty** - Embrace struggle as learning signal
- 🎯 **Teach-Back** - Explain in own words to reveal gaps
- 💤 **Sleep Consolidation** - Session timing, streak tracking

### Teaching-First Approach
- For NEW tasks: Teaching phase → Interactive Q&A → Confidence → Quiz
- For REVIEW tasks: Retrieval practice → Confidence → Quiz  
- For STRUGGLING tasks: Recovery teaching → Q&A → Confidence → Quiz

### Teaching Components
- 📚 Concept Summary
- 🔗 Django/React Comparisons
- 📖 Code File Pointers
- 📚 Documentation References
- 💡 Mini-Lectures (complex topics)

## Installation

Copy the skill to your `.agents/skills/` directory:

```bash
mkdir -p .agents/skills/adaptive-learning-coach
cp -r adaptive-learning-coach-skill/* .agents/skills/adaptive-learning-coach/
```

## Usage

Activate by saying:
- "give me a task"
- "what should I learn next"
- "teach me about [topic]"
- "start learning"
- "show my progress"

## Commands

### Teaching Commands
| Command | Action |
|---------|--------|
| `explain more` | Full mini-lecture |
| `explain [concept]` | Deep dive on specific concept |
| `example` | Working code example |
| `compare [django-thing]` | Django vs .NET comparison |
| `show docs` | Documentation resources |
| `ready` | Proceed to quiz |

### Progress Commands
| Command | Action |
|---------|--------|
| `progress` | Show progress report |
| `mastery` | Spaced repetition schedule |
| `struggling` | Mark as struggling |

## File Structure

```
adaptive-learning-coach/
├── SKILL.md              # Main skill instructions
├── README.md             # This file
├── references/
│   └── quiz_bank.md      # Teaching notes + quizzes
├── scripts/
│   └── progress_manager.py  # Progress utilities
└── evals/
    └── evals.json        # Test cases
```

## Progress Tracking

Progress is stored in `docs/LEARNING_PROGRESS.json`:

```json
{
  "completedTasks": ["1.1", "2.4"],
  "taughtTasks": ["1.1", "2.4", "3.1"],
  "strugglingTasks": { "2.4": { "count": 2 } },
  "masterySchedule": {
    "1.1": { "strength": 0.7, "interval": 7, "nextReview": "2026-04-30" }
  }
}
```

## License

MIT

## Author

Created for learning IAM Backend (.NET) and Frontend (React/Next.js) from a Django background.
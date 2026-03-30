# PawPal+ (Module 2 Project)

**🐾 PawPal+** is a smart pet care management app built with Python and Streamlit. It helps a busy pet owner stay on top of daily routines by scheduling tasks, detecting conflicts, and automatically carrying forward recurring activities.

---

## Features

### Owner & Pet Management
- Register an owner with a name and a daily time budget (in minutes)
- Add multiple pets per owner (dog, cat, bird, etc.)
- Tasks are scoped to individual pets but scheduled across all of them together

### Priority-First Scheduling
- Tasks are ranked **high → medium → low** and fitted greedily into the owner's available time
- Higher-priority tasks (medication, feeding) always claim a slot before lower-priority ones
- Tasks that don't fit are tracked as "skipped" with an explanation

### Chronological Sorting
- It reorders any task list by start time using numeric comparison insertion order never affects the output
- The final generated schedule is always displayed in time order

### Conflict Detection
- It checks every pair of tasks for overlapping windows.
- It returns plain warning strings, no crashes, just actionable messages shown directly in the UI

### Recurring Task Auto-Scheduling
- Marking a *daily* task complete automatically creates the next occurrence for **tomorrow**
- Marking a *weekly* task complete creates the next occurrence **7 days from today**
- *Once* tasks are marked done with no follow-up

### Skipped Task Reporting
- The *Schedule* object tracks both planned tasks and tasks that didn't fit the time budget
- The UI surfaces skipped tasks as individual warnings so owners know exactly what was dropped and why

---

## System Design

The app is built on six classes:

| Class | Role |
|---|---|
| `Task` | A single care activity with time, duration, priority, frequency, and completion state |
| `Pet` | Groups a pet's details with its task list; handles task completion and recurrence |
| `Owner` | Holds the time budget and a list of pets; aggregates tasks across all pets |
| `Schedule` | The output of the scheduler — planned tasks + skipped tasks |
| `Scheduler` | All algorithmic logic: sorting, filtering, conflict detection, plan generation |
| `PawPalApp` | CLI entry point for running a demo without the Streamlit UI |

See `uml_final.png` for the full class diagram.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python pawpal_system.py
```

---

## Testing PawPal+

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

13 tests across five categories:

| Category | Tests | What's verified |
|---|---|---|
| **Task completion** | 2 | mark_complete() flips status; adding a task increases pet count |
| **Sorting** | 2 | Out-of-order tasks return chronologically; same-hour minute edge case |
| **Recurrence** | 3 | Daily → +1 day; weekly → +7 days; once → no follow-up |
| **Conflict detection** | 3 | Exact same time flagged; overlapping windows flagged; back-to-back correctly not flagged |
| **Edge cases** | 3 | Empty pet; owner with no pets; all tasks exceed budget → all skipped |

### Confidence level

★★★★☆ (4 / 5)

Core scheduling logic is fully covered and all 13 tests pass. The remaining star reflects untested areas: Streamlit UI wiring, the expand_recurring helper, and multi-day recurring chains.

---

## Smarter Scheduling

Beyond basic task tracking, PawPal+ includes several algorithmic features:

- **Priority-first scheduling** >
tasks are sorted high → medium → low, then fitted into the owner's available time budget
- **Chronological sorting** >
sort_by_time() orders any task list by scheduled_time using numeric minute comparison
- **Conflict detection** >
conflict_warnings() scans for overlapping time windows and returns plain warning strings
- **Recurring task auto-scheduling** >
Pet.complete_task() marks a task done and creates the next occurrence anchored to today
- **Skipped task reporting** >
Schedule tracks tasks that didn't fit the time budget and lists them separately

---

## Demo

<a href="/pawpal_screenshot.jpg/" target="_blank"><img src='/pawpal_screenshot.jpg' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

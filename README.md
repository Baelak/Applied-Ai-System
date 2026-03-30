# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

Beyond basic task tracking, PawPal+ includes several algorithmic features:

- **Priority-first scheduling** > tasks are sorted high → medium → low, then fitted into the owner's available time budget. Higher-priority tasks (medication, feeding) always claim slots before lower-priority ones.
- **Chronological sorting** > 
sort_by_time() orders any task list by scheduled_time using numeric minute comparison, so 07:00 always sorts before 10:00 regardless of insertion order.
- **Conflict detection** >
 conflict_warnings() scans for overlapping time windows across all pets and returns plain warning strings (no crashes). Two tasks conflict when one starts before the other ends.
- **Recurring task auto-scheduling** >
 calling Pet.complete_task() marks a task done and automatically creates the next occurrence: +1 day for daily tasks, +7 days for weekly tasks, always anchored to today so it never schedules into the past.
- **Skipped task reporting** >
 the generated Schedule tracks tasks that didn't fit the time budget and lists them separately, so owners know what was left out and why.

## Testing PawPal+

### Run the tests

- python -m pytest tests/test_pawpal.py -v


### What the tests cover

13 tests across four categories:

| Category | Tests | What's verified |
|---|---|---|
| **Task completion** | 2 | mark_complete() flips status; adding a task increases pet count |
| **Sorting** | 2 | Out-of-order tasks return in chronological order; same-hour edge case handled correctly |
| **Recurrence** | 3 | Daily tasks create a +1 day follow-up; weekly creates +7 days; once tasks create nothing |
| **Conflict detection** | 3 | Exact same start time flagged; overlapping windows flagged; back-to-back tasks correctly not flagged |
| **Edge cases** | 3 | Empty pet returns no tasks; owner with no pets produces empty schedule; tasks over budget all go to skipped |

### Confidence level

★★★★☆ (4 out of 5 stars)

The core scheduling logic, priority sorting, time-budget fitting, recurring task creation, and conflict detection is fully tested and all 13 tests pass. The one star held back reflects untested areas such as the Streamlit UI wiring, the expand_recurring method, and multi-day scenarios where a recurring task's follow-up itself becomes due.

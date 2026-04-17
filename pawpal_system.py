from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta


# Priority order used for sorting (lower number = higher priority)
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


# ---------------------------------------------------------------------------
# Task  — a single care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    duration: int               # minutes
    priority: str               # "high" | "medium" | "low"
    scheduled_time: str = "08:00"       # "HH:MM" — when the task should start
    frequency: str = "once"             # "once" | "daily" | "weekly"
    scheduled_date: date = field(default_factory=date.today)
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate priority on creation."""
        if self.priority not in PRIORITY_ORDER:
            raise ValueError(f"priority must be 'high', 'medium', or 'low' — got '{self.priority}'")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a pending copy of this task due tomorrow (daily) or in 7 days (weekly).

        Always calculates from date.today() so the result is never in the past,
        even if the original scheduled_date is stale. Returns None for 'once' tasks.
        """
        today = date.today()
        if self.frequency == "daily":
            next_date = today + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = today + timedelta(weeks=1)
        else:
            return None
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            scheduled_date=next_date,
        )

    def end_time(self) -> str:
        """Return the calculated end time as 'HH:MM' based on start time + duration."""
        h, m = map(int, self.scheduled_time.split(":"))
        total = h * 60 + m + self.duration
        return f"{total // 60:02d}:{total % 60:02d}"

    def __str__(self) -> str:
        status = "done" if self.completed else "pending"
        return (
            f"[{self.priority.upper()}] {self.scheduled_time}–{self.end_time()} "
            f"{self.name} ({self.duration} min, {self.frequency}) — {status}"
        )


# ---------------------------------------------------------------------------
# Pet  — stores pet details and its task list
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    type: str               # "dog" | "cat" | "bird" | etc.
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's list."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's list."""
        self.tasks = [t for t in self.tasks if t is not task]

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and auto-schedule the next occurrence for recurring tasks."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            self.tasks.append(next_task)


# ---------------------------------------------------------------------------
# Owner  — manages multiple pets and time budget
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_time: int = 0             # total minutes available per day
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect every pending task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_pending_tasks())
        return all_tasks


# ---------------------------------------------------------------------------
# Schedule  — the final ordered plan
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(self, tasks: list[Task], skipped: list[Task] | None = None) -> None:
        self.tasks = tasks
        self.skipped = skipped or []

    def get_plan(self) -> str:
        """Return a human-readable summary of the scheduled tasks."""
        if not self.tasks:
            return "No tasks scheduled."
        lines = ["--- Daily Plan ---"]
        total = 0
        for i, task in enumerate(self.tasks, start=1):
            lines.append(f"{i}. {task}")
            total += task.duration
        lines.append(f"Total time: {total} min")
        if self.skipped:
            lines.append("\nSkipped (not enough time):")
            for task in self.skipped:
                lines.append(f"  - {task.name} ({task.duration} min)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler  — retrieves, filters, and organizes tasks across pets
# ---------------------------------------------------------------------------

class Scheduler:

    # --- 1. Sort by scheduled time ---

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically using their 'HH:MM' scheduled_time string.

        The lambda converts 'HH:MM' → total minutes since midnight so that
        string comparison ('09:00' < '10:00') is replaced with numeric ordering,
        which handles edge cases like '09:00' vs '10:00' correctly.
        """
        return sorted(tasks, key=lambda t: int(t.scheduled_time.replace(":", "")))

    # --- 2. Filter by pet or completion status ---

    def filter_by_pet(self, tasks: list[Task], pet: Pet) -> list[Task]:
        """Return only the tasks from the list that belong to the given pet."""
        return [t for t in tasks if t in pet.tasks]

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in tasks if t.completed == completed]

    # --- 3. Expand recurring tasks into a day's occurrences ---

    def expand_recurring(self, tasks: list[Task]) -> list[Task]:
        """Return the task list with an extra copy of each daily task shifted 12 hours later."""
        expanded = []
        for task in tasks:
            expanded.append(task)
            if task.frequency == "daily":
                h, m = map(int, task.scheduled_time.split(":"))
                new_h = (h + 12) % 24
                second = Task(
                    name=task.name,
                    duration=task.duration,
                    priority=task.priority,
                    scheduled_time=f"{new_h:02d}:{m:02d}",
                    frequency=task.frequency,
                )
                expanded.append(second)
        return expanded

    # --- 4. Conflict detection ---

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap.

        Two tasks conflict when one starts before the other ends:
            task_a.start < task_b.end  AND  task_b.start < task_a.end
        """
        def to_minutes(t: str) -> int:
            h, m = map(int, t.split(":"))
            return h * 60 + m

        conflicts = []
        sorted_tasks = self.sort_by_time(tasks)
        for i, a in enumerate(sorted_tasks):
            for b in sorted_tasks[i + 1:]:
                a_start = to_minutes(a.scheduled_time)
                a_end   = a_start + a.duration
                b_start = to_minutes(b.scheduled_time)
                b_end   = b_start + b.duration
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def conflict_warnings(self, tasks: list[Task]) -> list[str]:
        """Return human-readable warning strings for every overlapping task pair.

        Returns an empty list when there are no conflicts, so callers can check
        with a simple `if warnings:` without any risk of crashing.
        """
        warnings = []
        for a, b in self.detect_conflicts(tasks):
            warnings.append(
                f"WARNING: '{a.name}' ({a.scheduled_time}–{a.end_time()}) "
                f"overlaps with '{b.name}' ({b.scheduled_time}–{b.end_time()})"
            )
        return warnings

    # --- Main plan generator ---

    def generate_plan(self, owner: Owner) -> Schedule:
        """Sort the owner's pending tasks by priority and fit them into the available time budget."""
        tasks = owner.get_all_tasks()

        # Sort by priority rank, then by scheduled time as tiebreaker
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.scheduled_time)
        )

        # Greedy fit: keep scanning even after a task doesn't fit
        plan: list[Task] = []
        skipped: list[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration <= owner.available_time:
                plan.append(task)
                time_used += task.duration
            else:
                skipped.append(task)

        # Final output ordered by start time
        return Schedule(self.sort_by_time(plan), skipped)


# ---------------------------------------------------------------------------
# PawPalApp  (entry point)
# ---------------------------------------------------------------------------

class PawPalApp:
    def __init__(self) -> None:
        self.scheduler = Scheduler()

    def run(self) -> None:
        """Quick CLI demo that builds a sample owner/pet/task setup and prints a plan."""
        owner = Owner(name="Alex", available_time=60)

        dog = Pet(name="Biscuit", type="dog")
        dog.add_task(Task(name="Morning walk",     duration=20, priority="high",   scheduled_time="07:00", frequency="daily"))
        dog.add_task(Task(name="Feeding",          duration=10, priority="high",   scheduled_time="08:00", frequency="daily"))
        dog.add_task(Task(name="Grooming",         duration=30, priority="medium", scheduled_time="10:00", frequency="weekly"))
        dog.add_task(Task(name="Enrichment puzzle",duration=15, priority="low",    scheduled_time="17:00", frequency="daily"))

        owner.add_pet(dog)

        schedule = self.scheduler.generate_plan(owner)
        print(schedule.get_plan())

        conflicts = self.scheduler.detect_conflicts(dog.tasks)
        if conflicts:
            print("\nConflicts detected:")
            for a, b in conflicts:
                print(f"  '{a.name}' overlaps with '{b.name}'")
        else:
            print("\nNo conflicts detected.")


if __name__ == "__main__":
    PawPalApp().run()

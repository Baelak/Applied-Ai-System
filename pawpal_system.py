from __future__ import annotations
from dataclasses import dataclass, field


# Priority order used for sorting (lower number = higher priority)
PRIORITY_ORDER = {"high": 1, "medium": 2, "low": 3}


# ---------------------------------------------------------------------------
# Task  — a single care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    duration: int           # minutes
    priority: str           # "high" | "medium" | "low"
    frequency: str = "once" # "once" | "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def __str__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"[{self.priority.upper()}] {self.name} ({self.duration} min, {self.frequency}) — {status}"


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
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks

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
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler  — retrieves, filters, and organizes tasks across pets
# ---------------------------------------------------------------------------

class Scheduler:
    def generate_plan(self, owner: Owner) -> Schedule:
        """Sort the owner's pending tasks by priority and fit them into the available time budget."""
        tasks = owner.get_all_tasks()

        # Sort by priority rank, then alphabetically as a tiebreaker
        sorted_tasks = sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.name))

        # Fit as many tasks as possible within the available time
        plan: list[Task] = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration <= owner.available_time:
                plan.append(task)
                time_used += task.duration

        return Schedule(plan)


# ---------------------------------------------------------------------------
# PawPalApp  (entry point)
# ---------------------------------------------------------------------------

class PawPalApp:
    def __init__(self) -> None:
        self.scheduler = Scheduler()

    def run(self) -> None:
        """Quick CLI demo that builds a sample owner/pet/task setup and prints a plan."""
        # Sample data
        owner = Owner(name="Alex", available_time=60)

        dog = Pet(name="Biscuit", type="dog")
        dog.add_task(Task(name="Morning walk", duration=20, priority="high", frequency="daily"))
        dog.add_task(Task(name="Feeding", duration=10, priority="high", frequency="daily"))
        dog.add_task(Task(name="Grooming", duration=30, priority="medium", frequency="weekly"))
        dog.add_task(Task(name="Enrichment puzzle", duration=15, priority="low", frequency="daily"))

        owner.add_pet(dog)

        schedule = self.scheduler.generate_plan(owner)
        print(schedule.get_plan())


if __name__ == "__main__":
    PawPalApp().run()

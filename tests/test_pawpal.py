from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", type="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", duration=10, priority="high"))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    # Tasks added out of order on purpose
    scheduler = Scheduler()
    tasks = [
        Task(name="Evening walk",  duration=20, priority="low",  scheduled_time="17:00"),
        Task(name="Morning walk",  duration=20, priority="high", scheduled_time="07:00"),
        Task(name="Lunch feeding", duration=10, priority="high", scheduled_time="12:00"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.scheduled_time for t in sorted_tasks]
    assert times == ["07:00", "12:00", "17:00"]


def test_sort_by_time_handles_same_hour_different_minutes():
    scheduler = Scheduler()
    tasks = [
        Task(name="B", duration=5, priority="low",  scheduled_time="08:45"),
        Task(name="A", duration=5, priority="high", scheduled_time="08:05"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    assert sorted_tasks[0].scheduled_time == "08:05"
    assert sorted_tasks[1].scheduled_time == "08:45"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence_tomorrow():
    today = date.today()
    pet = Pet(name="Biscuit", type="dog")
    task = Task(name="Morning walk", duration=20, priority="high",
                frequency="daily", scheduled_date=today)
    pet.add_task(task)

    pet.complete_task(task)

    # Pet should now have 2 tasks: original (done) + new occurrence
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.completed is False
    assert next_task.scheduled_date == today + timedelta(days=1)


def test_weekly_task_creates_next_occurrence_in_seven_days():
    today = date.today()
    pet = Pet(name="Biscuit", type="dog")
    task = Task(name="Grooming", duration=30, priority="medium",
                frequency="weekly", scheduled_date=today)
    pet.add_task(task)

    pet.complete_task(task)

    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.scheduled_date == today + timedelta(weeks=1)


def test_once_task_creates_no_next_occurrence():
    pet = Pet(name="Biscuit", type="dog")
    task = Task(name="Vet visit", duration=60, priority="high", frequency="once")
    pet.add_task(task)

    pet.complete_task(task)

    # Only the original task — no follow-up
    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_detected_for_exact_same_start_time():
    scheduler = Scheduler()
    tasks = [
        Task(name="Walk",    duration=20, priority="high", scheduled_time="08:00"),
        Task(name="Feeding", duration=10, priority="high", scheduled_time="08:00"),
    ]
    warnings = scheduler.conflict_warnings(tasks)
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_conflict_detected_for_overlapping_windows():
    scheduler = Scheduler()
    # Walk: 07:00–07:20, Vet call: 07:10–07:25 — overlap of 10 min
    tasks = [
        Task(name="Morning walk", duration=20, priority="high", scheduled_time="07:00"),
        Task(name="Vet call",     duration=15, priority="high", scheduled_time="07:10"),
    ]
    warnings = scheduler.conflict_warnings(tasks)
    assert len(warnings) == 1


def test_no_conflict_for_back_to_back_tasks():
    scheduler = Scheduler()
    # Walk ends at 07:20, Feeding starts at 07:20 — touching but not overlapping
    tasks = [
        Task(name="Morning walk", duration=20, priority="high", scheduled_time="07:00"),
        Task(name="Feeding",      duration=10, priority="high", scheduled_time="07:20"),
    ]
    warnings = scheduler.conflict_warnings(tasks)
    assert len(warnings) == 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_pet_returns_no_tasks():
    pet = Pet(name="Biscuit", type="dog")
    assert pet.get_pending_tasks() == []


def test_owner_with_no_pets_generates_empty_schedule():
    owner = Owner(name="Jordan", available_time=60)
    scheduler = Scheduler()
    schedule = scheduler.generate_plan(owner)
    assert schedule.tasks == []
    assert "No tasks scheduled" in schedule.get_plan()


def test_all_tasks_exceed_budget_goes_to_skipped():
    owner = Owner(name="Jordan", available_time=10)
    pet = Pet(name="Biscuit", type="dog")
    pet.add_task(Task(name="Long walk", duration=30, priority="high", scheduled_time="07:00"))
    pet.add_task(Task(name="Grooming",  duration=60, priority="high", scheduled_time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler()
    schedule = scheduler.generate_plan(owner)

    assert schedule.tasks == []
    assert len(schedule.skipped) == 2

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Haile", available_time=90)
scheduler = Scheduler()

# --- Pet 1: dog (tasks added OUT OF ORDER intentionally) ---
dog = Pet(name="Jegol", type="dog")
dog.add_task(Task(name="Evening walk",      duration=20, priority="medium", scheduled_time="17:30", frequency="daily"))
dog.add_task(Task(name="Morning walk",      duration=20, priority="high",   scheduled_time="07:00", frequency="daily"))
dog.add_task(Task(name="Flea medication",   duration=5,  priority="high",   scheduled_time="09:00", frequency="weekly"))
dog.add_task(Task(name="Fetch in the yard", duration=15, priority="low",    scheduled_time="15:00", frequency="daily"))
dog.add_task(Task(name="Feeding",           duration=10, priority="high",   scheduled_time="08:00", frequency="daily"))

# --- Pet 2: cat (tasks also out of order) ---
cat = Pet(name="Luna", type="cat")
cat.add_task(Task(name="Laser pointer play", duration=10, priority="low",    scheduled_time="19:00", frequency="daily"))
cat.add_task(Task(name="Litter box clean",   duration=10, priority="high",   scheduled_time="07:30", frequency="daily"))
cat.add_task(Task(name="Brushing",           duration=10, priority="medium", scheduled_time="11:00", frequency="weekly"))
cat.add_task(Task(name="Feeding",            duration=5,  priority="high",   scheduled_time="08:30", frequency="daily"))

# --- Deliberate conflicts ---
# Conflict 1 (same pet): "Vet call" starts at 07:10, overlaps Morning walk (07:00–07:20)
dog.add_task(Task(name="Vet call",           duration=15, priority="high",   scheduled_time="07:10", frequency="once"))
# Conflict 2 (different pets): Luna's "Medication" starts at 07:25, overlaps Litter box clean (07:30–07:40)
cat.add_task(Task(name="Medication",         duration=20, priority="high",   scheduled_time="07:25", frequency="daily"))

owner.add_pet(dog)
owner.add_pet(cat)

all_tasks = owner.get_all_tasks()

# --- 1. Unsorted (raw insertion order) ---
print("=" * 55)
print("RAW ORDER (as added):")
print("=" * 55)
for t in all_tasks:
    print(f"  {t}")

# --- 2. Sorted by time ---
print("\n" + "=" * 55)
print("SORTED BY TIME:")
print("=" * 55)
for t in scheduler.sort_by_time(all_tasks):
    print(f"  {t}")

# --- 3. Filtered: Biscuit's tasks only ---
print("\n" + "=" * 55)
print("BISCUIT'S TASKS ONLY (filter_by_pet):")
print("=" * 55)
for t in scheduler.filter_by_pet(all_tasks, dog):
    print(f"  {t}")

# --- 4. Mark one task complete and filter by status ---
dog.tasks[0].mark_complete()   # Evening walk → done
print("\n" + "=" * 55)
print("PENDING TASKS ONLY (filter_by_status):")
print("=" * 55)
for t in scheduler.filter_by_status(all_tasks, completed=False):
    print(f"  {t}")

print("\n" + "=" * 55)
print("COMPLETED TASKS (filter_by_status):")
print("=" * 55)
for t in scheduler.filter_by_status(all_tasks, completed=True):
    print(f"  {t}")

# --- 5. Conflict detection ---
print("\n" + "=" * 55)
print("CONFLICT DETECTION (all tasks):")
print("=" * 55)
warnings = scheduler.conflict_warnings(all_tasks)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# --- 6. Full generated schedule ---
print("\n" + "=" * 55)
print(f"TODAY'S SCHEDULE for {owner.name} ({owner.available_time} min available):")
print("=" * 55)
schedule = scheduler.generate_plan(owner)
print(schedule.get_plan())

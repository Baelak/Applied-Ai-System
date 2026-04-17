import streamlit as st
import google.generativeai as genai
from pawpal_system import Owner, Pet, Task, Scheduler

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Initialize session state once ---
if "owner" not in st.session_state:
    st.session_state["owner"] = None

if "scheduler" not in st.session_state:
    st.session_state["scheduler"] = Scheduler()

scheduler: Scheduler = st.session_state["scheduler"]

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.subheader("Owner Setup")

owner_name = st.text_input("Owner name", value="Haile")
available_time = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)

if st.button("Save Owner"):
    st.session_state["owner"] = Owner(name=owner_name, available_time=int(available_time))
    st.success(f"Owner '{owner_name}' saved with {available_time} minutes available.")

owner: Owner | None = st.session_state["owner"]

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add a Pet
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

if owner is None:
    st.info("Save an owner above before adding pets.")
else:
    pet_type = st.selectbox("Species", ["dog", "cat", "bird", "other"])

    name_theme = st.text_input("Name theme (optional)", placeholder="e.g. royal, funny, Ethiopian", key="name_theme")
    if st.button("🤖 AI Pet Names"):
        with st.spinner("Asking Gemini for name ideas..."):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                theme_hint = f" The names should have a '{name_theme}' theme." if name_theme.strip() else ""
                prompt = (
                    f"Suggest pet names for a {pet_type}.{theme_hint} "
                    f"Give exactly 3 male names and 3 female names. "
                    f"Format your response as:\n"
                    f"Male: Name1, Name2, Name3\n"
                    f"Female: Name1, Name2, Name3\n"
                    f"Then add one short sentence explaining the theme or inspiration."
                )
                response = model.generate_content(prompt)
                text = response.text.strip()
                st.markdown("**Suggested names:**")
                for line in text.splitlines():
                    if line.startswith("Male:"):
                        st.markdown(f"**Male** — {line[5:].strip()}")
                    elif line.startswith("Female:"):
                        st.markdown(f"**Female** — {line[7:].strip()}")
                    elif line.strip():
                        st.caption(line.strip())
            except Exception as e:
                st.error(f"Gemini error: {e}")

    pet_name = st.text_input("Pet name", value="Jegol")

    if st.button("Add Pet"):
        owner.add_pet(Pet(name=pet_name, type=pet_type))
        st.success(f"Added {pet_type} '{pet_name}' to {owner.name}'s pets.")

    if owner.pets:
        st.caption(f"{owner.name}'s pets: " + ", ".join(f"{p.name} ({p.type})" for p in owner.pets))

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add a Task to a Pet
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if owner is None or not owner.pets:
    st.info("Add at least one pet before scheduling tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign task to", pet_names)

    PRESET_TASKS = [
        "Morning walk", "Evening walk", "Feeding", "Fetch in the yard",
        "Flea medication", "Vet call", "Litter box clean", "Brushing",
        "Laser pointer play", "Medication", "Custom...",
    ]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_choice = st.selectbox("Task name", PRESET_TASKS)
        task_name = st.text_input("Custom task name") if task_choice == "Custom..." else task_choice
    with col2:
        task_time = st.text_input("Start time (HH:MM)", value="08:00")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add Task"):
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            name=task_name,
            duration=int(duration),
            priority=priority,
            scheduled_time=task_time,
            frequency=frequency,
        ))
        st.success(f"Added '{task_name}' to {selected_pet_name}.")

    # --- All pending tasks, sorted chronologically via Scheduler.sort_by_time() ---
    all_tasks = owner.get_all_tasks()
    if "editing_task_id" not in st.session_state:
        st.session_state["editing_task_id"] = None

    if all_tasks:
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        task_to_pet = {id(t): p.name for p in owner.pets for t in p.tasks}

        st.markdown("**Current tasks** (sorted by start time)")
        header = st.columns([1, 1, 2, 1, 1, 1, 0.5, 0.5])
        for col, label in zip(header, ["Pet", "Start", "Task", "Duration", "Priority", "Frequency", "", ""]):
            col.markdown(f"**{label}**")

        for i, t in enumerate(sorted_tasks):
            c = st.columns([1, 1, 2, 1, 1, 1, 0.5, 0.5])
            c[0].write(task_to_pet.get(id(t), "—"))
            c[1].write(t.scheduled_time)
            c[2].write(t.name)
            c[3].write(f"{t.duration} min")
            c[4].write(t.priority.capitalize())
            c[5].write(t.frequency)
            if c[6].button("✏️", key=f"edit_{i}"):
                st.session_state["editing_task_id"] = id(t)
            if c[7].button("🗑️", key=f"remove_{i}"):
                for pet in owner.pets:
                    pet.remove_task(t)
                st.rerun()

        # --- Inline edit form ---
        if st.session_state["editing_task_id"] is not None:
            editing_task = next(
                (t for p in owner.pets for t in p.tasks if id(t) == st.session_state["editing_task_id"]), None
            )
            if editing_task:
                st.markdown("**Edit task**")
                with st.form("edit_form"):
                    e1, e2, e3, e4, e5 = st.columns(5)
                    new_name = e1.text_input("Task name", value=editing_task.name)
                    new_time = e2.text_input("Start time", value=editing_task.scheduled_time)
                    new_dur  = e3.number_input("Duration (min)", value=editing_task.duration, min_value=1, max_value=240)
                    new_pri  = e4.selectbox("Priority", ["high", "medium", "low"],
                                            index=["high", "medium", "low"].index(editing_task.priority))
                    new_freq = e5.selectbox("Frequency", ["daily", "weekly", "once"],
                                            index=["daily", "weekly", "once"].index(editing_task.frequency))
                    save, cancel = st.columns(2)
                    if save.form_submit_button("Save"):
                        editing_task.name = new_name
                        editing_task.scheduled_time = new_time
                        editing_task.duration = int(new_dur)
                        editing_task.priority = new_pri
                        editing_task.frequency = new_freq
                        st.session_state["editing_task_id"] = None
                        st.rerun()
                    if cancel.form_submit_button("Cancel"):
                        st.session_state["editing_task_id"] = None
                        st.rerun()

        # --- Conflict warnings via Scheduler.conflict_warnings() ---
        warnings = scheduler.conflict_warnings(all_tasks)
        if warnings:
            st.markdown("**Schedule conflicts**")
            for w in warnings:
                st.warning(w.replace("WARNING: ", ""))
        else:
            st.success("No scheduling conflicts detected.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("Today's Schedule")

if owner is None or not owner.pets or not owner.get_all_tasks():
    st.info("Add an owner, pets, and tasks before generating a schedule.")
else:
    if st.button("Generate Schedule"):
        schedule = scheduler.generate_plan(owner)

        if not schedule.tasks:
            st.error("No tasks could fit within the available time budget.")
        else:
            st.success(f"Scheduled {len(schedule.tasks)} task(s) — "
                       f"{sum(t.duration for t in schedule.tasks)} of "
                       f"{owner.available_time} minutes used.")

            # Scheduled tasks table
            st.markdown("**Planned tasks** (priority order, then by time)")
            st.table([
                {
                    "Start":     t.scheduled_time,
                    "End":       t.end_time(),
                    "Task":      t.name,
                    "Duration":  f"{t.duration} min",
                    "Priority":  t.priority.capitalize(),
                    "Frequency": t.frequency,
                }
                for t in schedule.tasks
            ])

        # Skipped tasks
        if schedule.skipped:
            st.markdown("**Skipped** (not enough time remaining)")
            for t in schedule.skipped:
                st.warning(f"{t.name} ({t.duration} min, {t.priority} priority) could not be scheduled today.")


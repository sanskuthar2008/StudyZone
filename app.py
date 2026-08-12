import streamlit as st
from datetime import datetime, date, time, timedelta
from collections import defaultdict
import json
import os
import uuid


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StudyZone",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FILE LOCATIONS
# ============================================================

DATA_FILE = "student_planner_data.json"
PHOTO_FOLDER = "study_note_photos"

if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)


# ============================================================
# DEFAULT DATA
# ============================================================

def default_data():
    return {
        "student_name": "",
        "tasks": [],
        "study_plans": [],
        "study_sessions": [],
        "notes": []
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        base = default_data()

        for key in base:
            if key not in saved:
                saved[key] = base[key]

        return saved

    except Exception:
        return default_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.data,
            file,
            indent=4,
            ensure_ascii=False
        )


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

if "edit_note_id" not in st.session_state:
    st.session_state.edit_note_id = None


data = st.session_state.data


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E6EAF0;
    }

    .main-header {
        font-size: 38px;
        font-weight: 800;
        color: #20345F;
        margin-bottom: 4px;
    }

    .sub-header {
        color: #697386;
        font-size: 16px;
        margin-bottom: 28px;
    }

    .section-header {
        color: #20345F;
        font-size: 27px;
        font-weight: 750;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #E5E9F0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 14px rgba(32, 52, 95, 0.05);
    }

    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E5E9F0;
        border-radius: 16px;
        padding: 20px;
        min-height: 120px;
        box-shadow: 0 4px 14px rgba(32, 52, 95, 0.05);
    }

    .stat-number {
        font-size: 30px;
        font-weight: 800;
        color: #20345F;
    }

    .stat-label {
        color: #697386;
        font-size: 14px;
        margin-top: 5px;
    }

    .study-bar {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px 22px;
        margin: 10px 0;
        border-left: 7px solid #5878D9;
        box-shadow: 0 4px 14px rgba(32, 52, 95, 0.05);
    }

    .lecture-bar {
        border-left-color: #5878D9;
    }

    .chapter-bar {
        border-left-color: #49A078;
    }

    .bar-title {
        color: #20345F;
        font-size: 19px;
        font-weight: 750;
    }

    .bar-time {
        color: #20345F;
        font-size: 17px;
        font-weight: 700;
        margin-top: 8px;
    }

    .bar-info {
        color: #697386;
        font-size: 14px;
        margin-top: 5px;
    }

    .break-bar {
        background: #FFF9E8;
        border: 1px solid #F0DE9B;
        border-radius: 14px;
        padding: 12px 18px;
        margin: 8px 0;
        color: #7A6218;
    }

    .note-card {
        background: #FFFFFF;
        border: 1px solid #E5E9F0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 14px rgba(32, 52, 95, 0.05);
    }

    .note-title {
        font-size: 20px;
        font-weight: 750;
        color: #20345F;
    }

    .small-text {
        color: #697386;
        font-size: 14px;
    }

    .progress-title {
        color: #20345F;
        font-size: 18px;
        font-weight: 700;
    }

    .type-option {
        background: #FFFFFF;
        border: 1px solid #E5E9F0;
        border-radius: 14px;
        padding: 15px;
        text-align: center;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def task_deadline(task):
    return datetime.strptime(
        task["deadline"],
        "%Y-%m-%d %H:%M"
    )


def deadline_status(task):
    if task.get("completed", False):
        return "COMPLETED"

    deadline = task_deadline(task)
    hours = (deadline - datetime.now()).total_seconds() / 3600

    if hours < 0:
        return "OVERDUE"

    if hours <= 24:
        return "URGENT"

    if hours <= 96:
        return "APPROACHING"

    return "PLENTY OF TIME"


def status_style(status):
    if status == "OVERDUE":
        return "#FFE5E5", "#C62828"

    if status == "URGENT":
        return "#FFE5E5", "#D32F2F"

    if status == "APPROACHING":
        return "#FFF4D6", "#946200"

    if status == "COMPLETED":
        return "#E5F6EC", "#197044"

    return "#E5F6EC", "#197044"


def parse_start_time(value):
    return datetime.strptime(
        value,
        "%H:%M"
    ).time()


def format_time(dt):
    return dt.strftime("%I:%M %p")


def format_date(value):
    return value.strftime("%A, %d %B %Y")


def get_week_start():
    today = date.today()
    return today - timedelta(days=today.weekday())


def get_week_end():
    return get_week_start() + timedelta(days=6)


def safe_photo_name(original_name):
    extension = os.path.splitext(
        original_name
    )[1]

    return (
        str(uuid.uuid4())
        + extension
    )


def calculate_total_hours(
    number_of_units,
    hours_per_unit
):
    return (
        number_of_units
        * hours_per_unit
    )


def calculate_completed_units(plan):
    subject = plan["subject"]

    planned_units = plan["units"]

    unit_type = plan["unit_type"]

    matching_sessions = []

    for session in data["study_sessions"]:

        if session.get("subject") != subject:
            continue

        if session.get("unit_type") != unit_type:
            continue

        matching_sessions.append(session)

    completed_names = set()

    for session in matching_sessions:

        topic = session.get(
            "topic",
            ""
        ).strip()

        if topic:
            completed_names.add(topic)

    return min(
        len(completed_names),
        planned_units
    )


def get_planned_topics(plan):
    topics = []

    for number in range(
        1,
        plan["units"] + 1
    ):
        topics.append(
            f'{plan["unit_type"]} {number}'
        )

    return topics


def get_completed_topic_names(
    subject,
    unit_type
):
    completed = set()

    for session in data["study_sessions"]:

        if session.get("subject") != subject:
            continue

        if session.get("unit_type") != unit_type:
            continue

        topic = session.get(
            "topic",
            ""
        ).strip()

        if topic:
            completed.add(topic)

    return completed


def subject_study_hours():
    result = defaultdict(float)

    for session in data["study_sessions"]:
        result[
            session.get(
                "subject",
                "General"
            )
        ] += float(
            session.get(
                "duration",
                0
            )
        )

    return result


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:27px;
            font-weight:800;
            color:#20345F;
            margin-bottom:4px;
        ">
            📚 StudyZone
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Plan your studies. Track your progress. Stay on time."
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "⏰ Deadline Tracker",
            "🧠 Smart Timetable",
            "📚 Study Tracker",
            "📝 Notes Organizer",
            "📈 Weekly Progress"
        ]
    )

    st.markdown("---")

    student_name = st.text_input(
        "Student Name",
        value=data.get(
            "student_name",
            ""
        ),
        placeholder="Enter your name"
    )

    if student_name != data.get(
        "student_name",
        ""
    ):
        data["student_name"] = student_name
        save_data()

    st.markdown("---")

    st.caption(
        "StudyZone"
    )

    st.caption(
        "Plan • Study • Track • Achieve"
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    '<div class="main-header">📚 StudyZone</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-header">A simple place to manage your study plan, deadlines, notes and progress.</div>',
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.html(
        '<div class="section-header">🏠 Dashboard</div>'
    )

    if data.get("student_name"):
        st.write(
            f"Welcome back, {data['student_name']}!"
        )
    else:
        st.write(
            "Welcome! Start by adding your study tasks and plans."
        )

    tasks = data["tasks"]

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if task.get(
            "completed",
            False
        )
    )

    pending_tasks = (
        total_tasks
        - completed_tasks
    )

    urgent_tasks = 0
    overdue_tasks = 0

    for task in tasks:

        status = deadline_status(task)

        if status == "URGENT":
            urgent_tasks += 1

        if status == "OVERDUE":
            overdue_tasks += 1

    total_study_hours = sum(
        float(
            session.get(
                "duration",
                0
            )
        )
        for session in data[
            "study_sessions"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    dashboard_stats = [
        (
            c1,
            total_tasks,
            "Total Tasks"
        ),
        (
            c2,
            completed_tasks,
            "Completed"
        ),
        (
            c3,
            pending_tasks,
            "Pending"
        ),
        (
            c4,
            urgent_tasks,
            "Urgent"
        ),
        (
            c5,
            overdue_tasks,
            "Overdue"
        )
    ]

    for column, number, label in dashboard_stats:

        with column:

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">
                        {number}
                    </div>
                    <div class="stat-label">
                        {label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.html(
        '<div class="section-header">📊 Task Progress</div>'
    )

    if total_tasks > 0:

        percentage = (
            completed_tasks
            / total_tasks
        )

        st.progress(
            percentage
        )

        st.write(
            f"{completed_tasks} of "
            f"{total_tasks} tasks completed "
            f"({percentage * 100:.0f}%)"
        )

    else:

        st.info(
            "Add some tasks to start tracking your progress."
        )

    st.html(
        '<div class="section-header">📚 Study Overview</div>'
    )

    study_col1, study_col2, study_col3 = st.columns(3)

    with study_col1:

        st.metric(
            "Total Study Hours",
            f"{total_study_hours:.1f} hrs"
        )

    with study_col2:

        st.metric(
            "Study Sessions",
            len(
                data["study_sessions"]
            )
        )

    with study_col3:

        st.metric(
            "Study Plans",
            len(
                data["study_plans"]
            )
        )

    st.html(
        '<div class="section-header">⏰ Upcoming Deadlines</div>'
    )

    upcoming = []

    for task in tasks:

        if task.get(
            "completed",
            False
        ):
            continue

        deadline = task_deadline(task)

        if deadline >= datetime.now():

            upcoming.append(
                (
                    deadline,
                    task
                )
            )

    upcoming.sort(
        key=lambda item: item[0]
    )

    if upcoming:

        for deadline, task in upcoming[:5]:

            status = deadline_status(task)

            bg, text = status_style(
                status
            )

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        {task["task"]}
                    </div>

                    <div class="small-text">
                        📚 {task.get("subject", "General")}
                    </div>

                    <br>

                    📅 {deadline.strftime("%d %B %Y")}
                    <br>
                    ⏰ {deadline.strftime("%I:%M %p")}

                    <br><br>

                    <span style="
                        background:{bg};
                        color:{text};
                        padding:6px 12px;
                        border-radius:20px;
                        font-size:12px;
                        font-weight:700;
                    ">
                        {status}
                    </span>

                </div>
                """
            )

    else:

        st.info(
            "No upcoming deadlines."
        )


# ============================================================
# DEADLINE TRACKER
# ============================================================

elif page == "⏰ Deadline Tracker":

    st.html(
        '<div class="section-header">⏰ Deadline Tracker</div>'
    )

    st.write(
        "Add assignments, projects, submissions and other tasks. Your deadlines will be automatically organized by urgency."
    )

    with st.container(border=True):

        st.html(
            "➕ Add New Task"
        )

        task_name = st.text_input(
            "Task Name",
            placeholder="Example: Complete Accounts Assignment"
        )

        subject = st.text_input(
            "Subject",
            placeholder="Example: Accounts"
        )

        description = st.text_area(
            "Task Description",
            placeholder="Add any important details about this task."
        )

        date_col, time_col = st.columns(2)

        with date_col:

            deadline_date = st.date_input(
                "Deadline Date",
                value=date.today()
            )

        with time_col:

            deadline_time = st.time_input(
                "Deadline Time",
                value=time(
                    23,
                    59
                )
            )

        if st.button(
            "➕ Add Task",
            type="primary",
            use_container_width=True
        ):

            if not task_name.strip():

                st.warning(
                    "Please enter a task name."
                )

            else:

                new_task = {
                    "id": str(uuid.uuid4()),
                    "task": task_name.strip(),
                    "subject": (
                        subject.strip()
                        if subject.strip()
                        else "General"
                    ),
                    "description": description.strip(),
                    "deadline": datetime.combine(
                        deadline_date,
                        deadline_time
                    ).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "completed": False
                }

                data["tasks"].append(
                    new_task
                )

                save_data()

                st.success(
                    "Task added successfully."
                )

    st.html(
        '<div class="section-header">🔍 Find Your Tasks</div>'
    )

    search = st.text_input(
        "Search by task or subject",
        placeholder="Search..."
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        task_filter = st.selectbox(
            "Task Status",
            [
                "All",
                "Pending",
                "Completed",
                "Urgent",
                "Approaching",
                "Overdue"
            ]
        )

    with filter_col2:

        all_subjects = sorted(
            list(
                set(
                    task.get(
                        "subject",
                        "General"
                    )
                    for task in data["tasks"]
                )
            )
        )

        subject_filter = st.selectbox(
            "Subject",
            [
                "All Subjects"
            ] + all_subjects
        )

    displayed_any = False

    for index, task in enumerate(
        data["tasks"]
    ):

        task_text = (
            task["task"]
            + " "
            + task.get(
                "subject",
                ""
            )
        ).lower()

        if search.strip():

            if search.lower() not in task_text:
                continue

        if (
            subject_filter
            != "All Subjects"
        ):

            if task.get(
                "subject",
                "General"
            ) != subject_filter:
                continue

        status = deadline_status(task)

        if task_filter == "Pending":

            if task.get(
                "completed",
                False
            ):
                continue

        elif task_filter == "Completed":

            if not task.get(
                "completed",
                False
            ):
                continue

        elif task_filter == "Urgent":

            if status != "URGENT":
                continue

        elif task_filter == "Approaching":

            if status != "APPROACHING":
                continue

        elif task_filter == "Overdue":

            if status != "OVERDUE":
                continue

        displayed_any = True

        deadline = task_deadline(task)

        bg, text = status_style(
            status
        )

        st.html(
            f"""
            <div class="card">

                <div class="progress-title">
                    {task["task"]}
                </div>

                <div class="small-text">
                    📚 {task.get("subject", "General")}
                </div>

                <br>

                {task.get("description", "")}

                <br><br>

                📅
                {deadline.strftime("%d %B %Y")}

                &nbsp;&nbsp;

                ⏰
                {deadline.strftime("%I:%M %p")}

                <br><br>

                <span style="
                    background:{bg};
                    color:{text};
                    padding:6px 12px;
                    border-radius:20px;
                    font-size:12px;
                    font-weight:700;
                ">
                    {status}
                </span>

            </div>
            """
        )

        completed_now = st.checkbox(
            "Mark this task as completed",
            value=task.get(
                "completed",
                False
            ),
            key=f"complete_{task['id']}"
        )

        if (
            completed_now
            != task.get(
                "completed",
                False
            )
        ):

            task["completed"] = completed_now

            save_data()

            st.rerun()

        if not completed_now:

            hours_left = (
                deadline
                - datetime.now()
            ).total_seconds() / 3600

            if hours_left <= 1:

                st.error(
                    "Reminder: This deadline is within 1 hour."
                )

            elif hours_left <= 12:

                st.warning(
                    "Reminder: This deadline is within 12 hours."
                )

            elif hours_left <= 24:

                st.warning(
                    "Reminder: This deadline is within 1 day."
                )

            elif hours_left <= 48:

                st.info(
                    "Reminder: This deadline is within 2 days."
                )

            elif hours_left <= 96:

                st.info(
                    "Reminder: This deadline is within 4 days."
                )

            elif hours_left <= 168:

                st.info(
                    "Reminder: This deadline is within 7 days."
                )

        edit_col, delete_col = st.columns(2)

        with edit_col:

            if st.button(
                "✏️ Edit Task",
                key=f"edit_{task['id']}",
                use_container_width=True
            ):

                st.session_state.edit_task_id = task["id"]

        with delete_col:

            if st.button(
                "🗑️ Delete Task",
                key=f"delete_{task['id']}",
                use_container_width=True
            ):

                data["tasks"].pop(index)

                save_data()

                st.rerun()

        if (
            st.session_state.edit_task_id
            == task["id"]
        ):

            st.markdown(
                "### ✏️ Edit Task"
            )

            edited_name = st.text_input(
                "Task Name",
                value=task["task"],
                key=f"name_edit_{task['id']}"
            )

            edited_subject = st.text_input(
                "Subject",
                value=task.get(
                    "subject",
                    "General"
                ),
                key=f"subject_edit_{task['id']}"
            )

            edited_description = st.text_area(
                "Task Description",
                value=task.get(
                    "description",
                    ""
                ),
                key=f"description_edit_{task['id']}"
            )

            edited_date = st.date_input(
                "Deadline Date",
                value=deadline.date(),
                key=f"date_edit_{task['id']}"
            )

            edited_time = st.time_input(
                "Deadline Time",
                value=deadline.time(),
                key=f"time_edit_{task['id']}"
            )

            save_col, cancel_col = st.columns(2)

            with save_col:

                if st.button(
                    "💾 Save Changes",
                    key=f"save_edit_{task['id']}",
                    use_container_width=True
                ):

                    task["task"] = edited_name.strip()

                    task["subject"] = (
                        edited_subject.strip()
                        if edited_subject.strip()
                        else "General"
                    )

                    task["description"] = (
                        edited_description.strip()
                    )

                    task["deadline"] = (
                        datetime.combine(
                            edited_date,
                            edited_time
                        ).strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    )

                    save_data()

                    st.session_state.edit_task_id = None

                    st.rerun()

            with cancel_col:

                if st.button(
                    "Cancel",
                    key=f"cancel_edit_{task['id']}",
                    use_container_width=True
                ):

                    st.session_state.edit_task_id = None

                    st.rerun()

    if not displayed_any:

        st.info(
            "No tasks match your search or filter."
        )


# ============================================================
# SMART TIMETABLE
# ============================================================

elif page == "🧠 Smart Timetable":

    st.html(
        '<div class="section-header">🧠 Smart Timetable</div>'
    )

    st.write(
        "Tell the planner what you need to complete and how much time you can study. It will create an organized timetable for you."
    )

    st.markdown(
        "📌 Add Study Requirement"
    )

    subject = st.text_input(
        "Subject",
        placeholder="Example: Accounts"
    )

    st.markdown(
        "### Choose Study Content"
    )

    type_col1, type_col2 = st.columns(2)

    with type_col1:

        lecture_selected = st.button(
            "📖 Lectures",
            use_container_width=True
        )

    with type_col2:

        chapter_selected = st.button(
            "📚 Chapters",
            use_container_width=True
        )

    if "selected_study_type" not in st.session_state:

        st.session_state.selected_study_type = "Lectures"

    if lecture_selected:

        st.session_state.selected_study_type = "Lectures"

    if chapter_selected:

        st.session_state.selected_study_type = "Chapters"

    selected_type = st.session_state.selected_study_type

    if selected_type == "Lectures":

        st.info(
            "📖 Lecture planning selected"
        )

        units = st.number_input(
            "Pending/Remaining Lectures",
            min_value=1,
            max_value=500,
            value=1,
            step=1
        )

        hours_per_unit = st.number_input(
            "Approximate Time Needed to Complete One Lecture",
            min_value=0.25,
            max_value=24.0,
            value=1.0,
            step=0.25
        )

    else:

        st.success(
            "📚 Chapter planning selected"
        )

        units = st.number_input(
            "Pending/Remaining Chapters",
            min_value=1,
            max_value=500,
            value=1,
            step=1
        )

        hours_per_unit = st.number_input(
            "Approximate Time Needed to Complete One Chapter",
            min_value=0.25,
            max_value=24.0,
            value=2.0,
            step=0.25
        )

    total_hours = calculate_total_hours(
        units,
        hours_per_unit
    )

    st.html(
        f"""
        <div class="card">

            <div class="progress-title">
                📊 Study Time Calculation
            </div>

            <br>

            {int(units)}
            {selected_type.lower()}
            ×
            {hours_per_unit:.2f}
            hours each

            <br><br>

            <b>
            Total Study Time Required:
            {total_hours:.2f} hours
            </b>

        </div>
        """
    )

    st.markdown(
        "### ⚙️ Plan Your Study Schedule"
    )

    completion_days = st.number_input(
        "How Many Days Needed to Complete This Chapter or Lecture",
        min_value=1,
        max_value=365,
        value=1,
        step=1
    )

    daily_hours = st.number_input(
        "How Many Hours Can You Study Each Day",
        min_value=0.5,
        max_value=24.0,
        value=5.0,
        step=0.5
    )

    preferred_start = st.time_input(
        "Preferred Study Start Time",
        value=time(
            9,
            0
        )
    )

    break_minutes = st.number_input(
        "Break Time Between Subjects",
        min_value=0,
        max_value=180,
        value=60,
        step=15
    )

    st.markdown("")

    if st.button(
        "➕ Add to Study Plan",
        type="primary",
        use_container_width=True
    ):

        if not subject.strip():

            st.warning(
                "Please enter a subject."
            )

        else:

            new_plan = {
                "id": str(uuid.uuid4()),
                "subject": subject.strip(),
                "unit_type": selected_type,
                "units": int(units),
                "hours_per_unit": float(
                    hours_per_unit
                ),
                "total_hours": float(
                    total_hours
                ),
                "completion_days": int(
                    completion_days
                ),
                "daily_hours": float(
                    daily_hours
                ),
                "start_time": preferred_start.strftime(
                    "%H:%M"
                ),
                "break_minutes": int(
                    break_minutes
                ),
                "created": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }

            data["study_plans"].append(
                new_plan
            )

            save_data()

            st.success(
                "Study requirement added to your study plan."
            )

    st.markdown("---")

    st.markdown(
        "### 📚 Your Study Plan"
    )

    if data["study_plans"]:

        for index, plan in enumerate(
            data["study_plans"]
        ):

            completed_units = calculate_completed_units(
                plan
            )

            progress = (
                completed_units
                / plan["units"]
            )

            type_icon = (
                "📖"
                if plan["unit_type"] == "Lectures"
                else "📚"
            )

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        {type_icon} {plan["subject"]}
                    </div>

                    <div class="small-text">
                        {plan["unit_type"]}
                    </div>

                    <br>

                    <b>Pending/Remaining:</b>
                    {plan["units"]}

                    <br>

                    <b>Time Needed for One:</b>
                    {plan["hours_per_unit"]:.2f} hours

                    <br>

                    <b>Total Study Time:</b>
                    {plan["total_hours"]:.2f} hours

                    <br>

                    <b>Completion:</b>
                    {plan["completion_days"]} day(s)

                    <br>

                    <b>Daily Study Time:</b>
                    {plan["daily_hours"]:.2f} hours

                    <br><br>

                    <b>Progress:</b>
                    {completed_units}
                    /
                    {plan["units"]}

                </div>
                """
            )

            st.progress(
                progress
            )

            if st.button(
                "🗑️ Remove from Study Plan",
                key=f"remove_plan_{plan['id']}",
                use_container_width=True
            ):

                data["study_plans"].pop(
                    index
                )

                save_data()

                st.rerun()

    else:

        st.info(
            "Your study requirements will appear here after you add them."
        )

    st.markdown("---")

    st.markdown(
        "### 🧠 Generate Smart Timetable"
    )


    if st.button(
        "🧠 Generate Smart Timetable",
        type="primary",
        use_container_width=True
    ):

        if not data["study_plans"]:

            st.warning(
                "Please add at least one study requirement first."
            )

        else:

            generated = []

            today = date.today()

            for day_offset in range(365):

                current_day = (
                    today
                    + timedelta(
                        days=day_offset
                    )
                )

                active_plans = []

                for plan in data["study_plans"]:

                    created_date = datetime.strptime(
                        plan["created"],
                        "%Y-%m-%d %H:%M"
                    ).date()

                    days_from_creation = (
                        current_day
                        - created_date
                    ).days

                    if (
                        0
                        <= days_from_creation
                        < plan["completion_days"]
                    ):

                        active_plans.append(
                            plan
                        )

                if not active_plans:
                    continue

                day_capacity = sum(
                    plan["daily_hours"]
                    for plan in active_plans
                )

                if day_capacity <= 0:
                    continue

                current_datetime = datetime.combine(
                    current_day,
                    parse_start_time(
                        active_plans[0][
                            "start_time"
                        ]
                    )
                )

                for plan in active_plans:

                    elapsed_days = (
                        current_day
                        - datetime.strptime(
                            plan["created"],
                            "%Y-%m-%d %H:%M"
                        ).date()
                    ).days

                    total_daily_target = (
                        plan["daily_hours"]
                    )

                    already_generated = 0

                    for old_session in generated:

                        if (
                            old_session["plan_id"]
                            == plan["id"]
                            and old_session["date"]
                            < current_day.isoformat()
                        ):

                            already_generated += old_session[
                                "hours"
                            ]

                    remaining = max(
                        0,
                        plan["total_hours"]
                        - already_generated
                    )

                    if remaining <= 0:
                        continue

                    session_hours = min(
                        total_daily_target,
                        remaining
                    )

                    if session_hours <= 0:
                        continue

                    start_dt = current_datetime

                    end_dt = (
                        start_dt
                        + timedelta(
                            minutes=int(
                                session_hours
                                * 60
                            )
                        )
                    )

                    generated.append(
                        {
                            "id": str(uuid.uuid4()),
                            "plan_id": plan["id"],
                            "date": current_day.isoformat(),
                            "subject": plan["subject"],
                            "unit_type": plan["unit_type"],
                            "hours": round(
                                session_hours,
                                2
                            ),
                            "start": start_dt.strftime(
                                "%H:%M"
                            ),
                            "end": end_dt.strftime(
                                "%H:%M"
                            )
                        }
                    )

                    current_datetime = (
                        end_dt
                        + timedelta(
                            minutes=plan[
                                "break_minutes"
                            ]
                        )
                    )

            data["generated_timetable"] = generated

            save_data()

            st.success(
                "Your personalized smart timetable is ready."
            )

    st.markdown("---")

    st.markdown(
        "### 📅 Your Personalized Timetable"
    )

    timetable = data.get(
        "generated_timetable",
        []
    )

    if timetable:

        grouped = defaultdict(list)

        for item in timetable:

            grouped[
                item["date"]
            ].append(item)

        for day_key in sorted(
            grouped.keys()
        ):

            day_date = datetime.strptime(
                day_key,
                "%Y-%m-%d"
            ).date()

            st.markdown(
                f"#### 📅 {format_date(day_date)}"
            )

            day_items = grouped[
                day_key
            ]

            for position, item in enumerate(
                day_items
            ):

                bar_class = (
                    "lecture-bar"
                    if item["unit_type"]
                    == "Lectures"
                    else "chapter-bar"
                )

                icon = (
                    "📖"
                    if item["unit_type"]
                    == "Lectures"
                    else "📚"
                )

                st.html(
                    f"""
                    <div class="study-bar {bar_class}">

                        <div class="bar-title">
                            {icon}
                            {item["subject"]}
                        </div>

                        <div class="bar-info">
                            {item["unit_type"]} Study
                        </div>

                        <div class="bar-time">
                            {datetime.strptime(
                                item["start"],
                                "%H:%M"
                            ).strftime("%I:%M %p")}
                            -
                            {datetime.strptime(
                                item["end"],
                                "%H:%M"
                            ).strftime("%I:%M %p")}
                        </div>

                        <div class="bar-info">
                            {item["hours"]:.2f} hours of study
                        </div>

                    </div>
                    """
                )

                if position < len(day_items) - 1:

                    next_item = day_items[
                        position + 1
                    ]

                    current_end = datetime.strptime(
                        item["end"],
                        "%H:%M"
                    )

                    next_start = datetime.strptime(
                        next_item["start"],
                        "%H:%M"
                    )

                    break_minutes = int(
                        (
                            next_start
                            - current_end
                        ).total_seconds()
                        / 60
                    )

                    if break_minutes > 0:

                        break_end = (
                            current_end
                            + timedelta(
                                minutes=break_minutes
                            )
                        )

                        st.markdown(
                            f"""
                            <div class="break-bar">
                                ☕ Break
                                &nbsp;&nbsp;
                                {format_time(current_end)}
                                -
                                {format_time(break_end)}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    else:

        st.info(
            "Add your study requirements and generate the timetable to see your schedule here."
        )


# ============================================================
# STUDY TRACKER
# ============================================================

elif page == "📚 Study Tracker":

    st.html(
        '<div class="section-header">📚 Study Tracker</div>'
    )

    st.write(
        "Record what you actually study and keep track of your progress subject by subject."
    )

    st.markdown(
        "➕ Record Study Session"
    )

    with st.container(border=True):

        session_subject = st.text_input(
            "Subject",
            placeholder="Example: Accounts"
        )

        matching_plans = [
            plan
            for plan in data["study_plans"]
            if plan["subject"].lower()
            == session_subject.strip().lower()
        ]

        selected_unit_type = st.selectbox(
            "Study Type",
            [
                "Lectures",
                "Chapters",
                "Revision"
            ]
        )

        if matching_plans:

            matching_types = [
                plan["unit_type"]
                for plan in matching_plans
            ]

            if selected_unit_type not in matching_types:

                selected_unit_type = st.selectbox(
                    "Study Type",
                    matching_types,
                    key="matching_type_selector"
                )

        session_topic = st.text_input(
            "Chapter or Lecture Completed",
            placeholder="Example: Chapter 3"
        )

        session_date = st.date_input(
            "Study Date",
            value=date.today()
        )

        session_duration = st.number_input(
            "How Many Hours Did You Study?",
            min_value=0.25,
            max_value=24.0,
            value=1.0,
            step=0.25
        )

        if st.button(
            "➕ Record Study Session",
            type="primary",
            use_container_width=True
        ):

            if not session_subject.strip():

                st.warning(
                    "Please enter a subject."
                )

            elif not session_topic.strip():

                st.warning(
                    "Please enter the chapter or lecture you studied."
                )

            else:

                data["study_sessions"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "subject": session_subject.strip(),
                        "unit_type": selected_unit_type,
                        "topic": session_topic.strip(),
                        "date": session_date.isoformat(),
                        "duration": float(
                            session_duration
                        )
                    }
                )

                save_data()

                st.success(
                    "Study session recorded successfully."
                )

    st.html("---")

    st.markdown(
        "### 📊 Subject-wise Study Time"
    )

    hours_by_subject = subject_study_hours()

    if hours_by_subject:

        total_hours = sum(
            hours_by_subject.values()
        )

        for subject_name, hours in sorted(
            hours_by_subject.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            percentage = (
                hours
                / total_hours
                if total_hours
                else 0
            )

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        📚 {subject_name}
                    </div>

                    <br>

                    <b>
                    {hours:.2f} study hours
                    </b>

                </div>
                """
            )

            st.progress(
                percentage
            )

    else:

        st.info(
            "Your subject-wise study time will appear here."
        )

    st.markdown(
        "### 📖 Chapter and Lecture Progress"
    )

    if data["study_plans"]:

        for plan in data["study_plans"]:

            completed_topics = (
                get_completed_topic_names(
                    plan["subject"],
                    plan["unit_type"]
                )
            )

            planned_topics = get_planned_topics(
                plan
            )

            completed_count = min(
                len(completed_topics),
                plan["units"]
            )

            progress = (
                completed_count
                / plan["units"]
            )

            icon = (
                "📖"
                if plan["unit_type"]
                == "Lectures"
                else "📚"
            )

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        {icon} {plan["subject"]}
                    </div>

                    <div class="small-text">
                        {plan["unit_type"]}
                    </div>

                    <br>

                    <b>
                    {completed_count}
                    of
                    {plan["units"]}
                    completed
                    </b>

                </div>
                """
            )

            st.progress(
                progress
            )

            for topic in planned_topics:

                if topic in completed_topics:

                    st.success(
                        f"✓ {topic} - Completed"
                    )

                else:

                    st.write(
                        f"○ {topic} - Pending"
                    )

    else:

        st.info(
            "Add a lecture or chapter study plan first."
        )

    st.markdown(
        "### 📝 Study History"
    )

    if data["study_sessions"]:

        for session in reversed(
            data["study_sessions"]
        ):

            icon = (
                "📖"
                if session["unit_type"]
                == "Lectures"
                else "📚"
            )

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        {icon}
                        {session["subject"]}
                    </div>

                    <div class="small-text">
                        {session["unit_type"]}
                    </div>

                    <br>

                    📝 {session["topic"]}

                    <br>

                    📅 {session["date"]}

                    <br>

                    ⏱️ {session["duration"]:.2f} hours

                </div>
                """
            )

    else:

        st.info(
            "No study sessions recorded yet."
        )


# ============================================================
# NOTES ORGANIZER
# ============================================================

elif page == "📝 Notes Organizer":

    st.markdown(
        '<div class="section-header">📝 Notes Organizer</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Keep your written notes, important information and study photos organized by subject."
    )

    st.markdown(
        "### ➕ Create a New Note"
    )

    note_title = st.text_input(
        "Note Title",
        placeholder="Example: Partnership Important Points"
    )

    note_subject = st.text_input(
        "Subject",
        placeholder="Example: Accounts"
    )

    note_topic = st.text_input(
        "Topic",
        placeholder="Example: Partnership"
    )

    note_content = st.text_area(
        "Write Your Notes",
        height=220,
        placeholder="Write your important points here..."
    )

    uploaded_photos = st.file_uploader(
        "Add Photos to Your Note",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        accept_multiple_files=True
    )

    if st.button(
        "💾 Save Note",
        type="primary",
        use_container_width=True
    ):

        if not note_title.strip():

            st.warning(
                "Please enter a note title."
            )

        else:

            photo_paths = []

            if uploaded_photos:

                for uploaded in uploaded_photos:

                    filename = safe_photo_name(
                        uploaded.name
                    )

                    path = os.path.join(
                        PHOTO_FOLDER,
                        filename
                    )

                    with open(
                        path,
                        "wb"
                    ) as file:

                        file.write(
                            uploaded.getbuffer()
                        )

                    photo_paths.append(
                        path
                    )

            new_note = {
                "id": str(uuid.uuid4()),
                "title": note_title.strip(),
                "subject": (
                    note_subject.strip()
                    if note_subject.strip()
                    else "General"
                ),
                "topic": note_topic.strip(),
                "content": note_content.strip(),
                "photos": photo_paths,
                "created": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }

            data["notes"].append(
                new_note
            )

            save_data()

            st.success(
                "Your note has been saved."
            )

    st.markdown("---")

    st.markdown(
        "### 🔍 Find Your Notes"
    )

    note_search = st.text_input(
        "Search Notes",
        placeholder="Search by title, subject or topic..."
    )

    subjects = sorted(
        list(
            set(
                note.get(
                    "subject",
                    "General"
                )
                for note in data["notes"]
            )
        )
    )

    note_filter = st.selectbox(
        "Filter by Subject",
        [
            "All Subjects"
        ] + subjects
    )

    shown_notes = False

    for index, note in enumerate(
        data["notes"]
    ):

        searchable = (
            note.get("title", "")
            + " "
            + note.get("subject", "")
            + " "
            + note.get("topic", "")
            + " "
            + note.get("content", "")
        ).lower()

        if (
            note_search.strip()
            and note_search.lower()
            not in searchable
        ):
            continue

        if (
            note_filter
            != "All Subjects"
            and note.get(
                "subject",
                "General"
            )
            != note_filter
        ):
            continue

        shown_notes = True

        st.html(
            f"""
            <div class="note-card">

                <div class="note-title">
                    📝 {note["title"]}
                </div>

                <div class="small-text">
                    📚 {note.get("subject", "General")}
                    &nbsp;&nbsp;
                    📖 {note.get("topic", "")}
                </div>

                <br>

                {note.get("content", "")}

                <br><br>

                <div class="small-text">
                    Created:
                    {note.get("created", "")}
                </div>

            </div>
            """
        )

        photos = note.get(
            "photos",
            []
        )

        if photos:

            st.markdown(
                "**🖼️ Photos attached to this note**"
            )

            photo_columns = st.columns(
                min(
                    3,
                    len(photos)
                )
            )

            for photo_index, path in enumerate(
                photos
            ):

                if os.path.exists(path):

                    with photo_columns[
                        photo_index
                        % len(photo_columns)
                    ]:

                        st.image(
                            path,
                            use_container_width=True
                        )

        edit_col, delete_col = st.columns(2)

        with edit_col:

            if st.button(
                "✏️ Edit Note",
                key=f"edit_note_{note['id']}",
                use_container_width=True
            ):

                st.session_state.edit_note_id = note["id"]

        with delete_col:

            if st.button(
                "🗑️ Delete Note",
                key=f"delete_note_{note['id']}",
                use_container_width=True
            ):

                for photo in note.get(
                    "photos",
                    []
                ):

                    if os.path.exists(photo):

                        try:
                            os.remove(photo)
                        except Exception:
                            pass

                data["notes"].pop(index)

                save_data()

                st.rerun()

        if (
            st.session_state.edit_note_id
            == note["id"]
        ):

            st.markdown(
                "### ✏️ Edit Note"
            )

            edited_title = st.text_input(
                "Note Title",
                value=note["title"],
                key=f"title_edit_{note['id']}"
            )

            edited_subject = st.text_input(
                "Subject",
                value=note.get(
                    "subject",
                    "General"
                ),
                key=f"subject_edit_note_{note['id']}"
            )

            edited_topic = st.text_input(
                "Topic",
                value=note.get(
                    "topic",
                    ""
                ),
                key=f"topic_edit_{note['id']}"
            )

            edited_content = st.text_area(
                "Notes",
                value=note.get(
                    "content",
                    ""
                ),
                height=200,
                key=f"content_edit_{note['id']}"
            )

            new_photos = st.file_uploader(
                "Add More Photos",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],
                accept_multiple_files=True,
                key=f"photos_edit_{note['id']}"
            )

            save_note_col, cancel_note_col = st.columns(2)

            with save_note_col:

                if st.button(
                    "💾 Save Changes",
                    key=f"save_note_{note['id']}",
                    use_container_width=True
                ):

                    note["title"] = edited_title.strip()

                    note["subject"] = (
                        edited_subject.strip()
                        if edited_subject.strip()
                        else "General"
                    )

                    note["topic"] = edited_topic.strip()

                    note["content"] = edited_content.strip()

                    if new_photos:

                        for uploaded in new_photos:

                            filename = safe_photo_name(
                                uploaded.name
                            )

                            path = os.path.join(
                                PHOTO_FOLDER,
                                filename
                            )

                            with open(
                                path,
                                "wb"
                            ) as file:

                                file.write(
                                    uploaded.getbuffer()
                                )

                            note["photos"].append(
                                path
                            )

                    save_data()

                    st.session_state.edit_note_id = None

                    st.rerun()

            with cancel_note_col:

                if st.button(
                    "Cancel",
                    key=f"cancel_note_{note['id']}",
                    use_container_width=True
                ):

                    st.session_state.edit_note_id = None

                    st.rerun()

    if not shown_notes:

        if data["notes"]:

            st.info(
                "No notes match your search."
            )

        else:

            st.info(
                "You have not created any notes yet."
            )


# ============================================================
# WEEKLY PROGRESS
# ============================================================

elif page == "📈 Weekly Progress":

    st.markdown(
        '<div class="section-header">📈 Weekly Progress</div>',
        unsafe_allow_html=True
    )

    week_start = get_week_start()
    week_end = get_week_end()

    st.write(
        f"This week: "
        f"{week_start.strftime('%d %B %Y')}"
        f" to "
        f"{week_end.strftime('%d %B %Y')}"
    )

    weekly_sessions = []

    for session in data["study_sessions"]:

        try:

            session_date = datetime.strptime(
                session["date"],
                "%Y-%m-%d"
            ).date()

        except Exception:

            continue

        if (
            week_start
            <= session_date
            <= week_end
        ):

            weekly_sessions.append(
                session
            )

    weekly_hours = sum(
        float(
            session.get(
                "duration",
                0
            )
        )
        for session in weekly_sessions
    )

    weekly_tasks = []

    for task in data["tasks"]:

        deadline = task_deadline(task).date()

        if (
            week_start
            <= deadline
            <= week_end
        ):

            weekly_tasks.append(
                task
            )

    completed_weekly_tasks = sum(
        1
        for task in weekly_tasks
        if task.get(
            "completed",
            False
        )
    )

    task_percentage = (
        completed_weekly_tasks
        / len(weekly_tasks)
        if weekly_tasks
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Weekly Study Hours",
            f"{weekly_hours:.1f}"
        )

    with c2:

        st.metric(
            "Weekly Tasks",
            len(weekly_tasks)
        )

    with c3:

        st.metric(
            "Tasks Completed",
            f"{task_percentage * 100:.0f}%"
        )

    st.markdown(
        "### 📚 Subject-wise Weekly Study"
    )

    weekly_subjects = defaultdict(float)

    for session in weekly_sessions:

        weekly_subjects[
            session["subject"]
        ] += float(
            session["duration"]
        )

    if weekly_subjects:

        for subject_name, hours in sorted(
            weekly_subjects.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            st.html(
                f"""
                <div class="card">

                    <div class="progress-title">
                        📚 {subject_name}
                    </div>

                    <br>

                    {hours:.2f} study hours

                </div>
                """
            )

    else:

        st.info(
            "No study sessions have been recorded this week."
        )

    st.markdown(
        "### 📅 Daily Study Progress"
    )

    daily_hours = defaultdict(float)

    for session in weekly_sessions:

        daily_hours[
            session["date"]
        ] += float(
            session["duration"]
        )

    for day_number in range(7):

        current_day = (
            week_start
            + timedelta(
                days=day_number
            )
        )

        key = current_day.isoformat()

        hours = daily_hours.get(
            key,
            0
        )

        st.write(
            f"**{current_day.strftime('%A, %d %B')}** "
            f"— {hours:.2f} hours"
        )

        st.progress(
            min(
                hours / 8,
                1
            )
        )

    st.markdown(
        "### 📖 Chapters and Lectures Completed This Week"
    )

    completed_this_week = []

    for session in weekly_sessions:

        topic = session.get(
            "topic",
            ""
        ).strip()

        if topic:

            completed_this_week.append(
                session
            )

    if completed_this_week:

        for session in completed_this_week:

            icon = (
                "📖"
                if session["unit_type"]
                == "Lectures"
                else "📚"
            )

            st.success(
                f"{icon} "
                f"{session['subject']} — "
                f"{session['topic']} completed"
            )

    else:

        st.info(
            "No chapters or lectures have been marked as completed this week."
        )

    st.markdown(
        "### 🎯 Your Weekly Summary"
    )

    if weekly_hours == 0 and not weekly_tasks:

        st.info(
            "Start recording your study sessions and deadlines to see your weekly summary."
        )

    else:

        if weekly_hours >= 20:

            st.success(
                "Excellent study effort this week. Keep it going!"
            )

        elif weekly_hours >= 10:

            st.info(
                "Good progress this week. You are building a consistent routine."
            )

        else:

            st.warning(
                "Try to increase your study consistency over the next few days."
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "StudyZone • Plan your work • Track your progress • Stay organized"
)
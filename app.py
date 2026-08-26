import streamlit as st
import json
import os
import random
from datetime import date, datetime, timedelta
from collections import defaultdict

# ============================================================
# HOUSE POINTS v2
# Fair competition + profiles + rewards + mobile UI
# ============================================================

st.set_page_config(
    page_title="House Points",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "house_points_data.json"

KIDS = ["Myron", "Brodie"]

# Monday=0 ... Sunday=6
DEFAULT_AVAILABILITY = {
    "Myron": [0, 1, 2, 3, 4, 5, 6],
    "Brodie": [2, 5],
}

DEFAULT_PIN = "1234"

# ============================================================
# TASKS
# ============================================================

TASK_MENU = {
    "⚡ Quick Jobs": {
        "Water the plants": 1,
        "Empty the dishwasher": 2,
        "Load the dishwasher": 2,
        "Empty a kitchen bin": 1,
        "Set the table": 1,
        "Clear the table": 1,
    },

    "🧹 Medium Jobs": {
        "Take bins out to the curb": 3,
        "Bring empty bins back in": 2,
        "Hoover a room": 4,
        "Sort and put out recycling": 3,
        "Tidy the shoe/coat area": 3,
        "Dust downstairs surfaces": 3,
    },

    "💪 Bigger Jobs": {
        "Help with the grass": 6,
        "Wash the car": 6,
        "Change bed sheets": 5,
        "Full bathroom clean": 8,
    },

    "📚 Personal Growth": {
        "Finished a book": 10,
        "Learned a new skill/fact": 10,
        "Practised an instrument/hobby": 5,
    },

    "🛏️ Own Room": {
        "Tidied own bedroom": 2,
    },
}

# ============================================================
# DEFAULT REWARDS
# ============================================================

DEFAULT_REWARDS = [
    {
        "name": "30 Minutes Device Time",
        "points": 10,
        "description": "30 minutes Xbox/tablet/device time",
        "emoji": "🎮",
    },
    {
        "name": "1 Hour Device Time",
        "points": 20,
        "description": "One hour of device time",
        "emoji": "🎮",
    },
    {
        "name": "Choose the Friday Film",
        "points": 25,
        "description": "You choose the family film",
        "emoji": "🎬",
    },
    {
        "name": "Choose Family Activity",
        "points": 40,
        "description": "Choose what the family does",
        "emoji": "🏃",
    },
    {
        "name": "£2 Pocket Money",
        "points": 50,
        "description": "£2 pocket money",
        "emoji": "💷",
    },
]

# ============================================================
# BADGES
# ============================================================

BADGES = [
    {
        "id": "first_task",
        "name": "First Step",
        "emoji": "👣",
        "description": "Complete your first task.",
    },
    {
        "id": "ten_tasks",
        "name": "Busy Bee",
        "emoji": "🐝",
        "description": "Complete 10 tasks.",
    },
    {
        "id": "fifty_points",
        "name": "Point Collector",
        "emoji": "⭐",
        "description": "Earn 50 points.",
    },
    {
        "id": "hundred_points",
        "name": "Century Club",
        "emoji": "💯",
        "description": "Earn 100 points.",
    },
    {
        "id": "three_day_streak",
        "name": "On Fire",
        "emoji": "🔥",
        "description": "Complete tasks on 3 consecutive days.",
    },
    {
        "id": "seven_day_streak",
        "name": "Unstoppable",
        "emoji": "🚀",
        "description": "Complete tasks on 7 consecutive days.",
    },
    {
        "id": "challenge",
        "name": "Challenge Accepted",
        "emoji": "🎯",
        "description": "Complete a weekly challenge.",
    },
    {
        "id": "helper",
        "name": "Super Helper",
        "emoji": "🤝",
        "description": "Be named Helper of the Week.",
    },
]

# ============================================================
# DEFAULT CHALLENGE
# ============================================================

DEFAULT_CHALLENGE = {
    "title": "The Weekend Challenge",
    "description": "Complete 3 jobs while you're here.",
    "target": 3,
    "bonus": 10,
}

# ============================================================
# BIN SCHEDULE
# ============================================================

BLACK_BIN_ANCHOR = date(2025, 12, 9)


def bin_type_for_date(d):
    days_since_anchor = (d - BLACK_BIN_ANCHOR).days
    weeks_since_anchor = days_since_anchor // 7

    if weeks_since_anchor % 2 == 0:
        return "Black bin (general waste)"

    return "Recycling + food waste caddy"


def next_tuesday(d):
    days_ahead = (1 - d.weekday()) % 7
    return d + timedelta(days=days_ahead)


# ============================================================
# DATA
# ============================================================

def default_data():
    return {
        "balances": {kid: 0 for kid in KIDS},

        "log": [],

        "redemptions": [],

        "rewards": DEFAULT_REWARDS.copy(),

        "availability": DEFAULT_AVAILABILITY.copy(),

        "challenge": DEFAULT_CHALLENGE.copy(),

        "challenge_progress": {kid: 0 for kid in KIDS},

        "helper_awards": [],

        "profiles": {
            kid: {
                "badges": [],
                "colour": "",
            }
            for kid in KIDS
        },

        "settings": {
            "parent_pin": DEFAULT_PIN,
        },
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return default_data()

    defaults = default_data()

    for key, value in defaults.items():
        if key not in data:
            data[key] = value

    for kid in KIDS:

        if kid not in data["balances"]:
            data["balances"][kid] = 0

        if kid not in data["availability"]:
            data["availability"][kid] = DEFAULT_AVAILABILITY.get(
                kid, []
            )

        if kid not in data["challenge_progress"]:
            data["challenge_progress"][kid] = 0

        if kid not in data["profiles"]:
            data["profiles"][kid] = {
                "badges": [],
                "colour": "",
            }

    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ============================================================
# DATE HELPERS
# ============================================================

TODAY = date.today()


def week_start(d=None):
    if d is None:
        d = TODAY

    return d - timedelta(days=d.weekday())


def previous_week_start():
    return week_start() - timedelta(days=7)


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()
    except Exception:
        return TODAY


def in_current_week(d):
    return d >= week_start()


def in_previous_week(d):
    return previous_week_start() <= d < week_start()


# ============================================================
# AVAILABILITY
# ============================================================

def kid_available(kid, d):
    return d.weekday() in data["availability"].get(
        kid,
        []
    )


def available_days(kid, start, end):
    count = 0
    current = start

    while current < end:

        if kid_available(kid, current):
            count += 1

        current += timedelta(days=1)

    return count


def available_days_this_week(kid):
    return available_days(
        kid,
        week_start(),
        week_start() + timedelta(days=7)
    )


# ============================================================
# POINT CALCULATIONS
# ============================================================

def approved_entries():
    return [
        e for e in data["log"]
        if e.get("approved", True)
    ]


def points_between(kid, start, end):
    total = 0

    for entry in approved_entries():

        if entry.get("kid") != kid:
            continue

        d = parse_date(entry.get("date"))

        if start <= d < end:
            total += int(entry.get("points", 0))

    return total


def points_this_week(kid):
    return points_between(
        kid,
        week_start(),
        week_start() + timedelta(days=7)
    )


def points_previous_week(kid):
    return points_between(
        kid,
        previous_week_start(),
        week_start()
    )


def tasks_this_week(kid):
    count = 0

    for entry in approved_entries():

        if entry.get("kid") != kid:
            continue

        d = parse_date(entry.get("date"))

        if in_current_week(d):
            count += 1

    return count


def total_tasks(kid):
    return sum(
        1
        for entry in approved_entries()
        if entry.get("kid") == kid
    )


def total_points_earned(kid):
    return sum(
        int(entry.get("points", 0))
        for entry in approved_entries()
        if entry.get("kid") == kid
    )


def points_per_available_day(kid):
    days = available_days_this_week(kid)

    if days <= 0:
        return 0

    return points_this_week(kid) / days


# ============================================================
# FAIRNESS SCORE
# ============================================================

def fairness_score(kid):
    """
    Fairness score is NOT simply the points total.

    It considers:
      1. points per available day
      2. tasks completed
      3. improvement versus previous week

    The score is normalised against the best child.
    """

    daily_scores = {
        child: points_per_available_day(child)
        for child in KIDS
    }

    max_daily = max(
        daily_scores.values()
    ) if daily_scores else 0

    if max_daily <= 0:
        daily_component = 0
    else:
        daily_component = (
            daily_scores[kid] / max_daily
        ) * 60

    # Task participation
    task_scores = {
        child: tasks_this_week(child)
        for child in KIDS
    }

    max_tasks = max(
        task_scores.values()
    ) if task_scores else 0

    if max_tasks <= 0:
        task_component = 0
    else:
        task_component = (
            task_scores[kid] / max_tasks
        ) * 20

    # Improvement
    improvement = improvement_percentage(kid)

    if improvement <= 0:
        improvement_component = 0
    else:
        improvement_component = min(
            improvement,
            100
        ) / 100 * 20

    return round(
        daily_component
        + task_component
        + improvement_component,
        1
    )


def improvement_percentage(kid):
    current = points_this_week(kid)
    previous = points_previous_week(kid)

    if previous == 0:

        if current > 0:
            return 100

        return 0

    return (
        (current - previous)
        / previous
    ) * 100


# ============================================================
# STREAKS
# ============================================================

def task_dates(kid):

    dates = set()

    for entry in approved_entries():

        if entry.get("kid") == kid:
            dates.add(
                parse_date(entry.get("date"))
            )

    return dates


def current_streak(kid):

    dates = task_dates(kid)

    if not dates:
        return 0

    streak = 0
    check = TODAY

    while check in dates:

        streak += 1
        check -= timedelta(days=1)

    return streak


# ============================================================
# BADGES
# ============================================================

def badge_unlocked(kid, badge_id):

    badges = data["profiles"][kid].get(
        "badges",
        []
    )

    return badge_id in badges


def award_badges(kid):

    unlocked = data["profiles"][kid].setdefault(
        "badges",
        []
    )

    total_tasks_done = total_tasks(kid)
    total_points = total_points_earned(kid)
    streak = current_streak(kid)
    challenge_done = (
        data["challenge_progress"].get(kid, 0)
        >= data["challenge"]["target"]
    )

    checks = {
        "first_task": total_tasks_done >= 1,
        "ten_tasks": total_tasks_done >= 10,
        "fifty_points": total_points >= 50,
        "hundred_points": total_points >= 100,
        "three_day_streak": streak >= 3,
        "seven_day_streak": streak >= 7,
        "challenge": challenge_done,
        "helper": any(
            a.get("kid") == kid
            for a in data["helper_awards"]
        ),
    }

    newly_unlocked = []

    for badge_id, unlocked_now in checks.items():

        if unlocked_now and badge_id not in unlocked:

            unlocked.append(badge_id)
            newly_unlocked.append(badge_id)

    if newly_unlocked:
        save_data(data)

    return newly_unlocked


# ============================================================
# TRANSACTIONS
# ============================================================

def add_points(
    kid,
    points,
    task,
    note="",
    approved=True
):

    entry = {
        "date": TODAY.isoformat(),
        "kid": kid,
        "task": task,
        "points": int(points),
        "note": note,
        "approved": approved,
    }

    data["log"].append(entry)

    if approved:
        data["balances"][kid] += int(points)

        data["challenge_progress"][kid] += 1

    newly_unlocked = award_badges(kid)

    save_data(data)

    return newly_unlocked


def award_bonus(kid, points, reason):

    data["balances"][kid] += int(points)

    data["log"].append(
        {
            "date": TODAY.isoformat(),
            "kid": kid,
            "task": reason,
            "points": int(points),
            "note": "Parent bonus",
            "approved": True,
        }
    )

    award_badges(kid)

    save_data(data)


# ============================================================
# CSS — MOBILE FIRST
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 700px;
    }

    .stButton > button {
        min-height: 48px;
        border-radius: 12px;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        border-radius: 14px;
        padding: 10px;
    }

    div[data-testid="stExpander"] {
        border-radius: 14px;
    }

    .hero-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 12px;
    }

    .big-number {
        font-size: 38px;
        font-weight: 800;
        line-height: 1;
    }

    .small-muted {
        opacity: .7;
        font-size: 13px;
    }

    .reward-card {
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "parent_mode" not in st.session_state:
    st.session_state.parent_mode = False

if "selected_kid" not in st.session_state:
    st.session_state.selected_kid = KIDS[0]


# ============================================================
# HEADER
# ============================================================

st.title("🏠 House Points")

st.caption(
    "Earn it • Achieve it • Win it"
)

# ============================================================
# BIN CARD
# ============================================================

bin_day = next_tuesday(TODAY)
bin_due = bin_type_for_date(bin_day)

with st.container(border=True):

    st.subheader("🗑️ Next Bin Day")

    st.write(
        f"**{bin_day.strftime('%A %d %B')}**"
    )

    st.write(
        f"Put out: **{bin_due}**"
    )


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Navigate",
    [
        "🏠 Home",
        "👦 My Profile",
        "✅ Chores",
        "🎁 Rewards",
        "🏆 House Cup",
        "📜 History",
        "🔐 Parent",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.header("🏠 Family Dashboard")

    st.subheader("This Week")

    cols = st.columns(len(KIDS))

    for index, kid in enumerate(KIDS):

        with cols[index]:

            st.markdown(
                f"""
                <div class="hero-card">

                <h3>{kid}</h3>

                <div class="big-number">
                {data['balances'][kid]}
                </div>

                <div class="small-muted">
                total points
                </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                f"⭐ {points_this_week(kid)} this week"
            )

            st.write(
                f"⚖️ {fairness_score(kid)}/100 fair score"
            )

            st.write(
                f"🔥 {current_streak(kid)} day streak"
            )


    st.divider()

    st.subheader("🎯 Weekly Challenge")

    challenge = data["challenge"]

    st.info(
        f"""
        **{challenge['title']}**

        {challenge['description']}

        🏆 Complete it for **+{challenge['bonus']} bonus points**
        """
    )

    for kid in KIDS:

        progress = data["challenge_progress"].get(
            kid,
            0
        )

        target = challenge["target"]

        st.write(
            f"**{kid}: {progress}/{target}**"
        )

        st.progress(
            min(progress / target, 1.0)
        )


    st.divider()

    st.subheader("🏆 Current Leaders")

    scores = {
        kid: fairness_score(kid)
        for kid in KIDS
    }

    leader = max(
        scores,
        key=scores.get
    )

    st.success(
        f"⚖️ Current Fairness Leader: "
        f"**{leader}** — {scores[leader]}/100"
    )


    raw_leader = max(
        KIDS,
        key=lambda k: points_this_week(k)
    )

    st.info(
        f"⭐ Points Leader: "
        f"**{raw_leader}** — "
        f"{points_this_week(raw_leader)} points"
    )


# ============================================================
# PROFILE
# ============================================================

elif page == "👦 My Profile":

    st.header("👦 My Profile")

    kid = st.selectbox(
        "Choose profile",
        KIDS
    )

    st.session_state.selected_kid = kid

    st.subheader(
        f"{kid}'s Dashboard"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Points",
            data["balances"][kid]
        )

    with c2:

        st.metric(
            "Fair Score",
            f"{fairness_score(kid)}/100"
        )


    st.divider()

    st.subheader("📊 Your Week")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "This Week",
            points_this_week(kid)
        )

    with c2:
        st.metric(
            "Per Available Day",
            f"{points_per_available_day(kid):.1f}"
        )

    with c3:
        st.metric(
            "Streak",
            f"{current_streak(kid)} 🔥"
        )


    st.divider()

    st.subheader("📈 Your Improvement")

    improvement = improvement_percentage(kid)

    if improvement > 0:

        st.success(
            f"You're up **{improvement:.0f}%** "
            f"on last week! 🚀"
        )

    elif improvement < 0:

        st.warning(
            f"You're {abs(improvement):.0f}% "
            f"below last week."
        )

    else:

        st.info(
            "No change from last week."
        )


    st.divider()

    st.subheader("🏅 Badges")

    newly = award_badges(kid)

    if newly:

        st.balloons()

        st.success(
            "🎉 New badge unlocked!"
        )

    badges = data["profiles"][kid].get(
        "badges",
        []
    )

    if not badges:

        st.info(
            "No badges yet. Start completing tasks!"
        )

    else:

        badge_cols = st.columns(2)

        for i, badge_id in enumerate(badges):

            badge = next(
                (
                    b for b in BADGES
                    if b["id"] == badge_id
                ),
                None
            )

            if badge:

                with badge_cols[i % 2]:

                    st.success(
                        f"{badge['emoji']} "
                        f"**{badge['name']}**"
                    )

                    st.caption(
                        badge["description"]
                    )


    st.divider()

    st.subheader("🎯 Challenge")

    progress = data["challenge_progress"].get(
        kid,
        0
    )

    target = data["challenge"]["target"]

    st.progress(
        min(progress / target, 1.0)
    )

    st.write(
        f"{progress}/{target} tasks completed"
    )

    if progress >= target:

        st.success(
            "🏆 Challenge complete!"
        )


# ============================================================
# CHORES
# ============================================================

elif page == "✅ Chores":

    st.header("✅ Chores")

    kid = st.selectbox(
        "Who completed the task?",
        KIDS,
        key="chore_kid"
    )

    if not kid_available(kid, TODAY):

        st.warning(
            f"Today isn't normally one of {kid}'s available days."
        )

        st.caption(
            "A parent can still approve the task."
        )


    category = st.selectbox(
        "Category",
        list(TASK_MENU.keys())
    )

    tasks = TASK_MENU[category]

    task = st.selectbox(
        "Task",
        list(tasks.keys())
    )

    points = tasks[task]

    st.markdown(
        f"""
        <div class="hero-card">

        <h3>⭐ {points} points</h3>

        <p>{task}</p>

        </div>
        """,
        unsafe_allow_html=True
    )


    note = ""

    if category == "📚 Personal Growth":

        note = st.text_input(
            "Tell us what you read/learned/practised"
        )


    if st.button(
        "🎉 Complete Task",
        type="primary",
        use_container_width=True
    ):

        requires_approval = (
            category == "📚 Personal Growth"
        )

        if requires_approval:

            data["log"].append(
                {
                    "date": TODAY.isoformat(),
                    "kid": kid,
                    "task": task,
                    "points": points,
                    "note": note,
                    "approved": False,
                }
            )

            save_data(data)

            st.info(
                "⏳ Sent to Parent Mode for approval."
            )

        else:

            new_badges = add_points(
                kid,
                points,
                task,
                note,
                True
            )

            st.balloons()

            st.success(
                f"🎉 {kid} earned {points} points!"
            )

            if new_badges:

                for badge_id in new_badges:

                    badge = next(
                        b for b in BADGES
                        if b["id"] == badge_id
                    )

                    st.success(
                        f"{badge['emoji']} "
                        f"NEW BADGE: "
                        f"{badge['name']}!"
                    )

        st.rerun()


# ============================================================
# REWARDS
# ============================================================

elif page == "🎁 Rewards":

    st.header("🎁 Rewards Shop")

    kid = st.selectbox(
        "Who's spending points?",
        KIDS,
        key="shop_kid"
    )

    balance = data["balances"][kid]

    st.metric(
        f"{kid}'s Balance",
        f"{balance} pts"
    )

    st.divider()

    for index, reward in enumerate(
        data["rewards"]
    ):

        affordable = (
            balance >= reward["points"]
        )

        with st.container(border=True):

            st.subheader(
                f"{reward['emoji']} "
                f"{reward['name']}"
            )

            st.write(
                reward["description"]
            )

            st.write(
                f"⭐ **{reward['points']} points**"
            )

            if affordable:

                if st.button(
                    "🎁 Redeem",
                    key=f"redeem_{index}",
                    use_container_width=True
                ):

                    data["balances"][kid] -= reward["points"]

                    data["redemptions"].append(
                        {
                            "date": TODAY.isoformat(),
                            "kid": kid,
                            "reward": reward["name"],
                            "points_spent": reward["points"],
                        }
                    )

                    save_data(data)

                    st.balloons()

                    st.success(
                        f"🎉 {kid} redeemed "
                        f"{reward['name']}!"
                    )

                    st.rerun()

            else:

                missing = (
                    reward["points"] - balance
                )

                st.caption(
                    f"🔒 {missing} more points needed"
                )


# ============================================================
# HOUSE CUP
# ============================================================

elif page == "🏆 House Cup":

    st.header("🏆 House Cup")

    st.caption(
        "There are several ways to win. "
        "Raw points aren't everything."
    )


    # ========================================================
    # FAIRNESS LEADER
    # ========================================================

    scores = {
        kid: fairness_score(kid)
        for kid in KIDS
    }

    fairness_winner = max(
        scores,
        key=scores.get
    )

    st.subheader("⚖️ Fairness Champion")

    st.success(
        f"🏆 **{fairness_winner}** — "
        f"{scores[fairness_winner]}/100"
    )


    # ========================================================
    # POINTS CHAMPION
    # ========================================================

    raw_scores = {
        kid: points_this_week(kid)
        for kid in KIDS
    }

    points_winner = max(
        raw_scores,
        key=raw_scores.get
    )

    st.subheader("⭐ Points Champion")

    st.info(
        f"⭐ **{points_winner}** — "
        f"{raw_scores[points_winner]} points"
    )


    # ========================================================
    # CONSISTENCY
    # ========================================================

    consistency_scores = {
        kid: points_per_available_day(kid)
        for kid in KIDS
    }

    consistency_winner = max(
        consistency_scores,
        key=consistency_scores.get
    )

    st.subheader("⚖️ Consistency Champion")

    st.success(
        f"⚖️ **{consistency_winner}** — "
        f"{consistency_scores[consistency_winner]:.1f} "
        f"points per available day"
    )


    # ========================================================
    # BIGGEST IMPROVER
    # ========================================================

    improvement_scores = {
        kid: improvement_percentage(kid)
        for kid in KIDS
    }

    improvement_winner = max(
        improvement_scores,
        key=improvement_scores.get
    )

    st.subheader("📈 Biggest Improver")

    if improvement_scores[improvement_winner] > 0:

        st.success(
            f"🚀 **{improvement_winner}** — "
            f"+{improvement_scores[improvement_winner]:.0f}%"
        )

    else:

        st.info(
            "Not enough improvement data yet."
        )


    # ========================================================
    # CHALLENGE
    # ========================================================

    challenge_scores = {
        kid: data["challenge_progress"].get(
            kid,
            0
        )
        for kid in KIDS
    }

    challenge_winner = max(
        challenge_scores,
        key=challenge_scores.get
    )

    st.subheader("🎯 Challenge Champion")

    st.success(
        f"🎯 **{challenge_winner}** — "
        f"{challenge_scores[challenge_winner]}/"
        f"{data['challenge']['target']}"
    )


    # ========================================================
    # HELPER
    # ========================================================

    st.subheader("🤝 Helper of the Week")

    if data["helper_awards"]:

        latest = data["helper_awards"][-1]

        st.success(
            f"🤝 **{latest['kid']}** — "
            f"{latest['reason']}"
        )

    else:

        st.info(
            "No Helper of the Week selected yet."
        )


    # ========================================================
    # SCOREBOARD
    # ========================================================

    st.divider()

    st.subheader("📊 Full Scoreboard")

    for kid in sorted(
        KIDS,
        key=lambda k: scores[k],
        reverse=True
    ):

        st.markdown(
            f"### {kid}"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "Fair Score",
                f"{scores[kid]}/100"
            )

        with c2:

            st.metric(
                "Weekly Points",
                raw_scores[kid]
            )

        st.write(
            f"📅 {available_days_this_week(kid)} "
            f"available days"
        )

        st.write(
            f"⚖️ {consistency_scores[kid]:.1f} "
            f"points/day"
        )

        st.write(
            f"📈 {improvement_scores[kid]:+.0f}% "
            f"vs last week"
        )

        st.write(
            f"🔥 {current_streak(kid)} day streak"
        )

        st.divider()


# ============================================================
# HISTORY
# ============================================================

elif page == "📜 History":

    st.header("📜 History")

    filter_kid = st.selectbox(
        "Show",
        ["Everyone"] + KIDS
    )

    events = []

    for entry in data["log"]:

        if (
            filter_kid != "Everyone"
            and entry["kid"] != filter_kid
        ):
            continue

        events.append(
            {
                "date": entry["date"],
                "kid": entry["kid"],
                "description": entry["task"],
                "points": entry["points"],
                "approved": entry.get(
                    "approved",
                    True
                ),
            }
        )


    for entry in data["redemptions"]:

        if (
            filter_kid != "Everyone"
            and entry["kid"] != filter_kid
        ):
            continue

        events.append(
            {
                "date": entry["date"],
                "kid": entry["kid"],
                "description": (
                    "Redeemed: "
                    + entry.get(
                        "reward",
                        "Device time"
                    )
                ),
                "points": -entry["points_spent"],
                "approved": True,
            }
        )


    events.sort(
        key=lambda x: x["date"],
        reverse=True
    )


    if not events:

        st.info(
            "No activity yet."
        )

    else:

        for event in events[:100]:

            if not event["approved"]:

                st.warning(
                    f"⏳ **{event['date']}** — "
                    f"{event['kid']} — "
                    f"{event['description']} — "
                    f"{event['points']} pts — "
                    f"Awaiting approval"
                )

            elif event["points"] > 0:

                st.success(
                    f"⭐ **{event['date']}** — "
                    f"{event['kid']} — "
                    f"{event['description']} — "
                    f"+{event['points']} pts"
                )

            else:

                st.info(
                    f"🎁 **{event['date']}** — "
                    f"{event['kid']} — "
                    f"{event['description']} — "
                    f"{event['points']} pts"
                )


# ============================================================
# PARENT
# ============================================================

elif page == "🔐 Parent":

    st.header("🔐 Parent Mode")

    if not st.session_state.parent_mode:

        pin = st.text_input(
            "Parent PIN",
            type="password"
        )

        if st.button(
            "🔓 Unlock",
            type="primary",
            use_container_width=True
        ):

            if pin == data["settings"]["parent_pin"]:

                st.session_state.parent_mode = True

                st.rerun()

            else:

                st.error(
                    "Incorrect PIN."
                )


    else:

        st.success(
            "🔓 Parent Mode unlocked"
        )

        if st.button(
            "🔒 Lock Parent Mode"
        ):

            st.session_state.parent_mode = False

            st.rerun()


        st.divider()

        # ====================================================
        # APPROVALS
        # ====================================================

        st.subheader("⏳ Pending Approvals")

        pending = [
            (i, entry)
            for i, entry in enumerate(data["log"])
            if not entry.get("approved", True)
        ]

        if not pending:

            st.info(
                "No tasks waiting for approval."
            )

        for index, entry in pending:

            with st.container(border=True):

                st.write(
                    f"**{entry['kid']}**"
                )

                st.write(
                    entry["task"]
                )

                st.write(
                    f"⭐ {entry['points']} points"
                )

                if entry.get("note"):

                    st.caption(
                        entry["note"]
                    )

                c1, c2 = st.columns(2)

                with c1:

                    if st.button(
                        "✅ Approve",
                        key=f"approve_{index}"
                    ):

                        entry["approved"] = True

                        data["balances"][
                            entry["kid"]
                        ] += entry["points"]

                        data["challenge_progress"][
                            entry["kid"]
                        ] += 1

                        award_badges(
                            entry["kid"]
                        )

                        save_data(data)

                        st.rerun()

                with c2:

                    if st.button(
                        "❌ Reject",
                        key=f"reject_{index}"
                    ):

                        data["log"].pop(index)

                        save_data(data)

                        st.rerun()


        st.divider()

        # ====================================================
        # PARENT BONUS
        # ====================================================

        st.subheader("⭐ Parent Bonus")

        bonus_kid = st.selectbox(
            "Child",
            KIDS,
            key="parent_bonus_kid"
        )

        bonus_points = st.number_input(
            "Points",
            min_value=1,
            max_value=100,
            value=5
        )

        bonus_reason = st.text_input(
            "Reason",
            value="Great helping"
        )

        if st.button(
            "⭐ Award Bonus",
            type="primary"
        ):

            award_bonus(
                bonus_kid,
                int(bonus_points),
                bonus_reason
            )

            st.success(
                f"{bonus_kid} received "
                f"{bonus_points} points."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # HELPER OF WEEK
        # ====================================================

        st.subheader("🤝 Helper of the Week")

        helper_kid = st.selectbox(
            "Winner",
            KIDS,
            key="helper_winner"
        )

        helper_reason = st.text_input(
            "Reason",
            value="Fantastic helping this week"
        )

        if st.button(
            "🏆 Award Helper of the Week"
        ):

            data["helper_awards"].append(
                {
                    "date": TODAY.isoformat(),
                    "kid": helper_kid,
                    "reason": helper_reason,
                }
            )

            award_bonus(
                helper_kid,
                10,
                "Helper of the Week"
            )

            save_data(data)

            st.success(
                f"🏆 {helper_kid} is Helper of the Week!"
            )

            st.rerun()


        st.divider()

        # ====================================================
        # AVAILABILITY
        # ====================================================

        st.subheader("📅 Availability")

        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for kid in KIDS:

            selected = st.multiselect(
                f"{kid}'s normal days",
                options=list(range(7)),
                default=data["availability"].get(
                    kid,
                    []
                ),
                format_func=lambda x: day_names[x],
                key=f"days_{kid}"
            )

            data["availability"][kid] = selected


        if st.button(
            "💾 Save Availability"
        ):

            save_data(data)

            st.success(
                "Availability saved."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # CHALLENGE
        # ====================================================

        st.subheader("🎯 Weekly Challenge")

        challenge_title = st.text_input(
            "Title",
            value=data["challenge"]["title"]
        )

        challenge_description = st.text_input(
            "Description",
            value=data["challenge"]["description"]
        )

        challenge_target = st.number_input(
            "Target",
            min_value=1,
            max_value=20,
            value=int(
                data["challenge"]["target"]
            )
        )

        challenge_bonus = st.number_input(
            "Bonus",
            min_value=1,
            max_value=100,
            value=int(
                data["challenge"]["bonus"]
            )
        )

        if st.button(
            "💾 Save Challenge"
        ):

            data["challenge"] = {
                "title": challenge_title,
                "description": challenge_description,
                "target": int(challenge_target),
                "bonus": int(challenge_bonus),
            }

            save_data(data)

            st.success(
                "Challenge saved."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # ADD REWARD
        # ====================================================

        st.subheader("🎁 Add Reward")

        reward_name = st.text_input(
            "Reward name"
        )

        reward_description = st.text_input(
            "Description"
        )

        reward_points = st.number_input(
            "Cost",
            min_value=1,
            max_value=1000,
            value=20
        )

        reward_emoji = st.text_input(
            "Emoji",
            value="🎁"
        )

        if st.button(
            "➕ Add Reward"
        ):

            if reward_name:

                data["rewards"].append(
                    {
                        "name": reward_name,
                        "points": int(reward_points),
                        "description": reward_description,
                        "emoji": reward_emoji,
                    }
                )

                save_data(data)

                st.success(
                    "Reward added."
                )

                st.rerun()


        st.divider()

        # ====================================================
        # RESET WEEKLY CHALLENGE
        # ====================================================

        st.subheader(
            "🔄 Start New Weekly Challenge"
        )

        if st.button(
            "Reset Challenge Progress"
        ):

            data["challenge_progress"] = {
                kid: 0
                for kid in KIDS
            }

            save_data(data)

            st.success(
                "Challenge progress reset."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # CHANGE PIN
        # ====================================================

        st.subheader("🔑 Change Parent PIN")

        new_pin = st.text_input(
            "New PIN",
            type="password"
        )

        if st.button(
            "Change PIN"
        ):

            if len(new_pin) >= 4:

                data["settings"]["parent_pin"] = new_pin

                save_data(data)

                st.success(
                    "PIN changed."
                )

            else:

                st.error(
                    "PIN must contain at least 4 characters."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏠 House Points • Fair competition • "
    "Different ways to win"
)

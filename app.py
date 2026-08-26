import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
from collections import defaultdict

# ============================================================
# HOUSE POINTS — FAIR HOUSE CUP
# ============================================================

st.set_page_config(
    page_title="House Points",
    page_icon="🏠",
    layout="centered"
)

DATA_FILE = "house_points_data.json"

# ============================================================
# CHILDREN
# ============================================================

KIDS = ["Myron", "Brodie"]

# Days each child is normally available.
# 0 = Monday ... 6 = Sunday
#
# Change these if the arrangements change.
#
# Brodie:
# Wednesday + one weekend day.
#
# We deliberately don't count days he isn't available.
DEFAULT_AVAILABILITY = {
    "Myron": [0, 1, 2, 3, 4, 5, 6],
    "Brodie": [2, 5, 6],
}

# ============================================================
# DEVICE TIME
# ============================================================

DEVICE_TIME_RATE = 10
DEVICE_BLOCK_MINUTES = 30

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


def next_tuesday(from_date):
    days_ahead = (1 - from_date.weekday()) % 7

    if days_ahead == 0:
        return from_date

    return from_date + timedelta(days=days_ahead)


# ============================================================
# TASKS
# ============================================================

TASK_MENU = {
    "Quick jobs": {
        "Water the plants": 1,
        "Empty the dishwasher": 2,
        "Load the dishwasher": 2,
        "Empty a kitchen bin": 1,
        "Set the table": 1,
        "Clear the table": 1,
    },

    "Medium jobs": {
        "Take bins out to the curb": 3,
        "Bring empty bins back in": 2,
        "Hoover a room": 4,
        "Sort and put out cardboard/recycling": 3,
        "Tidy the shoe/coat area": 3,
        "Dust downstairs surfaces": 3,
    },

    "Bigger jobs": {
        "Help with the grass": 6,
        "Wash the car": 6,
        "Change bed sheets": 5,
        "Full bathroom clean": 8,
    },

    "Personal growth": {
        "Finished a book": 10,
        "Learned a new skill/fact": 10,
        "Practised an instrument/hobby": 5,
    },

    "Own room": {
        "Tidied own bedroom": 2,
    },
}


# ============================================================
# REWARDS
# ============================================================

DEFAULT_REWARDS = [
    {
        "name": "30 minutes device time",
        "points": 10,
        "description": "30 minutes Xbox/tablet/device time"
    },
    {
        "name": "1 hour device time",
        "points": 20,
        "description": "One hour of device time"
    },
    {
        "name": "Choose the Friday film",
        "points": 25,
        "description": "You choose the family film"
    },
    {
        "name": "Choose the family activity",
        "points": 40,
        "description": "Choose a family activity"
    },
    {
        "name": "£2 pocket money",
        "points": 50,
        "description": "£2 pocket money"
    },
]


# ============================================================
# WEEKLY AWARDS
# ============================================================

AWARDS = [
    "🏆 Points Champion",
    "⚖️ Consistency Champion",
    "📈 Biggest Effort",
    "🤝 Helper of the Week",
    "🎯 Challenge Champion",
    "📚 Personal Achievement",
]


# ============================================================
# DATA
# ============================================================

def default_data():

    return {
        "balances": {
            kid: 0
            for kid in KIDS
        },

        "log": [],

        "redemptions": [],

        "rewards": DEFAULT_REWARDS,

        "availability": DEFAULT_AVAILABILITY,

        "weekly_challenges": {
            "title": "Weekend Challenge",
            "description": "Complete 3 jobs while you're here",
            "bonus": 10
        },

        "challenge_progress": {
            kid: 0
            for kid in KIDS
        },

        "helper_awards": [],

        "settings": {
            "parent_pin": "1234"
        }
    }


def load_data():

    if os.path.exists(DATA_FILE):

        try:

            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            defaults = default_data()

            for key, value in defaults.items():

                if key not in data:
                    data[key] = value

            return data

        except Exception:

            return default_data()

    return default_data()


def save_data(data):

    with open(DATA_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=2
        )


if "data" not in st.session_state:

    st.session_state.data = load_data()


data = st.session_state.data


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def current_week_start():

    today = date.today()

    return today - timedelta(days=today.weekday())


def week_key(d):

    return d.strftime("%Y-%m-%d")


def parse_date(value):

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except Exception:
        return date.today()


def kid_available(kid, d):

    return d.weekday() in data["availability"].get(
        kid,
        []
    )


def available_days_this_week(kid):

    start = current_week_start()

    count = 0

    for i in range(7):

        d = start + timedelta(days=i)

        if kid_available(kid, d):
            count += 1

    return count


def points_earned_this_week(kid):

    start = current_week_start()

    total = 0

    for entry in data["log"]:

        if entry.get("kid") != kid:
            continue

        d = parse_date(entry.get("date"))

        if d >= start:
            total += int(entry.get("points", 0))

    return total


def tasks_completed_this_week(kid):

    start = current_week_start()

    count = 0

    for entry in data["log"]:

        if entry.get("kid") != kid:
            continue

        d = parse_date(entry.get("date"))

        if d >= start:
            count += 1

    return count


def points_per_available_day(kid):

    days = available_days_this_week(kid)

    if days == 0:
        return 0

    return points_earned_this_week(kid) / days


def previous_week_points(kid):

    start = current_week_start()

    previous_start = start - timedelta(days=7)

    total = 0

    for entry in data["log"]:

        if entry.get("kid") != kid:
            continue

        d = parse_date(entry.get("date"))

        if previous_start <= d < start:
            total += int(entry.get("points", 0))

    return total


def improvement_score(kid):

    current = points_earned_this_week(kid)

    previous = previous_week_points(kid)

    if previous == 0:

        if current > 0:
            return 100

        return 0

    return ((current - previous) / previous) * 100


def streak_for_kid(kid):

    logged_dates = set()

    for entry in data["log"]:

        if entry.get("kid") != kid:
            continue

        logged_dates.add(
            parse_date(entry.get("date"))
        )

    if not logged_dates:
        return 0

    streak = 0

    check = date.today()

    while check in logged_dates:

        streak += 1
        check -= timedelta(days=1)

    return streak


def challenge_progress(kid):

    return int(
        data.get("challenge_progress", {}).get(
            kid,
            0
        )
    )


def challenge_complete(kid):

    return challenge_progress(kid) >= 3


def add_points(kid, points, task, note="", approved=True):

    data["balances"][kid] += points

    data["log"].append(
        {
            "date": date.today().isoformat(),
            "kid": kid,
            "task": task,
            "points": points,
            "note": note,
            "approved": approved,
        }
    )


def award_bonus(kid, points, reason):

    data["balances"][kid] += points

    data["log"].append(
        {
            "date": date.today().isoformat(),
            "kid": kid,
            "task": reason,
            "points": points,
            "note": "Bonus",
            "approved": True,
        }
    )


# ============================================================
# HEADER
# ============================================================

st.title("🏠 House Points")

st.caption(
    "Earn points • Complete challenges • Win awards • Have fun"
)


today = date.today()

upcoming_tuesday = next_tuesday(today)

bin_due = bin_type_for_date(
    upcoming_tuesday
)


# ============================================================
# TOP DASHBOARD
# ============================================================

with st.container(border=True):

    st.subheader("🗑️ Next bin day")

    st.write(
        f"**{upcoming_tuesday.strftime('%A %d %B')}**"
    )

    st.write(
        f"Put out: **{bin_due}**"
    )


# ============================================================
# FAIRNESS EXPLANATION
# ============================================================

with st.expander("⚖️ How the fair competition works"):

    st.write(
        """
        Everyone is compared against the opportunities they actually
        have.

        A child isn't disadvantaged because they weren't at the house.

        The app looks at:

        • Points earned  
        • Available days  
        • Points per available day  
        • Improvement  
        • Challenges  
        • Streaks  
        • Helping others
        """
    )


# ============================================================
# MAIN TABS
# ============================================================

tabs = st.tabs(
    [
        "🏠 Home",
        "✅ Chores",
        "⭐ My Points",
        "🎁 Rewards",
        "🏆 House Cup",
        "📜 History",
        "🔐 Parent Mode",
    ]
)


# ============================================================
# HOME
# ============================================================

with tabs[0]:

    st.header("🏠 House Dashboard")

    cols = st.columns(len(KIDS))

    for i, kid in enumerate(KIDS):

        with cols[i]:

            st.subheader(kid)

            st.metric(
                "Points",
                data["balances"][kid]
            )

            week_points = points_earned_this_week(kid)

            st.write(
                f"**{week_points} pts this week**"
            )

            days = available_days_this_week(kid)

            st.caption(
                f"{days} available days this week"
            )

            streak = streak_for_kid(kid)

            if streak > 0:

                st.write(
                    f"🔥 {streak} day streak"
                )

            progress = challenge_progress(kid)

            st.progress(
                min(progress / 3, 1.0)
            )

            st.caption(
                f"🎯 Weekend challenge: {progress}/3 jobs"
            )


    st.divider()

    st.header("🎯 This week's challenge")

    challenge = data["weekly_challenges"]

    st.info(
        f"""
        **{challenge['title']}**

        {challenge['description']}

        ⭐ **+{challenge['bonus']} bonus points**
        """
    )


    st.divider()

    st.header("📅 Today's opportunities")

    today_tasks = [
        (
            category,
            task,
            points
        )

        for category, tasks in TASK_MENU.items()

        for task, points in tasks.items()
    ]

    for category, task, points in today_tasks[:8]:

        st.write(
            f"**{task}** — ⭐ {points} pts"
        )


# ============================================================
# CHORES
# ============================================================

with tabs[1]:

    st.header("✅ Complete a chore")

    kid = st.selectbox(
        "Who completed it?",
        KIDS,
        key="chore_kid"
    )

    if not kid_available(kid, today):

        st.warning(
            f"{kid} isn't normally scheduled to be here today."
        )

        st.caption(
            "Parent can still approve a task if appropriate."
        )


    category = st.selectbox(
        "Category",
        list(TASK_MENU.keys()),
        key="task_category"
    )

    task = st.selectbox(
        "Task",
        list(TASK_MENU[category].keys()),
        key="task"
    )

    points = TASK_MENU[category][task]

    st.success(
        f"⭐ This task is worth **{points} points**"
    )


    note = ""

    if category == "Personal growth":

        note = st.text_input(
            "What did you read/learn/practise?",
            key="growth_note"
        )


    if st.button(
        "⭐ Complete Task",
        type="primary",
        use_container_width=True
    ):

        # Personal growth tasks require parent approval.
        requires_approval = category == "Personal growth"

        if requires_approval:

            data["log"].append(
                {
                    "date": today.isoformat(),
                    "kid": kid,
                    "task": task,
                    "points": points,
                    "note": note,
                    "approved": False,
                }
            )

            st.info(
                "Task submitted for parent approval."
            )

        else:

            add_points(
                kid,
                points,
                task,
                note,
                True
            )

            data["challenge_progress"][kid] += 1

            st.balloons()

            st.success(
                f"🎉 {kid} earned {points} points!"
            )

        save_data(data)

        st.rerun()


# ============================================================
# MY POINTS
# ============================================================

with tabs[2]:

    st.header("⭐ Points")

    kid = st.selectbox(
        "Choose player",
        KIDS,
        key="points_kid"
    )

    balance = data["balances"][kid]

    st.metric(
        "Current balance",
        f"{balance} pts"
    )

    device_minutes = (
        balance // DEVICE_TIME_RATE
    ) * DEVICE_BLOCK_MINUTES

    st.write(
        f"🎮 That's approximately **{device_minutes} minutes** of device time."
    )


    st.divider()

    weekly = points_earned_this_week(kid)

    days = available_days_this_week(kid)

    per_day = points_per_available_day(kid)

    st.subheader("📊 This week")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Points",
            weekly
        )

    with c2:
        st.metric(
            "Available days",
            days
        )

    with c3:
        st.metric(
            "Points/day",
            f"{per_day:.1f}"
        )


    st.divider()

    st.subheader("🔥 Streak")

    streak = streak_for_kid(kid)

    if streak:

        st.success(
            f"{streak} consecutive day(s)!"
        )

    else:

        st.info(
            "Complete a task today to start a streak."
        )


# ============================================================
# REWARDS
# ============================================================

with tabs[3]:

    st.header("🎁 Rewards Shop")

    kid = st.selectbox(
        "Who's spending?",
        KIDS,
        key="reward_kid"
    )

    balance = data["balances"][kid]

    st.write(
        f"**{kid}'s balance: {balance} points**"
    )

    st.divider()

    for index, reward in enumerate(
        data["rewards"]
    ):

        with st.container(border=True):

            st.subheader(
                f"🎁 {reward['name']}"
            )

            st.write(
                reward["description"]
            )

            st.write(
                f"⭐ **{reward['points']} points**"
            )

            can_afford = (
                balance >= reward["points"]
            )

            if st.button(
                "Redeem",
                key=f"reward_{index}",
                disabled=not can_afford
            ):

                cost = reward["points"]

                data["balances"][kid] -= cost

                data["redemptions"].append(
                    {
                        "date": today.isoformat(),
                        "kid": kid,
                        "reward": reward["name"],
                        "points_spent": cost,
                    }
                )

                save_data(data)

                st.success(
                    f"🎉 {kid} redeemed {reward['name']}!"
                )

                st.rerun()


# ============================================================
# HOUSE CUP
# ============================================================

with tabs[4]:

    st.header("🏆 House Cup")

    st.caption(
        "The winner isn't simply the person with the most points."
    )


    stats = {}

    for kid in KIDS:

        weekly = points_earned_this_week(kid)

        days = available_days_this_week(kid)

        per_day = points_per_available_day(kid)

        improvement = improvement_score(kid)

        tasks = tasks_completed_this_week(kid)

        stats[kid] = {
            "weekly": weekly,
            "days": days,
            "per_day": per_day,
            "improvement": improvement,
            "tasks": tasks,
        }


    # --------------------------------------------------------
    # POINTS CHAMPION
    # --------------------------------------------------------

    st.subheader("🏆 Points Champion")

    winner = max(
        KIDS,
        key=lambda k: stats[k]["weekly"]
    )

    st.success(
        f"🏆 **{winner}** — {stats[winner]['weekly']} points"
    )


    # --------------------------------------------------------
    # CONSISTENCY
    # --------------------------------------------------------

    st.subheader("⚖️ Consistency Champion")

    winner = max(
        KIDS,
        key=lambda k: stats[k]["per_day"]
    )

    st.success(
        f"⚖️ **{winner}** — "
        f"{stats[winner]['per_day']:.1f} points per available day"
    )


    # --------------------------------------------------------
    # BIGGEST IMPROVEMENT
    # --------------------------------------------------------

    st.subheader("📈 Biggest Effort")

    winner = max(
        KIDS,
        key=lambda k: stats[k]["improvement"]
    )

    improvement = stats[winner]["improvement"]

    if improvement > 0:

        st.success(
            f"📈 **{winner}** improved by "
            f"{improvement:.0f}% compared with last week."
        )

    else:

        st.info(
            "Not enough previous-week data yet."
        )


    # --------------------------------------------------------
    # CHALLENGE CHAMPION
    # --------------------------------------------------------

    st.subheader("🎯 Challenge Champion")

    challenge_winner = max(
        KIDS,
        key=lambda k: challenge_progress(k)
    )

    st.success(
        f"🎯 **{challenge_winner}** — "
        f"{challenge_progress(challenge_winner)}/3 jobs"
    )


    # --------------------------------------------------------
    # HELPER OF THE WEEK
    # --------------------------------------------------------

    st.subheader("🤝 Helper of the Week")

    if data["helper_awards"]:

        latest = data["helper_awards"][-1]

        st.success(
            f"🤝 **{latest['kid']}** — "
            f"{latest['reason']}"
        )

    else:

        st.info(
            "Parent hasn't selected Helper of the Week yet."
        )


    st.divider()

    st.subheader("📊 Fair comparison")

    for kid in KIDS:

        st.write(
            f"### {kid}"
        )

        st.write(
            f"⭐ {stats[kid]['weekly']} points"
        )

        st.write(
            f"📅 {stats[kid]['days']} available days"
        )

        st.write(
            f"⚖️ {stats[kid]['per_day']:.1f} points/day"
        )

        st.write(
            f"🔥 {streak_for_kid(kid)} day streak"
        )

        st.divider()


# ============================================================
# HISTORY
# ============================================================

with tabs[5]:

    st.header("📜 Activity History")

    events = []


    for entry in data["log"]:

        status = ""

        if not entry.get("approved", True):

            status = " ⏳ Awaiting approval"

        events.append(
            {
                "date": entry["date"],
                "kid": entry["kid"],
                "description": (
                    f"Earned {entry['points']} pts — "
                    f"{entry['task']}"
                    f"{status}"
                ),
                "points": entry["points"],
            }
        )


    for entry in data["redemptions"]:

        events.append(
            {
                "date": entry["date"],
                "kid": entry["kid"],
                "description": (
                    f"Redeemed — "
                    f"{entry.get('reward', 'Device time')}"
                ),
                "points": -entry["points_spent"],
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

            symbol = (
                "⭐"
                if event["points"] > 0
                else "🎁"
            )

            st.write(
                f"{symbol} **{event['date']}** — "
                f"**{event['kid']}** — "
                f"{event['description']}"
            )


# ============================================================
# PARENT MODE
# ============================================================

with tabs[6]:

    st.header("🔐 Parent Mode")

    if "parent_authenticated" not in st.session_state:

        st.session_state.parent_authenticated = False


    if not st.session_state.parent_authenticated:

        pin = st.text_input(
            "Enter parent PIN",
            type="password"
        )

        if st.button(
            "Unlock Parent Mode",
            type="primary"
        ):

            if pin == data["settings"]["parent_pin"]:

                st.session_state.parent_authenticated = True

                st.success(
                    "Parent Mode unlocked."
                )

                st.rerun()

            else:

                st.error(
                    "Incorrect PIN."
                )


    else:

        st.success(
            "🔓 Parent Mode unlocked"
        )


        if st.button("Lock Parent Mode"):

            st.session_state.parent_authenticated = False

            st.rerun()


        st.divider()

        # ====================================================
        # PENDING APPROVALS
        # ====================================================

        st.subheader("⏳ Pending approvals")

        pending_found = False

        for index, entry in enumerate(data["log"]):

            if entry.get("approved", True):
                continue

            pending_found = True

            with st.container(border=True):

                st.write(
                    f"**{entry['kid']}**"
                )

                st.write(
                    entry["task"]
                )

                if entry.get("note"):

                    st.caption(
                        entry["note"]
                    )

                st.write(
                    f"⭐ {entry['points']} points"
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


        if not pending_found:

            st.info(
                "No pending approvals."
            )


        st.divider()

        # ====================================================
        # MANUAL BONUS
        # ====================================================

        st.subheader("⭐ Award bonus points")

        bonus_kid = st.selectbox(
            "Child",
            KIDS,
            key="bonus_kid"
        )

        bonus_points = st.number_input(
            "Points",
            min_value=1,
            max_value=100,
            value=5,
            key="bonus_points"
        )

        bonus_reason = st.text_input(
            "Reason",
            value="Helping without being asked",
            key="bonus_reason"
        )

        if st.button(
            "Award Bonus",
            type="primary"
        ):

            award_bonus(
                bonus_kid,
                int(bonus_points),
                bonus_reason
            )

            save_data(data)

            st.success(
                f"{bonus_kid} received "
                f"{bonus_points} bonus points!"
            )

            st.rerun()


        st.divider()

        # ====================================================
        # HELPER OF THE WEEK
        # ====================================================

        st.subheader("🤝 Helper of the Week")

        helper_kid = st.selectbox(
            "Choose winner",
            KIDS,
            key="helper_kid"
        )

        helper_reason = st.text_input(
            "Why?",
            value="Great helping this week",
            key="helper_reason"
        )

        if st.button(
            "🏆 Award Helper of the Week"
        ):

            data["helper_awards"].append(
                {
                    "date": today.isoformat(),
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
                f"{helper_kid} is Helper of the Week!"
            )

            st.rerun()


        st.divider()

        # ====================================================
        # CHANGE AVAILABILITY
        # ====================================================

        st.subheader("📅 Availability")

        st.caption(
            "This is what makes the competition fair."
        )

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

            st.write(
                f"**{kid}**"
            )

            current_days = data[
                "availability"
            ].get(kid, [])

            selected = st.multiselect(
                f"{kid}'s available days",
                options=list(range(7)),
                default=current_days,
                format_func=lambda x: day_names[x],
                key=f"availability_{kid}"
            )

            data["availability"][kid] = selected


        if st.button(
            "Save availability"
        ):

            save_data(data)

            st.success(
                "Availability saved."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # CHANGE CHALLENGE
        # ====================================================

        st.subheader("🎯 Weekly Challenge")

        challenge_title = st.text_input(
            "Challenge title",
            value=data["weekly_challenges"]["title"]
        )

        challenge_description = st.text_input(
            "Description",
            value=data["weekly_challenges"]["description"]
        )

        challenge_bonus = st.number_input(
            "Bonus points",
            min_value=1,
            max_value=100,
            value=int(
                data["weekly_challenges"]["bonus"]
            )
        )

        if st.button(
            "Save Challenge"
        ):

            data["weekly_challenges"] = {
                "title": challenge_title,
                "description": challenge_description,
                "bonus": int(challenge_bonus),
            }

            save_data(data)

            st.success(
                "Challenge updated."
            )

            st.rerun()


        st.divider()

        # ====================================================
        # ADD REWARD
        # ====================================================

        st.subheader("🎁 Add Reward")

        reward_name = st.text_input(
            "Reward name",
            key="new_reward_name"
        )

        reward_description = st.text_input(
            "Description",
            key="new_reward_description"
        )

        reward_cost = st.number_input(
            "Cost",
            min_value=1,
            max_value=1000,
            value=20,
            key="new_reward_cost"
        )

        if st.button(
            "Add Reward"
        ):

            if reward_name:

                data["rewards"].append(
                    {
                        "name": reward_name,
                        "points": int(reward_cost),
                        "description": reward_description,
                    }
                )

                save_data(data)

                st.success(
                    "Reward added."
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
                    "Parent PIN changed."
                )

            else:

                st.error(
                    "PIN must be at least 4 characters."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏠 House Points • Fair competition • "
    "Earn it • Achieve it • Enjoy it"
)

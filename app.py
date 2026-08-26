Yes — this is much more than a task list now. Looking at the screenshot, the current app is basically a household task manager. What you're describing is closer to a family game where the chores are the gameplay.
I would make Household Hub 3.0 feel like this:
🏆 Main dashboard
Big House Cup / family leaderboard
Myron and Brodie's current points
Level and XP
Progress towards next reward
Current streak
Badges earned
Today's challenges
"Pick a task" button
"Spend my points" button
Weekly winner
Fair leaderboard that accounts for Brodie being around less
👦 Individual profile
Each child gets their own page:
Avatar
Level
Total points earned
Points available
XP progress bar
Tasks completed
Best streak
Badges
Recent achievements
Favourite tasks
Weekly/monthly progress
Rewards they've unlocked
✅ Task marketplace
Instead of parents simply assigning everything:
WHAT DO YOU WANT TO DO?
Then cards such as:
🧹 Hoover a room — 4 pts
🌱 Help with garden — 6 pts
🚗 Wash the car — 6 pts
🛏️ Change bed sheets — 5 pts
♻️ Sort recycling — 3 pts
The child chooses what they want to do.
🎮 Reward shop
For example:
Reward
Cost
30 mins Xbox
10 pts
1 hour Xbox
20 pts
Choose tonight's dessert
15 pts
Choose family film
20 pts
Stay up 30 mins later
25 pts
£1 pocket money
30 pts
Choose Saturday activity
40 pts
2 hours gaming
40 pts
And the child sees a progress bar toward each reward.
🥇 Gamification
Levels
XP
Streaks
Badges
Weekly challenges
Personal records
"First task of the week"
"10 tasks completed"
"50 points earned"
"7-day streak"
House Cup
Monthly champion
⚖️ Most importantly: Brodie's fairness system
I wouldn't simply compare total points.
The app should understand that Brodie has fewer opportunities to earn points.
So the leaderboard can show:
🥇 Myron — 84 pts
🥈 Brodie — 57 pts
but also:
Fair Score
Myron: 12.0 pts / available day
Brodie: 15.2 pts / available day 🔥
That means Brodie isn't automatically disadvantaged just because he isn't physically in the house every day.
Household Hub 3.0
I'd replace your current script rather than keep bolting features onto it.
Put this into your app.py:
import streamlit as st
import json
import os
import random
from datetime import date, datetime, timedelta
from collections import Counter

# ============================================================
# HOUSEHOLD HUB 3.0
# ============================================================

st.set_page_config(
    page_title="Household Hub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "household_hub_data.json"


# ============================================================
# FAMILY
# ============================================================

FAMILY = {
    "Myron": {
        "emoji": "🦁",
        "colour": "blue",
        "type": "child",
        "available_days": ["Monday", "Tuesday", "Wednesday",
                           "Thursday", "Friday", "Saturday", "Sunday"]
    },

    "Brodie": {
        "emoji": "⚽",
        "colour": "green",
        "type": "child",

        # Brodie has fewer opportunities to earn points.
        # The fairness system uses available days rather than
        # simply comparing total points.
        "available_days": ["Wednesday", "Saturday", "Sunday"]
    },

    "Anthony": {
        "emoji": "👨",
        "colour": "purple",
        "type": "adult",
        "available_days": [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]
    },

    "Ksenia": {
        "emoji": "👩",
        "colour": "pink",
        "type": "adult",
        "available_days": [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]
    }
}

CHILDREN = ["Myron", "Brodie"]


# ============================================================
# TASKS
# ============================================================

TASKS = {

    "⚡ Quick Jobs": {
        "Water the plants": 1,
        "Set the table": 1,
        "Clear the table": 1,
        "Empty a kitchen bin": 1,
        "Load the dishwasher": 2,
        "Empty the dishwasher": 2,
    },

    "🧹 Household": {
        "Hoover a room": 4,
        "Tidy the shoe and coat area": 3,
        "Dust downstairs": 3,
        "Sort recycling": 3,
        "Bring bins back in": 2,
    },

    "🌳 Bigger Jobs": {
        "Help with the grass": 6,
        "Wash the car": 6,
        "Change bed sheets": 5,
        "Full bathroom clean": 8,
    },

    "📚 Personal Growth": {
        "Finish a book": 10,
        "Learn something new": 10,
        "Practise an instrument or hobby": 5,
    },

    "🛏️ Own Room": {
        "Tidy bedroom": 2,
    }
}


# ============================================================
# REWARDS
# ============================================================

REWARDS = {
    "🎮 Gaming": {
        "30 minutes Xbox": 10,
        "1 hour Xbox": 20,
        "2 hours Xbox": 40,
    },

    "🍿 Family": {
        "Choose the family film": 20,
        "Choose tonight's dessert": 15,
        "Choose Saturday activity": 40,
    },

    "⭐ Special": {
        "Stay up 30 minutes later": 25,
        "£1 pocket money": 30,
    }
}


# ============================================================
# BADGES
# ============================================================

BADGES = [
    {
        "id": "first_task",
        "name": "First Steps",
        "emoji": "👣",
        "description": "Complete your first task",
        "requirement": lambda s: s["tasks_completed"] >= 1
    },

    {
        "id": "ten_tasks",
        "name": "Getting Busy",
        "emoji": "💪",
        "description": "Complete 10 tasks",
        "requirement": lambda s: s["tasks_completed"] >= 10
    },

    {
        "id": "fifty_points",
        "name": "Point Collector",
        "emoji": "⭐",
        "description": "Earn 50 points",
        "requirement": lambda s: s["lifetime_points"] >= 50
    },

    {
        "id": "hundred_points",
        "name": "Century Club",
        "emoji": "💯",
        "description": "Earn 100 points",
        "requirement": lambda s: s["lifetime_points"] >= 100
    },

    {
        "id": "streak_three",
        "name": "On Fire",
        "emoji": "🔥",
        "description": "Complete tasks on 3 consecutive days",
        "requirement": lambda s: s["best_streak"] >= 3
    },

    {
        "id": "streak_seven",
        "name": "Super Streak",
        "emoji": "🚀",
        "description": "Complete tasks on 7 consecutive days",
        "requirement": lambda s: s["best_streak"] >= 7
    },

    {
        "id": "ten_rewards",
        "name": "Big Spender",
        "emoji": "🛍️",
        "description": "Redeem 10 rewards",
        "requirement": lambda s: s["rewards_redeemed"] >= 10
    }
]


# ============================================================
# LEVEL SYSTEM
# ============================================================

def level_for_xp(xp):
    return max(1, (xp // 50) + 1)


def xp_for_next_level(xp):
    level = level_for_xp(xp)
    return level * 50


def level_progress(xp):
    level = level_for_xp(xp)
    previous = (level - 1) * 50
    next_level = level * 50

    progress = xp - previous
    required = next_level - previous

    return progress, required


# ============================================================
# DATA
# ============================================================

def default_data():

    return {
        "balances": {
            "Myron": 0,
            "Brodie": 0
        },

        "xp": {
            "Myron": 0,
            "Brodie": 0
        },

        "stats": {
            "Myron": {
                "tasks_completed": 0,
                "lifetime_points": 0,
                "best_streak": 0,
                "current_streak": 0,
                "rewards_redeemed": 0,
                "badges": []
            },

            "Brodie": {
                "tasks_completed": 0,
                "lifetime_points": 0,
                "best_streak": 0,
                "current_streak": 0,
                "rewards_redeemed": 0,
                "badges": []
            }
        },

        "log": [],
        "redemptions": [],

        "settings": {
            "week_start": date.today().isoformat()
        }
    }


def load_data():

    if os.path.exists(DATA_FILE):

        try:

            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            default = default_data()

            # Fill in anything missing from older versions
            for key in default:

                if key not in data:
                    data[key] = default[key]

            for kid in CHILDREN:

                if kid not in data["balances"]:
                    data["balances"][kid] = 0

                if kid not in data["xp"]:
                    data["xp"][kid] = 0

                if kid not in data["stats"]:
                    data["stats"][kid] = default["stats"][kid]

            return data

        except Exception:
            return default_data()

    return default_data()


def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# ============================================================
# HELPERS
# ============================================================

def today_string():
    return date.today().isoformat()


def add_task(kid, task, points):

    data["balances"][kid] += points
    data["xp"][kid] += points

    stats = data["stats"][kid]

    stats["tasks_completed"] += 1
    stats["lifetime_points"] += points

    # Record task
    data["log"].append({
        "date": today_string(),
        "kid": kid,
        "task": task,
        "points": points,
        "timestamp": datetime.now().isoformat()
    })

    update_streak(kid)
    check_badges(kid)

    save_data(data)


def update_streak(kid):

    dates = sorted({
        entry["date"]
        for entry in data["log"]
        if entry["kid"] == kid
    })

    if not dates:
        return

    date_objects = [
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in dates
    ]

    date_objects.sort()

    streak = 1

    for i in range(len(date_objects) - 1, 0, -1):

        difference = (
            date_objects[i] -
            date_objects[i - 1]
        ).days

        if difference == 1:
            streak += 1
        else:
            break

    stats = data["stats"][kid]

    stats["current_streak"] = streak
    stats["best_streak"] = max(
        stats["best_streak"],
        streak
    )


def check_badges(kid):

    stats = data["stats"][kid]

    for badge in BADGES:

        if (
            badge["id"] not in stats["badges"]
            and badge["requirement"](stats)
        ):

            stats["badges"].append(badge["id"])


def get_badge(badge_id):

    for badge in BADGES:

        if badge["id"] == badge_id:
            return badge

    return None


def fair_score(kid):

    """
    Fair score = points per available day.

    This prevents someone who is physically in the house
    fewer days from automatically losing the competition.
    """

    stats = data["stats"][kid]

    points = stats["lifetime_points"]

    available_days = len(
        FAMILY[kid]["available_days"]
    )

    if available_days == 0:
        return 0

    return round(points / available_days, 1)


def weekly_points(kid):

    week_ago = date.today() - timedelta(days=7)

    total = 0

    for entry in data["log"]:

        if entry["kid"] != kid:
            continue

        try:
            d = datetime.strptime(
                entry["date"],
                "%Y-%m-%d"
            ).date()
        except:
            continue

        if d >= week_ago:
            total += entry["points"]

    return total


def child_log(kid):

    return [
        e for e in data["log"]
        if e["kid"] == kid
    ]


def reward_progress(kid, cost):

    balance = data["balances"][kid]

    return min(balance / cost, 1.0)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    color: #888;
    font-size: 1.1rem;
}

.hero-card {
    padding: 25px;
    border-radius: 20px;
    background: linear-gradient(135deg, #1e293b, #111827);
    border: 1px solid #374151;
    margin-bottom: 20px;
}

.profile-card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #374151;
    background: rgba(255,255,255,0.03);
    margin-bottom: 15px;
}

.big-number {
    font-size: 2.2rem;
    font-weight: 800;
}

.reward-card {
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #374151;
    background: rgba(255,255,255,0.025);
    min-height: 160px;
}

.badge-card {
    text-align: center;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid #374151;
    margin-bottom: 10px;
}

.small-muted {
    color: #888;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🏠 Household Hub</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">{date.today().strftime("%A, %d %B %Y")} • Turn chores into a game!</div>',
    unsafe_allow_html=True
)

st.write("")


# ============================================================
# NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "🏆 Dashboard"


pages = [
    "🏆 Dashboard",
    "👦 My Profile",
    "✅ Pick a Task",
    "🎁 Reward Shop",
    "🏅 Achievements",
    "📜 History"
]

selected_page = st.radio(
    "Go to",
    pages,
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

if selected_page == "🏆 Dashboard":

    st.subheader("🏆 Household Dashboard")

    # --------------------------------------------------------
    # CHILD SUMMARY
    # --------------------------------------------------------

    cols = st.columns(2)

    for i, kid in enumerate(CHILDREN):

        with cols[i]:

            stats = data["stats"][kid]
            xp = data["xp"][kid]

            level = level_for_xp(xp)
            progress, required = level_progress(xp)

            st.markdown(
                f"""
                <div class="hero-card">
                    <h2>{FAMILY[kid]['emoji']} {kid}</h2>
                    <div class="big-number">
                        {data['balances'][kid]} ⭐
                    </div>
                    <p>Available points</p>
                    <p>Level {level} • {stats['tasks_completed']} tasks completed</p>
                    <p>🔥 {stats['current_streak']} day streak</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(
                progress / required
                if required else 0
            )

            st.caption(
                f"{progress} / {required} XP towards Level {level + 1}"
            )

    # --------------------------------------------------------
    # FAIR LEADERBOARD
    # --------------------------------------------------------

    st.subheader("⚖️ Fair Leaderboard")

    st.caption(
        "The leaderboard considers how often each person is actually around."
    )

    rankings = sorted(
        CHILDREN,
        key=lambda x: fair_score(x),
        reverse=True
    )

    for position, kid in enumerate(rankings, start=1):

        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }.get(position, "🏅")

        st.write(
            f"{medal} **{kid}** — "
            f"{fair_score(kid)} points per available day "
            f"({weekly_points(kid)} this week)"
        )

    # --------------------------------------------------------
    # TODAY'S CHALLENGE
    # --------------------------------------------------------

    st.divider()

    st.subheader("🎯 Today's Challenge")

    challenges = [
        ("🧹", "Complete a household job", 3),
        ("⭐", "Earn 5 points today", 5),
        ("🔥", "Keep your streak alive", 3),
        ("🏠", "Do something helpful without being asked", 5),
        ("📚", "Spend 20 minutes learning something", 5)
    ]

    challenge = challenges[date.today().toordinal() % len(challenges)]

    st.info(
        f"{challenge[0]} **{challenge[1]}** — "
        f"Bonus: **+{challenge[2]} points**"
    )

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    st.divider()

    st.subheader("🚀 What do you want to do?")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "✅ Pick a Task",
            use_container_width=True
        ):
            st.session_state.page = "✅ Pick a Task"
            st.rerun()

    with c2:
        if st.button(
            "🎁 Spend Points",
            use_container_width=True
        ):
            st.session_state.page = "🎁 Reward Shop"
            st.rerun()

    with c3:
        if st.button(
            "🏅 My Achievements",
            use_container_width=True
        ):
            st.session_state.page = "🏅 Achievements"
            st.rerun()


# ============================================================
# PROFILE
# ============================================================

elif selected_page == "👦 My Profile":

    st.subheader("👦 Choose a profile")

    profile_kid = st.selectbox(
        "Profile",
        CHILDREN
    )

    kid = profile_kid
    stats = data["stats"][kid]
    xp = data["xp"][kid]

    level = level_for_xp(xp)
    progress, required = level_progress(xp)

    st.markdown(
        f"""
        <div class="hero-card">
            <h1>{FAMILY[kid]['emoji']} {kid}</h1>
            <h2>Level {level}</h2>
            <p>{stats['tasks_completed']} tasks completed</p>
            <p>🔥 Best streak: {stats['best_streak']} days</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Stats
    cols = st.columns(4)

    with cols[0]:
        st.metric(
            "⭐ Points",
            data["balances"][kid]
        )

    with cols[1]:
        st.metric(
            "📈 XP",
            xp
        )

    with cols[2]:
        st.metric(
            "✅ Tasks",
            stats["tasks_completed"]
        )

    with cols[3]:
        st.metric(
            "🔥 Best streak",
            stats["best_streak"]
        )

    st.subheader("📈 Level Progress")

    st.progress(
        progress / required
        if required else 0
    )

    st.caption(
        f"{progress} / {required} XP"
    )

    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    st.subheader("🏅 Achievements")

    earned = stats["badges"]

    if earned:

        badge_cols = st.columns(4)

        for i, badge_id in enumerate(earned):

            badge = get_badge(badge_id)

            with badge_cols[i % 4]:

                st.markdown(
                    f"""
                    <div class="badge-card">
                        <div style="font-size:2rem">
                            {badge['emoji']}
                        </div>
                        <strong>{badge['name']}</strong>
                        <br>
                        <small>{badge['description']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.info(
            "No badges yet. Complete your first task to unlock one!"
        )

    # --------------------------------------------------------
    # RECENT ACTIVITY
    # --------------------------------------------------------

    st.subheader("📜 Recent achievements")

    entries = child_log(kid)

    entries = sorted(
        entries,
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

    if not entries:

        st.info("No tasks completed yet.")

    else:

        for entry in entries[:8]:

            st.write(
                f"**{entry['date']}** — "
                f"{entry['task']} "
                f"**+{entry['points']} ⭐**"
            )


# ============================================================
# PICK A TASK
# ============================================================

elif selected_page == "✅ Pick a Task":

    st.subheader("✅ Pick a Task")

    st.markdown(
        "### What would you like to do?"
    )

    kid = st.selectbox(
        "Who's doing the task?",
        CHILDREN,
        key="task_kid"
    )

    st.write("")

    for category, tasks in TASKS.items():

        st.markdown(f"### {category}")

        task_names = list(tasks.keys())

        columns = st.columns(3)

        for i, task in enumerate(task_names):

            points = tasks[task]

            with columns[i % 3]:

                st.markdown(
                    f"""
                    <div class="profile-card">
                        <h3>{task}</h3>
                        <div class="big-number">
                            +{points} ⭐
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    f"Do this → {points} pts",
                    key=f"task_{kid}_{task}",
                    use_container_width=True
                ):

                    add_task(
                        kid,
                        task,
                        points
                    )

                    st.success(
                        f"🎉 {kid} earned {points} points!"
                    )

                    st.rerun()


# ============================================================
# REWARD SHOP
# ============================================================

elif selected_page == "🎁 Reward Shop":

    st.subheader("🎁 Reward Shop")

    kid = st.selectbox(
        "Who's spending points?",
        CHILDREN,
        key="reward_kid"
    )

    balance = data["balances"][kid]

    st.markdown(
        f"""
        <div class="hero-card">
            <h2>{FAMILY[kid]['emoji']} {kid}</h2>
            <div class="big-number">{balance} ⭐</div>
            <p>points available to spend</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    for category, rewards in REWARDS.items():

        st.markdown(f"### {category}")

        reward_cols = st.columns(3)

        for i, (reward, cost) in enumerate(rewards.items()):

            with reward_cols[i % 3]:

                affordable = balance >= cost

                st.markdown(
                    f"""
                    <div class="reward-card">
                        <h3>{reward}</h3>
                        <div class="big-number">
                            {cost} ⭐
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                progress = reward_progress(
                    kid,
                    cost
                )

                st.progress(progress)

                if affordable:

                    if st.button(
                        "🎉 Redeem",
                        key=f"redeem_{kid}_{reward}",
                        use_container_width=True
                    ):

                        data["balances"][kid] -= cost

                        data["redemptions"].append({
                            "date": today_string(),
                            "kid": kid,
                            "reward": reward,
                            "cost": cost,
                            "timestamp": datetime.now().isoformat()
                        })

                        data["stats"][kid]["rewards_redeemed"] += 1

                        save_data(data)

                        st.success(
                            f"🎉 {kid} redeemed: {reward}"
                        )

                        st.rerun()

                else:

                    missing = cost - balance

                    st.caption(
                        f"🔒 {missing} more points needed"
                    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

elif selected_page == "🏅 Achievements":

    st.subheader("🏅 Achievement Hall")

    kid = st.selectbox(
        "Who's achievements?",
        CHILDREN,
        key="achievement_kid"
    )

    stats = data["stats"][kid]

    for badge in BADGES:

        unlocked = badge["id"] in stats["badges"]

        if unlocked:

            st.success(
                f"{badge['emoji']} **{badge['name']}** — "
                f"{badge['description']} ✓"
            )

        else:

            st.write(
                f"🔒 {badge['name']} — "
                f"{badge['description']}"
            )


# ============================================================
# HISTORY
# ============================================================

elif selected_page == "📜 History":

    st.subheader("📜 Activity History")

    filter_kid = st.selectbox(
        "Show",
        ["Everyone"] + CHILDREN,
        key="history_kid"
    )

    events = []

    for entry in data["log"]:

        if (
            filter_kid != "Everyone"
            and entry["kid"] != filter_kid
        ):
            continue

        events.append({
            "date": entry["date"],
            "person": entry["kid"],
            "activity": entry["task"],
            "points": f"+{entry['points']} ⭐"
        })

    for entry in data["redemptions"]:

        if (
            filter_kid != "Everyone"
            and entry["kid"] != filter_kid
        ):
            continue

        events.append({
            "date": entry["date"],
            "person": entry["kid"],
            "activity": f"🎁 {entry['reward']}",
            "points": f"-{entry['cost']} ⭐"
        })

    events.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    if not events:

        st.info("Nothing has happened yet.")

    else:

        for event in events[:100]:

            st.write(
                f"**{event['date']}** • "
                f"{event['person']} • "
                f"{event['activity']} • "
                f"**{event['points']}**"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🏠 Household Hub 3.0 • Earn ⭐ • Level up • Unlock rewards • "
    "Build streaks • Win the House Cup"
)
One important change I'd make after this
I wouldn't stop at this version.
The next step should be making the dashboard genuinely feel like an app for children rather than a Streamlit business dashboard.
For example, when Brodie opens it, I want the screen to effectively say:
⚽ BRODIE'S HOUSE
Level 4
⭐ 67 points
🔥 3 day streak
████████░░ 83% to Level 5
🎯 Today's Missions
🧹 Hoover a room +4
🛏️ Tidy bedroom +2
📚 Read a book +10
[ PICK A MISSION ]
🎁 Next Reward
🎮 1 Hour Xbox — 20 ⭐
████████████░
17 / 20
🏅 Your Badges
👣 💯 🔥 🚀
And then the parent side should have a completely different dashboard where you can see who has done what, approve self-reported activities, change rewards, create special jobs, and see the House Cup.
That would turn this from the basic screen in your screenshot into a proper little family game rather than just another chore tracker.

import streamlit as st
import json
import os
import base64
import requests
from datetime import date, datetime, timedelta

# ============================================================
# HOUSEHOLD HUB 4.0
# ============================================================

st.set_page_config(
    page_title="Household Hub",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Persistent storage
# The app uses GitHub storage when the three secrets below are configured.
# This means points/history survive Streamlit Cloud restarts and redeploys.
DATA_FILE = "household_hub_data.json"
GITHUB_API = "https://api.github.com"


def github_configured():
    return all([
        st.secrets.get("GITHUB_TOKEN", ""),
        st.secrets.get("GITHUB_REPO", ""),
        st.secrets.get("GITHUB_DATA_PATH", DATA_FILE),
    ])


def github_headers():
    return {
        "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_file_url():
    repo = st.secrets["GITHUB_REPO"].strip().strip("/")
    path = st.secrets.get("GITHUB_DATA_PATH", DATA_FILE).lstrip("/")
    return f"{GITHUB_API}/repos/{repo}/contents/{path}"

# ============================================================
# FAMILY
# ============================================================

FAMILY = {
    "Myron": {
        "emoji": "🦁",
        "colour": "blue",
        "available_days": [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]
    },

    "Brodie": {
        "emoji": "⚽",
        "colour": "green",
        "available_days": [
            "Wednesday", "Saturday", "Sunday"
        ]
    }
}

CHILDREN = ["Myron", "Brodie"]


# ============================================================
# TASK MARKETPLACE
# ============================================================

TASKS = {

    "⚡ Quick Missions": {
        "Water the plants": 1,
        "Set the table": 1,
        "Clear the table": 1,
        "Empty a kitchen bin": 1,
        "Load the dishwasher": 2,
        "Empty the dishwasher": 2,
    },

    "🧹 Household Missions": {
        "Hoover a room": 4,
        "Tidy the shoe and coat area": 3,
        "Dust downstairs": 3,
        "Sort recycling": 3,
        "Bring bins back in": 2,
        "Take bins to the curb": 3,
    },

    "🌳 Big Missions": {
        "Help with the grass": 6,
        "Wash the car": 6,
        "Change bed sheets": 5,
        "Full bathroom clean": 8,
    },

    "📚 Level Up Yourself": {
        "Finish a book": 10,
        "Learn something new": 10,
        "Practise an instrument or hobby": 5,
    },

    "🛏️ My Space": {
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
    ("first_task", "First Steps", "👣", "Complete your first mission"),
    ("ten_tasks", "Getting Busy", "💪", "Complete 10 missions"),
    ("fifty_points", "Point Collector", "⭐", "Earn 50 lifetime points"),
    ("hundred_points", "Century Club", "💯", "Earn 100 lifetime points"),
    ("three_streak", "On Fire", "🔥", "Reach a 3 day streak"),
    ("seven_streak", "Super Streak", "🚀", "Reach a 7 day streak"),
    ("five_rewards", "Treat Time", "🎁", "Redeem 5 rewards"),
    ("ten_rewards", "Big Spender", "🛍️", "Redeem 10 rewards"),
]


# ============================================================
# LEVEL SYSTEM
# ============================================================

def level_for_xp(xp):
    return max(1, (xp // 50) + 1)


def level_progress(xp):
    level = level_for_xp(xp)

    previous = (level - 1) * 50
    next_level = level * 50

    progress = xp - previous
    required = next_level - previous

    return progress, required


# ============================================================
# DEFAULT DATA
# ============================================================

def empty_child():

    return {
        "balance": 0,
        "xp": 0,
        "tasks_completed": 0,
        "lifetime_points": 0,
        "current_streak": 0,
        "best_streak": 0,
        "rewards_redeemed": 0,
        "badges": []
    }


def default_data():

    return {
        "children": {
            "Myron": empty_child(),
            "Brodie": empty_child()
        },

        "log": [],

        "redemptions": [],

        "pending": [],

        "custom_tasks": [],

        "custom_rewards": []
    }


# ============================================================
# LOAD / SAVE
# ============================================================

def load_data():
    # Production: load from GitHub so the data is persistent.
    if github_configured():
        try:
            response = requests.get(
                github_file_url(),
                headers=github_headers(),
                timeout=15,
            )

            if response.status_code == 200:
                payload = response.json()
                raw = base64.b64decode(payload["content"]).decode("utf-8")
                data = json.loads(raw)

                default = default_data()
                for key in default:
                    if key not in data:
                        data[key] = default[key]

                if "children" not in data:
                    data["children"] = {}

                for kid in CHILDREN:
                    if kid not in data["children"]:
                        data["children"][kid] = empty_child()
                    child = data["children"][kid]
                    for key, value in empty_child().items():
                        if key not in child:
                            child[key] = value

                return data

            if response.status_code == 404:
                return default_data()

        except Exception as e:
            st.warning(f"Could not load saved family data: {e}")
            return default_data()

    # Local fallback for testing outside Streamlit Cloud.
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        default = default_data()
        for key in default:
            if key not in data:
                data[key] = default[key]

        if "children" not in data:
            data["children"] = {}

        for kid in CHILDREN:
            if kid not in data["children"]:
                data["children"][kid] = empty_child()
            child = data["children"][kid]
            for key, value in empty_child().items():
                if key not in child:
                    child[key] = value

        return data

    except Exception:
        return default_data()


def save_data():
    # Production: commit the latest family data to GitHub.
    if github_configured():
        try:
            url = github_file_url()
            raw = json.dumps(data, indent=2)

            # Get the current file SHA, required by GitHub when updating it.
            response = requests.get(
                url,
                headers=github_headers(),
                timeout=15,
            )

            sha = None
            if response.status_code == 200:
                sha = response.json().get("sha")
            elif response.status_code != 404:
                response.raise_for_status()

            payload = {
                "message": "Update Household Hub family data",
                "content": base64.b64encode(raw.encode("utf-8")).decode("ascii"),
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(
                url,
                headers=github_headers(),
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            return True

        except Exception as e:
            st.error(f"⚠️ Could not save family data: {e}")
            return False

    # Local fallback for testing outside Streamlit Cloud.
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return True



if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# ============================================================
# HELPERS
# ============================================================

def today_string():

    return date.today().isoformat()


def all_tasks():

    result = []

    for category, tasks in TASKS.items():

        for task, points in tasks.items():

            result.append({
                "category": category,
                "task": task,
                "points": points
            })

    for task in data.get("custom_tasks", []):

        result.append({
            "category": "⭐ Special Missions",
            "task": task["name"],
            "points": task["points"]
        })

    return result


def all_rewards():

    result = []

    for category, rewards in REWARDS.items():

        for reward, cost in rewards.items():

            result.append({
                "category": category,
                "reward": reward,
                "cost": cost
            })

    for reward in data.get("custom_rewards", []):

        result.append({
            "category": "⭐ Special Rewards",
            "reward": reward["name"],
            "cost": reward["cost"]
        })

    return result


def update_streak(kid):

    dates = sorted({
        entry["date"]
        for entry in data["log"]
        if entry["kid"] == kid
    })

    if not dates:
        return

    date_objects = sorted(
        datetime.strptime(x, "%Y-%m-%d").date()
        for x in dates
    )

    current = 1

    for i in range(len(date_objects) - 1, 0, -1):

        if (date_objects[i] - date_objects[i - 1]).days == 1:
            current += 1
        else:
            break

    child = data["children"][kid]

    child["current_streak"] = current

    child["best_streak"] = max(
        child["best_streak"],
        current
    )


def check_badges(kid):

    child = data["children"][kid]

    checks = {

        "first_task":
            child["tasks_completed"] >= 1,

        "ten_tasks":
            child["tasks_completed"] >= 10,

        "fifty_points":
            child["lifetime_points"] >= 50,

        "hundred_points":
            child["lifetime_points"] >= 100,

        "three_streak":
            child["best_streak"] >= 3,

        "seven_streak":
            child["best_streak"] >= 7,

        "five_rewards":
            child["rewards_redeemed"] >= 5,

        "ten_rewards":
            child["rewards_redeemed"] >= 10,
    }

    for badge_id, unlocked in checks.items():

        if unlocked and badge_id not in child["badges"]:
            child["badges"].append(badge_id)


def add_points(kid, task, points, approved=True, note=""):

    child = data["children"][kid]

    child["balance"] += points
    child["xp"] += points
    child["tasks_completed"] += 1
    child["lifetime_points"] += points

    data["log"].append({
        "date": today_string(),
        "kid": kid,
        "task": task,
        "points": points,
        "note": note,
        "timestamp": datetime.now().isoformat(),
        "approved": approved
    })

    update_streak(kid)
    check_badges(kid)

    save_data()


def weekly_points(kid):

    cutoff = date.today() - timedelta(days=7)

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

        if d >= cutoff:
            total += entry["points"]

    return total


def fair_score(kid):

    child = data["children"][kid]

    points = child["lifetime_points"]

    available_days = len(
        FAMILY[kid]["available_days"]
    )

    if available_days == 0:
        return 0

    return round(
        points / available_days,
        1
    )


def badge_info(badge_id):

    for badge in BADGES:

        if badge[0] == badge_id:
            return badge

    return None


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.big-title {
    font-size: 3.2rem;
    font-weight: 900;
}

.hero {
    padding: 30px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,.12);
    background: linear-gradient(
        135deg,
        rgba(59,130,246,.18),
        rgba(139,92,246,.18)
    );
    margin-bottom: 20px;
}

.child-card {
    padding: 25px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.04);
    margin-bottom: 15px;
}

.task-card {
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.035);
    min-height: 170px;
}

.reward-card {
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.035);
    min-height: 170px;
}

.badge-card {
    text-align: center;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.04);
}

.points {
    font-size: 2.5rem;
    font-weight: 900;
}

.muted {
    opacity: .65;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="big-title">🏠 Household Hub</div>',
    unsafe_allow_html=True
)

st.caption(
    f"{date.today().strftime('%A, %d %B %Y')} • "
    "Earn ⭐ • Complete missions • Level up • Unlock rewards"
)


# ============================================================
# NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"


pages = [
    "🏠 Home",
    "👦 My Profile",
    "🎯 Missions",
    "🎁 Rewards",
    "🏅 Badges",
    "🏆 House Cup",
    "👨‍👩‍👦 Parent Zone",
    "📜 History"
]


selected_page = st.radio(
    "Navigation",
    pages,
    horizontal=True,
    label_visibility="collapsed"
)


st.divider()


# ============================================================
# HOME
# ============================================================

if selected_page == "🏠 Home":

    st.header("🏠 Welcome to Household Hub")

    st.write(
        "Who is playing today?"
    )

    cols = st.columns(2)

    for i, kid in enumerate(CHILDREN):

        child = data["children"][kid]

        level = level_for_xp(
            child["xp"]
        )

        progress, required = level_progress(
            child["xp"]
        )

        with cols[i]:

            st.markdown(
                f"""
                <div class="child-card">

                <h1>
                {FAMILY[kid]['emoji']} {kid}
                </h1>

                <div class="points">
                ⭐ {child['balance']}
                </div>

                <p>
                Level {level}
                • 🔥 {child['current_streak']} day streak
                </p>

                <p>
                {child['tasks_completed']} missions completed
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(
                min(progress / required, 1)
            )

            st.caption(
                f"{progress}/{required} XP to Level {level + 1}"
            )


    st.divider()

    # ========================================================
    # DAILY MISSION
    # ========================================================

    st.header("🎯 Today's Mission")

    daily_missions = [

        ("🧹", "Complete a household mission", 3),

        ("⭐", "Earn 5 points today", 5),

        ("🔥", "Keep your streak alive", 3),

        ("🤝", "Help someone without being asked", 5),

        ("📚", "Spend 20 minutes learning", 5),

    ]

    mission = daily_missions[
        date.today().toordinal()
        % len(daily_missions)
    ]

    st.success(
        f"{mission[0]} **{mission[1]}**  "
        f"Bonus: **+{mission[2]} ⭐**"
    )


    st.divider()

    st.header("🚀 What do you want to do?")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "🎯 PICK A MISSION",
            use_container_width=True
        ):

            st.session_state.page = "🎯 Missions"
            st.rerun()

    with c2:

        if st.button(
            "🎁 SPEND MY POINTS",
            use_container_width=True
        ):

            st.session_state.page = "🎁 Rewards"
            st.rerun()

    with c3:

        if st.button(
            "🏅 MY BADGES",
            use_container_width=True
        ):

            st.session_state.page = "🏅 Badges"
            st.rerun()


# ============================================================
# PROFILE
# ============================================================

elif selected_page == "👦 My Profile":

    st.header("👦 My Profile")

    kid = st.selectbox(
        "Choose player",
        CHILDREN
    )

    child = data["children"][kid]

    level = level_for_xp(
        child["xp"]
    )

    progress, required = level_progress(
        child["xp"]
    )

    st.markdown(
        f"""
        <div class="hero">

        <h1>
        {FAMILY[kid]['emoji']} {kid}
        </h1>

        <h2>
        Level {level}
        </h2>

        <div class="points">
        ⭐ {child['balance']}
        </div>

        <p>
        🔥 Current streak:
        {child['current_streak']} days
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        progress / required
    )

    st.caption(
        f"{progress} / {required} XP to Level {level + 1}"
    )


    # ========================================================
    # STATS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "⭐ Points",
        child["balance"]
    )

    c2.metric(
        "📈 XP",
        child["xp"]
    )

    c3.metric(
        "🎯 Missions",
        child["tasks_completed"]
    )

    c4.metric(
        "🔥 Best streak",
        child["best_streak"]
    )


    st.divider()

    # ========================================================
    # NEXT REWARD
    # ========================================================

    st.header("🎁 Next Reward")

    affordable_rewards = sorted(
        all_rewards(),
        key=lambda x: x["cost"]
    )

    next_reward = None

    for reward in affordable_rewards:

        if reward["cost"] > child["balance"]:
            next_reward = reward
            break

    if next_reward:

        missing = (
            next_reward["cost"]
            - child["balance"]
        )

        st.info(
            f"🎁 **{next_reward['reward']}** "
            f"costs {next_reward['cost']} ⭐\n\n"
            f"You need **{missing} more ⭐**."
        )

        st.progress(
            min(
                child["balance"]
                / next_reward["cost"],
                1
            )
        )

    else:

        st.success(
            "🎉 You can afford all the current rewards!"
        )


    # ========================================================
    # BADGES
    # ========================================================

    st.header("🏅 Your Badges")

    earned = child["badges"]

    if not earned:

        st.info(
            "Complete your first mission to earn your first badge!"
        )

    else:

        badge_cols = st.columns(4)

        for i, badge_id in enumerate(earned):

            badge = badge_info(badge_id)

            if badge:

                with badge_cols[i % 4]:

                    st.markdown(
                        f"""
                        <div class="badge-card">

                        <div style="font-size:3rem">
                        {badge[2]}
                        </div>

                        <strong>
                        {badge[1]}
                        </strong>

                        <p class="muted">
                        {badge[3]}
                        </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# ============================================================
# MISSIONS
# ============================================================

elif selected_page == "🎯 Missions":

    st.header("🎯 Mission Marketplace")

    st.write(
        "Choose something you want to do and earn ⭐."
    )

    kid = st.selectbox(
        "Who's completing the mission?",
        CHILDREN,
        key="mission_kid"
    )

    child = data["children"][kid]

    st.markdown(
        f"### {FAMILY[kid]['emoji']} {kid} has "
        f"**{child['balance']} ⭐**"
    )


    for category, tasks in TASKS.items():

        st.subheader(category)

        task_names = list(tasks.keys())

        cols = st.columns(3)

        for i, task in enumerate(task_names):

            points = tasks[task]

            with cols[i % 3]:

                st.markdown(
                    f"""
                    <div class="task-card">

                    <h3>
                    {task}
                    </h3>

                    <div class="points">
                    +{points} ⭐
                    </div>

                    <p class="muted">
                    Complete this mission
                    </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "✅ COMPLETE",
                    key=f"mission_{kid}_{task}",
                    use_container_width=True
                ):

                    # Self-reported growth tasks
                    # go to approval.
                    if category == "📚 Level Up Yourself":

                        data["pending"].append({
                            "kid": kid,
                            "task": task,
                            "points": points,
                            "date": today_string(),
                            "timestamp": datetime.now().isoformat()
                        })

                        save_data()

                        st.success(
                            "📨 Sent to Parent Zone for approval!"
                        )

                    else:

                        add_points(
                            kid,
                            task,
                            points
                        )

                        st.success(
                            f"🎉 {kid} earned "
                            f"{points} ⭐!"
                        )

                    st.rerun()


# ============================================================
# REWARDS
# ============================================================

elif selected_page == "🎁 Rewards":

    st.header("🎁 Reward Shop")

    kid = st.selectbox(
        "Who's spending points?",
        CHILDREN,
        key="shop_kid"
    )

    child = data["children"][kid]

    st.markdown(
        f"""
        <div class="hero">

        <h2>
        {FAMILY[kid]['emoji']} {kid}
        </h2>

        <div class="points">
        ⭐ {child['balance']}
        </div>

        <p>
        Points available
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    for category, rewards in REWARDS.items():

        st.subheader(category)

        reward_cols = st.columns(3)

        for i, (reward, cost) in enumerate(
            rewards.items()
        ):

            with reward_cols[i % 3]:

                affordable = (
                    child["balance"] >= cost
                )

                st.markdown(
                    f"""
                    <div class="reward-card">

                    <h3>
                    {reward}
                    </h3>

                    <div class="points">
                    {cost} ⭐
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                progress = min(
                    child["balance"] / cost,
                    1
                )

                st.progress(progress)

                if affordable:

                    if st.button(
                        "🎉 REDEEM",
                        key=f"reward_{kid}_{reward}",
                        use_container_width=True
                    ):

                        child["balance"] -= cost

                        child[
                            "rewards_redeemed"
                        ] += 1

                        data["redemptions"].append({
                            "date": today_string(),
                            "kid": kid,
                            "reward": reward,
                            "cost": cost,
                            "timestamp":
                                datetime.now().isoformat()
                        })

                        check_badges(kid)

                        save_data()

                        st.success(
                            f"🎉 {reward} unlocked!"
                        )

                        st.rerun()

                else:

                    st.caption(
                        f"🔒 {cost - child['balance']} "
                        f"more ⭐ needed"
                    )


# ============================================================
# BADGES
# ============================================================

elif selected_page == "🏅 Badges":

    st.header("🏅 Achievement Hall")

    kid = st.selectbox(
        "Player",
        CHILDREN,
        key="badge_kid"
    )

    child = data["children"][kid]

    for badge in BADGES:

        unlocked = (
            badge[0] in child["badges"]
        )

        if unlocked:

            st.success(
                f"{badge[2]} **{badge[1]}** — "
                f"{badge[3]} ✓"
            )

        else:

            st.write(
                f"🔒 {badge[1]} — "
                f"{badge[3]}"
            )


# ============================================================
# HOUSE CUP
# ============================================================

elif selected_page == "🏆 House Cup":

    st.header("🏆 House Cup")

    st.write(
        "Who is currently leading?"
    )

    rankings = sorted(
        CHILDREN,
        key=lambda kid: fair_score(kid),
        reverse=True
    )

    for position, kid in enumerate(
        rankings,
        start=1
    ):

        child = data["children"][kid]

        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }.get(position, "🏅")

        st.markdown(
            f"""
            ### {medal} {kid}

            ⭐ **{child['lifetime_points']} lifetime points**

            ⚖️ **{fair_score(kid)} points per
            available day**

            📅 **{weekly_points(kid)} points this week**

            🔥 **{child['best_streak']} day best streak**
            """
        )

        st.divider()


    st.info(
        "⚖️ The Fair Score helps make the competition "
        "fair when someone isn't in the house every day."
    )


# ============================================================
# PARENT ZONE
# ============================================================

elif selected_page == "👨‍👩‍👦 Parent Zone":

    st.header("👨‍👩‍👦 Parent Zone")

    st.caption(
        "Manage missions, approve activities and see how everyone is doing."
    )


    # ========================================================
    # FAMILY OVERVIEW
    # ========================================================

    st.subheader("📊 Family Overview")

    cols = st.columns(2)

    for i, kid in enumerate(CHILDREN):

        child = data["children"][kid]

        with cols[i]:

            st.metric(
                f"{FAMILY[kid]['emoji']} {kid}",
                f"{child['balance']} ⭐"
            )

            st.caption(
                f"Level {level_for_xp(child['xp'])} • "
                f"{child['tasks_completed']} missions • "
                f"{weekly_points(kid)} this week"
            )


    st.divider()


    # ========================================================
    # PENDING APPROVALS
    # ========================================================

    st.subheader("✅ Activities Awaiting Approval")

    if not data["pending"]:

        st.success(
            "Nothing waiting for approval."
        )

    else:

        for i, pending in enumerate(
            data["pending"]
        ):

            st.warning(
                f"**{pending['kid']}** says they completed "
                f"**{pending['task']}** for "
                f"**{pending['points']} ⭐**."
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "✅ APPROVE",
                    key=f"approve_{i}",
                    use_container_width=True
                ):

                    add_points(
                        pending["kid"],
                        pending["task"],
                        pending["points"]
                    )

                    data["pending"].pop(i)

                    save_data()

                    st.success(
                        "Approved!"
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "❌ REJECT",
                    key=f"reject_{i}",
                    use_container_width=True
                ):

                    data["pending"].pop(i)

                    save_data()

                    st.info(
                        "Activity rejected."
                    )

                    st.rerun()


    st.divider()


    # ========================================================
    # CREATE SPECIAL MISSION
    # ========================================================

    st.subheader("⭐ Create Special Mission")

    with st.expander(
        "➕ Add a custom mission"
    ):

        new_task = st.text_input(
            "Mission name"
        )

        new_points = st.number_input(
            "Points",
            min_value=1,
            max_value=100,
            value=5
        )

        if st.button(
            "Create Mission"
        ):

            if new_task.strip():

                data["custom_tasks"].append({
                    "name": new_task.strip(),
                    "points": int(new_points)
                })

                save_data()

                st.success(
                    "Mission created!"
                )

                st.rerun()


    # ========================================================
    # CREATE SPECIAL REWARD
    # ========================================================

    st.subheader("🎁 Create Special Reward")

    with st.expander(
        "➕ Add a custom reward"
    ):

        new_reward = st.text_input(
            "Reward name"
        )

        reward_cost = st.number_input(
            "Point cost",
            min_value=1,
            max_value=500,
            value=20
        )

        if st.button(
            "Create Reward"
        ):

            if new_reward.strip():

                data["custom_rewards"].append({
                    "name": new_reward.strip(),
                    "cost": int(reward_cost)
                })

                save_data()

                st.success(
                    "Reward created!"
                )

                st.rerun()


# ============================================================
# HISTORY
# ============================================================

elif selected_page == "📜 History":

    st.header("📜 Activity History")

    filter_person = st.selectbox(
        "Show",
        ["Everyone"] + CHILDREN
    )

    events = []

    for entry in data["log"]:

        if (
            filter_person != "Everyone"
            and entry["kid"] != filter_person
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
            filter_person != "Everyone"
            and entry["kid"] != filter_person
        ):
            continue

        events.append({
            "date": entry["date"],
            "person": entry["kid"],
            "activity":
                f"🎁 {entry['reward']}",
            "points":
                f"-{entry['cost']} ⭐"
        })


    events.sort(
        key=lambda x: x["date"],
        reverse=True
    )


    if not events:

        st.info(
            "Nothing has happened yet."
        )

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
    "🏠 Household Hub 4.0 • "
    "Earn ⭐ • Complete missions • "
    "Level up • Unlock rewards • "
    "Build streaks • Win the House Cup"
)

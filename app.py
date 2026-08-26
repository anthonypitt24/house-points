import streamlit as st
import json
import os
import random
from datetime import date, datetime, timedelta
from collections import defaultdict

# ============================================================
# HOUSE POINTS 3.0
# ============================================================

st.set_page_config(
    page_title="House Points",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = "house_points_data.json"

KIDS = ["Myron", "Brodie"]

DEFAULT_PIN = "1234"

DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# ============================================================
# DEFAULT TASKS
# ============================================================

DEFAULT_TASKS = [
    {
        "name": "Water the plants",
        "points": 1,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Empty the dishwasher",
        "points": 2,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Load the dishwasher",
        "points": 2,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Empty a kitchen bin",
        "points": 1,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Set the table",
        "points": 1,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Clear the table",
        "points": 1,
        "category": "Quick Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Take bins out to the curb",
        "points": 3,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Bring empty bins back in",
        "points": 2,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Hoover a room",
        "points": 4,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Sort and put out recycling",
        "points": 3,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Tidy the shoe/coat area",
        "points": 3,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Dust downstairs surfaces",
        "points": 3,
        "category": "Medium Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Help with the grass",
        "points": 6,
        "category": "Bigger Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Wash the car",
        "points": 6,
        "category": "Bigger Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Change bed sheets",
        "points": 5,
        "category": "Bigger Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Full bathroom clean",
        "points": 8,
        "category": "Bigger Jobs",
        "eligible": KIDS,
        "approval": False,
    },
    {
        "name": "Finished a book",
        "points": 10,
        "category": "Personal Growth",
        "eligible": KIDS,
        "approval": True,
    },
    {
        "name": "Learned a new skill/fact",
        "points": 10,
        "category": "Personal Growth",
        "eligible": KIDS,
        "approval": True,
    },
    {
        "name": "Practised an instrument/hobby",
        "points": 5,
        "category": "Personal Growth",
        "eligible": KIDS,
        "approval": True,
    },
    {
        "name": "Tidied own bedroom",
        "points": 2,
        "category": "Own Room",
        "eligible": KIDS,
        "approval": False,
    },
]

# ============================================================
# DEFAULT REWARDS
# ============================================================

DEFAULT_REWARDS = [
    {
        "name": "30 Minutes Device Time",
        "points": 10,
        "description": "30 minutes Xbox/tablet/device time",
        "emoji": "🎮",
        "approval": False,
    },
    {
        "name": "1 Hour Device Time",
        "points": 20,
        "description": "One hour of device time",
        "emoji": "🎮",
        "approval": False,
    },
    {
        "name": "Choose the Friday Film",
        "points": 25,
        "description": "You choose the family film",
        "emoji": "🎬",
        "approval": False,
    },
    {
        "name": "Choose Family Activity",
        "points": 40,
        "description": "Choose what the family does",
        "emoji": "🏃",
        "approval": True,
    },
    {
        "name": "£2 Pocket Money",
        "points": 50,
        "description": "£2 pocket money",
        "emoji": "💷",
        "approval": True,
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
    {
        "id": "welcome_back",
        "name": "Welcome Back",
        "emoji": "👋",
        "description": "Complete a Welcome Back mission.",
    },
    {
        "id": "perfect_week",
        "name": "Perfect Week",
        "emoji": "🏅",
        "description": "Complete at least one task on every available day in a week.",
    },
]

# ============================================================
# CHALLENGES
# ============================================================

CHALLENGE_POOL = [
    {
        "title": "Weekend Warrior",
        "description": "Complete 3 jobs while you're available.",
        "target": 3,
        "bonus": 15,
    },
    {
        "title": "Helping Hands",
        "description": "Complete 4 household jobs.",
        "target": 4,
        "bonus": 15,
    },
    {
        "title": "Big Job Challenge",
        "description": "Complete 2 bigger jobs.",
        "target": 2,
        "bonus": 20,
    },
    {
        "title": "Quick Fire",
        "description": "Complete 5 smaller household jobs.",
        "target": 5,
        "bonus": 15,
    },
    {
        "title": "Super Helper",
        "description": "Complete 3 jobs without a parent reminder.",
        "target": 3,
        "bonus": 20,
    },
]

DEFAULT_CHALLENGE = CHALLENGE_POOL[0]

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

    if days_ahead == 0:
        return d

    return d + timedelta(days=days_ahead)


# ============================================================
# WEEK FUNCTIONS
# ============================================================

def week_start(d=None):
    if d is None:
        d = date.today()

    return d - timedelta(days=d.weekday())


def week_end(d=None):
    return week_start(d) + timedelta(days=7)


def previous_week_start(d=None):
    return week_start(d) - timedelta(days=7)


def date_from_string(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()
    except Exception:
        return date.today()


# ============================================================
# DEFAULT DATA
# ============================================================

def default_data():

    return {
        "version": 3,

        "transactions": [],

        "redemptions": [],

        "pending_tasks": [],

        "weekly_results": [],

        "current_week": week_start().isoformat(),

        "challenge": DEFAULT_CHALLENGE.copy(),

        "challenge_progress": {
            kid: 0
            for kid in KIDS
        },

        "welcome_back": {
            kid: {
                "last_seen": None,
                "mission_completed": False,
            }
            for kid in KIDS
        },

        "availability": {
            "Myron": [0, 1, 2, 3, 4, 5, 6],
            "Brodie": [2, 5],
        },

        "special_dates": {
            "Myron": [],
            "Brodie": [],
        },

        "profiles": {
            kid: {
                "badges": [],
            }
            for kid in KIDS
        },

        "rewards": DEFAULT_REWARDS.copy(),

        "tasks": DEFAULT_TASKS.copy(),

        "settings": {
            "parent_pin": DEFAULT_PIN,
        },
    }


# ============================================================
# LOAD / MIGRATION
# ============================================================

def load_data():

    if not os.path.exists(DATA_FILE):
        return default_data()

    try:

        with open(DATA_FILE, "r") as f:
            old = json.load(f)

    except Exception:

        return default_data()

    new = default_data()

    # --------------------------------------------------------
    # Existing balances/log structure migration
    # --------------------------------------------------------

    if "balances" in old:

        for kid in KIDS:

            balance = int(
                old.get(
                    "balances",
                    {}
                ).get(
                    kid,
                    0
                )
            )

            if balance > 0:

                new["transactions"].append(
                    {
                        "date": date.today().isoformat(),
                        "kid": kid,
                        "type": "legacy_balance",
                        "description": "Imported previous balance",
                        "points": balance,
                        "approved": True,
                    }
                )

    if "log" in old:

        for entry in old["log"]:

            if "kid" not in entry:
                continue

            new["transactions"].append(
                {
                    "date": entry.get(
                        "date",
                        date.today().isoformat()
                    ),
                    "kid": entry["kid"],
                    "type": "task",
                    "description": entry.get(
                        "task",
                        "Task"
                    ),
                    "points": int(
                        entry.get(
                            "points",
                            0
                        )
                    ),
                    "note": entry.get(
                        "note",
                        ""
                    ),
                    "approved": entry.get(
                        "approved",
                        True
                    ),
                }
            )

    if "redemptions" in old:

        for entry in old["redemptions"]:

            new["redemptions"].append(
                entry
            )

            new["transactions"].append(
                {
                    "date": entry.get(
                        "date",
                        date.today().isoformat()
                    ),
                    "kid": entry.get(
                        "kid",
                        ""
                    ),
                    "type": "redemption",
                    "description": entry.get(
                        "reward",
                        "Reward redemption"
                    ),
                    "points": -int(
                        entry.get(
                            "points_spent",
                            0
                        )
                    ),
                    "approved": True,
                }
            )

    # --------------------------------------------------------
    # Copy newer structures
    # --------------------------------------------------------

    for key in [
        "transactions",
        "redemptions",
        "pending_tasks",
        "weekly_results",
        "current_week",
        "challenge",
        "challenge_progress",
        "welcome_back",
        "availability",
        "special_dates",
        "profiles",
        "rewards",
        "tasks",
        "settings",
    ]:

        if key in old:
            new[key] = old[key]

    # --------------------------------------------------------
    # Safety defaults
    # --------------------------------------------------------

    for kid in KIDS:

        if kid not in new["availability"]:
            new["availability"][kid] = []

        if kid not in new["special_dates"]:
            new["special_dates"][kid] = []

        if kid not in new["profiles"]:
            new["profiles"][kid] = {
                "badges": []
            }

        if kid not in new["challenge_progress"]:
            new["challenge_progress"][kid] = 0

        if kid not in new["welcome_back"]:
            new["welcome_back"][kid] = {
                "last_seen": None,
                "mission_completed": False,
            }

    return new


data = load_data()


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=2
        )


# ============================================================
# TRANSACTION LEDGER
# ============================================================

def balance(kid):

    total = 0

    for transaction in data["transactions"]:

        if transaction.get("kid") != kid:
            continue

        if not transaction.get(
            "approved",
            True
        ):
            continue

        total += int(
            transaction.get(
                "points",
                0
            )
        )

    return total


def add_transaction(
    kid,
    points,
    description,
    transaction_type="task",
    note="",
):

    data["transactions"].append(
        {
            "date": date.today().isoformat(),
            "kid": kid,
            "type": transaction_type,
            "description": description,
            "points": int(points),
            "note": note,
            "approved": True,
        }
    )

    save_data()


# ============================================================
# AVAILABILITY
# ============================================================

def is_available(kid, d):

    if d.weekday() in data["availability"].get(
        kid,
        []
    ):
        return True

    if d.isoformat() in data["special_dates"].get(
        kid,
        []
    ):
        return True

    return False


def available_days(kid, start, end):

    days = 0
    current = start

    while current < end:

        if is_available(
            kid,
            current
        ):
            days += 1

        current += timedelta(days=1)

    return days


def available_days_this_week(kid):

    return available_days(
        kid,
        week_start(),
        week_end()
    )


# ============================================================
# TRANSACTION QUERIES
# ============================================================

def earned_points(
    kid,
    start,
    end
):

    total = 0

    for transaction in data["transactions"]:

        if transaction.get("kid") != kid:
            continue

        if not transaction.get(
            "approved",
            True
        ):
            continue

        if transaction.get("type") not in [
            "task",
            "bonus",
            "challenge_bonus",
            "helper_bonus",
            "welcome_bonus",
            "legacy_balance",
        ]:
            continue

        d = date_from_string(
            transaction.get(
                "date",
                ""
            )
        )

        if start <= d < end:

            points = int(
                transaction.get(
                    "points",
                    0
                )
            )

            if points > 0:
                total += points

    return total


def spent_points(
    kid,
    start,
    end
):

    total = 0

    for transaction in data["transactions"]:

        if transaction.get("kid") != kid:
            continue

        if not transaction.get(
            "approved",
            True
        ):
            continue

        d = date_from_string(
            transaction.get(
                "date",
                ""
            )
        )

        if start <= d < end:

            points = int(
                transaction.get(
                    "points",
                    0
                )
            )

            if points < 0:
                total += abs(points)

    return total


def weekly_points(kid, start=None):

    if start is None:
        start = week_start()

    return earned_points(
        kid,
        start,
        start + timedelta(days=7)
    )


def task_count(
    kid,
    start,
    end
):

    count = 0

    for transaction in data["transactions"]:

        if transaction.get("kid") != kid:
            continue

        if transaction.get("type") != "task":
            continue

        if not transaction.get(
            "approved",
            True
        ):
            continue

        d = date_from_string(
            transaction.get(
                "date",
                ""
            )
        )

        if start <= d < end:
            count += 1

    return count


def task_days(
    kid,
    start,
    end
):

    days = set()

    for transaction in data["transactions"]:

        if transaction.get("kid") != kid:
            continue

        if transaction.get("type") != "task":
            continue

        if not transaction.get(
            "approved",
            True
        ):
            continue

        d = date_from_string(
            transaction.get(
                "date",
                ""
            )
        )

        if start <= d < end:
            days.add(d)

    return days


# ============================================================
# FAIRNESS / COMPETITION
# ============================================================

def points_per_available_day(
    kid,
    start=None
):

    if start is None:
        start = week_start()

    end = start + timedelta(days=7)

    days = available_days(
        kid,
        start,
        end
    )

    if days <= 0:
        return 0

    return weekly_points(
        kid,
        start
    ) / days


def improvement_percent(kid):

    current = weekly_points(
        kid,
        week_start()
    )

    previous = weekly_points(
        kid,
        previous_week_start()
    )

    if previous == 0:

        if current > 0:
            return 100

        return 0

    return (
        (current - previous)
        / previous
    ) * 100


def fair_score(kid):

    # --------------------------------------------------------
    # Component 1: performance per available day
    # 50%
    # --------------------------------------------------------

    daily = {
        child: points_per_available_day(
            child
        )
        for child in KIDS
    }

    best_daily = max(
        daily.values()
    ) if daily else 0

    if best_daily > 0:
        daily_score = (
            daily[kid]
            / best_daily
        ) * 50
    else:
        daily_score = 0

    # --------------------------------------------------------
    # Component 2: consistency / participation
    # 20%
    # --------------------------------------------------------

    available = available_days_this_week(
        kid
    )

    completed_days = len(
        task_days(
            kid,
            week_start(),
            week_end()
        )
    )

    if available > 0:

        consistency = min(
            completed_days / available,
            1
        )

    else:

        consistency = 0

    consistency_score = (
        consistency * 20
    )

    # --------------------------------------------------------
    # Component 3: personal improvement
    # 20%
    # --------------------------------------------------------

    improvement = improvement_percent(
        kid
    )

    improvement_score = min(
        max(improvement, 0),
        100
    ) / 100 * 20

    # --------------------------------------------------------
    # Component 4: challenge completion
    # 10%
    # --------------------------------------------------------

    target = max(
        int(
            data["challenge"].get(
                "target",
                1
            )
        ),
        1
    )

    progress = data["challenge_progress"].get(
        kid,
        0
    )

    challenge_score = min(
        progress / target,
        1
    ) * 10

    total = (
        daily_score
        + consistency_score
        + improvement_score
        + challenge_score
    )

    return round(
        min(total, 100),
        1
    )


# ============================================================
# STREAKS
# ============================================================

def current_streak(kid):

    dates = task_days(
        kid,
        date.today() - timedelta(days=365),
        date.today() + timedelta(days=1)
    )

    if not dates:
        return 0

    streak = 0
    current = date.today()

    # If there is no task today, start checking yesterday.
    if current not in dates:
        current -= timedelta(days=1)

    while current in dates:

        streak += 1
        current -= timedelta(days=1)

    return streak


def longest_streak(kid):

    dates = sorted(
        task_days(
            kid,
            date.today() - timedelta(days=1000),
            date.today() + timedelta(days=1)
        )
    )

    if not dates:
        return 0

    longest = 1
    current = 1

    for i in range(
        1,
        len(dates)
    ):

        if dates[i] == dates[i - 1] + timedelta(days=1):

            current += 1

            longest = max(
                longest,
                current
            )

        else:

            current = 1

    return longest


# ============================================================
# BADGES
# ============================================================

def award_badges(kid):

    profile = data["profiles"][kid]

    badges = profile.setdefault(
        "badges",
        []
    )

    total_tasks = task_count(
        kid,
        date.today() - timedelta(days=1000),
        date.today() + timedelta(days=1)
    )

    total_earned = earned_points(
        kid,
        date.today() - timedelta(days=1000),
        date.today() + timedelta(days=1)
    )

    streak = current_streak(kid)

    completed_challenge = (
        data["challenge_progress"].get(
            kid,
            0
        )
        >= int(
            data["challenge"].get(
                "target",
                1
            )
        )
    )

    helper = any(
        award.get("kid") == kid
        for award in data["weekly_results"]
        if award.get("helper") == kid
    )

    checks = {
        "first_task": total_tasks >= 1,
        "ten_tasks": total_tasks >= 10,
        "fifty_points": total_earned >= 50,
        "hundred_points": total_earned >= 100,
        "three_day_streak": streak >= 3,
        "seven_day_streak": streak >= 7,
        "challenge": completed_challenge,
        "helper": helper,
    }

    new_badges = []

    for badge_id, condition in checks.items():

        if condition and badge_id not in badges:

            badges.append(
                badge_id
            )

            new_badges.append(
                badge_id
            )

    if new_badges:
        save_data()

    return new_badges


# ============================================================
# CHALLENGE
# ============================================================

def generate_challenge():

    challenge = random.choice(
        CHALLENGE_POOL
    ).copy()

    return challenge


# ============================================================
# WEEKLY RESULTS
# ============================================================

def calculate_week_result(start):

    end = start + timedelta(days=7)

    scores = {
        kid: fair_score_for_period(
            kid,
            start
        )
        for kid in KIDS
    }

    points = {
        kid: weekly_points(
            kid,
            start
        )
        for kid in KIDS
    }

    per_day = {
        kid: points_per_available_day(
            kid,
            start
        )
        for kid in KIDS
    }

    improvement = {}

    for kid in KIDS:

        previous = weekly_points(
            kid,
            start - timedelta(days=7)
        )

        current = points[kid]

        if previous == 0:
            improvement[kid] = (
                100 if current > 0 else 0
            )
        else:
            improvement[kid] = (
                (current - previous)
                / previous
            ) * 100

    points_winner = max(
        KIDS,
        key=lambda k: points[k]
    )

    consistency_winner = max(
        KIDS,
        key=lambda k: per_day[k]
    )

    improvement_winner = max(
        KIDS,
        key=lambda k: improvement[k]
    )

    overall_winner = max(
        KIDS,
        key=lambda k: scores[k]
    )

    return {
        "week": start.isoformat(),
        "points": points,
        "fair_scores": scores,
        "points_per_day": per_day,
        "improvement": improvement,
        "points_champion": points_winner,
        "consistency_champion": consistency_winner,
        "improvement_champion": improvement_winner,
        "overall_champion": overall_winner,
        "helper": None,
    }


def fair_score_for_period(
    kid,
    start
):

    end = start + timedelta(days=7)

    available = available_days(
        kid,
        start,
        end
    )

    if available <= 0:
        return 0

    points = weekly_points(
        kid,
        start
    )

    daily_rate = points / available

    # Relative performance
    other_rates = []

    for other in KIDS:

        other_available = available_days(
            other,
            start,
            end
        )

        if other_available > 0:

            other_rates.append(
                weekly_points(
                    other,
                    start
                ) / other_available
            )

    best_rate = max(
        other_rates
    ) if other_rates else 0

    if best_rate > 0:

        performance = (
            daily_rate / best_rate
        ) * 60

    else:

        performance = 0

    completed = len(
        task_days(
            kid,
            start,
            end
        )
    )

    consistency = (
        min(
            completed / available,
            1
        ) * 20
    )

    previous = weekly_points(
        kid,
        start - timedelta(days=7)
    )

    if previous == 0:

        improvement = (
            100 if points > 0 else 0
        )

    else:

        improvement = (
            (points - previous)
            / previous
        ) * 100

    improvement_component = (
        min(
            max(improvement, 0),
            100
        )
        / 100
        * 20
    )

    return round(
        min(
            performance
            + consistency
            + improvement_component,
            100
        ),
        1
    )


def perform_week_rollover():

    current = week_start()

    stored = date_from_string(
        data.get(
            "current_week",
            current.isoformat()
        )
    )

    if stored >= current:
        return False

    # --------------------------------------------------------
    # Archive every missing week.
    # --------------------------------------------------------

    cursor = stored

    while cursor < current:

        if not any(
            r.get("week") == cursor.isoformat()
            for r in data["weekly_results"]
        ):

            result = calculate_week_result(
                cursor
            )

            data["weekly_results"].append(
                result
            )

        cursor += timedelta(days=7)

    # --------------------------------------------------------
    # New week
    # --------------------------------------------------------

    data["current_week"] = current.isoformat()

    data["challenge"] = generate_challenge()

    data["challenge_progress"] = {
        kid: 0
        for kid in KIDS
    }

    for kid in KIDS:

        data["welcome_back"][kid] = {
            "last_seen": data["welcome_back"][kid].get(
                "last_seen"
            ),
            "mission_completed": False,
        }

    save_data()

    return True


# Automatically roll over when the app is opened.
perform_week_rollover()


# ============================================================
# WELCOME BACK
# ============================================================

def last_task_date(kid):

    dates = task_days(
        kid,
        date.today() - timedelta(days=1000),
        date.today() + timedelta(days=1)
    )

    if not dates:
        return None

    return max(dates)


def welcome_back_available(kid):

    if not is_available(
        kid,
        date.today()
    ):
        return False

    last = last_task_date(kid)

    if last is None:
        return True

    return (
        date.today() - last
    ).days >= 5


def complete_welcome_back(kid):

    data["welcome_back"][kid][
        "mission_completed"
    ] = True

    add_transaction(
        kid,
        10,
        "Welcome Back Bonus",
        "welcome_bonus"
    )

    data["welcome_back"][kid][
        "last_seen"
    ] = date.today().isoformat()

    save_data()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 760px;
        padding-top: 1rem;
        padding-bottom: 4rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .hero-number {
        font-size: 42px;
        font-weight: 800;
        line-height: 1;
    }

    .card {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .muted {
        opacity: .65;
    }

    .stButton > button {
        min-height: 48px;
        border-radius: 12px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        border-radius: 14px;
    }

    @media (max-width: 600px) {

        .block-container {
            padding-left: .7rem;
            padding-right: .7rem;
        }

        .hero-number {
            font-size: 34px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "parent_mode" not in st.session_state:
    st.session_state.parent_mode = False


# ============================================================
# HEADER
# ============================================================

st.title("🏠 House Points")

st.caption(
    "Earn • Improve • Compete • Win"
)

today = date.today()

bin_day = next_tuesday(today)

st.info(
    f"🗑️ **Next bin day:** "
    f"{bin_day.strftime('%A %d %B')} — "
    f"**{bin_type_for_date(bin_day)}**"
)


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Menu",
    [
        "🏠 Home",
        "👦 Profiles",
        "✅ Earn",
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

    # --------------------------------------------------------
    # Welcome Back
    # --------------------------------------------------------

    for kid in KIDS:

        if welcome_back_available(kid):

            if not data["welcome_back"][kid].get(
                "mission_completed",
                False
            ):

                st.success(
                    f"👋 **Welcome back, {kid}!** "
                    f"You've got a chance to earn a "
                    f"**10 point Welcome Back bonus**."
                )

                if st.button(
                    f"🎯 Start {kid}'s Welcome Back Mission",
                    key=f"welcome_{kid}",
                    use_container_width=True
                ):

                    complete_welcome_back(
                        kid
                    )

                    st.balloons()

                    st.success(
                        f"🎉 {kid} earned 10 points!"
                    )

                    st.rerun()

    # --------------------------------------------------------
    # Current scores
    # --------------------------------------------------------

    st.subheader("🏆 This Week")

    cols = st.columns(2)

    for i, kid in enumerate(KIDS):

        with cols[i]:

            st.markdown(
                f"""
                <div class="hero">

                <h2>{kid}</h2>

                <div class="hero-number">
                {balance(kid)}
                </div>

                <div class="muted">
                total points
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.write(
                f"⭐ **{weekly_points(kid)}** this week"
            )

            st.write(
                f"⚖️ **{fair_score(kid)}/100** Fair Score"
            )

            st.write(
                f"🔥 **{current_streak(kid)}** day streak"
            )

    # --------------------------------------------------------
    # Challenge
    # --------------------------------------------------------

    st.divider()

    challenge = data["challenge"]

    st.subheader("🎯 This Week's Challenge")

    st.markdown(
        f"""
        <div class="card">

        <h3>{challenge['title']}</h3>

        <p>{challenge['description']}</p>

        <strong>🏆 +{challenge['bonus']} bonus points</strong>

        </div>
        """,
        unsafe_allow_html=True
    )

    for kid in KIDS:

        progress = data["challenge_progress"].get(
            kid,
            0
        )

        target = int(
            challenge["target"]
        )

        st.write(
            f"**{kid} — {progress}/{target}**"
        )

        st.progress(
            min(
                progress / target,
                1
            )
        )

    # --------------------------------------------------------
    # Quick actions
    # --------------------------------------------------------

    st.divider()

    st.subheader("⚡ Quick Actions")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "✅ Log a Job",
            use_container_width=True
        ):

            st.info(
                "Use the **Earn** tab to log a job."
            )

    with c2:

        if st.button(
            "🎁 View Rewards",
            use_container_width=True
        ):

            st.info(
                "Use the **Rewards** tab."
            )


# ============================================================
# PROFILES
# ============================================================

elif page == "👦 Profiles":

    st.header("👦 My Profile")

    kid = st.selectbox(
        "Choose a profile",
        KIDS
    )

    st.subheader(
        f"{kid}'s Stats"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Current Balance",
            f"{balance(kid)} pts"
        )

    with c2:

        st.metric(
            "Fair Score",
            f"{fair_score(kid)}/100"
        )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "This Week",
            weekly_points(kid)
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

    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    st.subheader("📅 Opportunity")

    available = available_days_this_week(
        kid
    )

    completed = len(
        task_days(
            kid,
            week_start(),
            week_end()
        )
    )

    st.write(
        f"You're normally available "
        f"**{available} days** this week."
    )

    st.write(
        f"You've completed tasks on "
        f"**{completed} days**."
    )

    if available:

        st.progress(
            min(
                completed / available,
                1
            )
        )

    # --------------------------------------------------------
    # Improvement
    # --------------------------------------------------------

    st.divider()

    st.subheader("📈 Personal Improvement")

    improvement = improvement_percent(
        kid
    )

    if improvement > 0:

        st.success(
            f"🚀 You're **{improvement:.0f}%** "
            f"ahead of last week."
        )

    elif improvement < 0:

        st.warning(
            f"You're **{abs(improvement):.0f}%** "
            f"below last week."
        )

    else:

        st.info(
            "No change compared with last week."
        )

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    st.subheader("📊 Weekly Points")

    chart_data = []

    for result in data["weekly_results"][-8:]:

        chart_data.append(
            {
                "Week": result["week"],
                "Points": result["points"].get(
                    kid,
                    0
                ),
            }
        )

    current_week_entry = {
        "Week": week_start().isoformat(),
        "Points": weekly_points(kid),
    }

    chart_data.append(
        current_week_entry
    )

    if chart_data:

        import pandas as pd

        df = pd.DataFrame(
            chart_data
        )

        df = df.set_index(
            "Week"
        )

        st.line_chart(
            df
        )

    # --------------------------------------------------------
    # Badges
    # --------------------------------------------------------

    st.divider()

    st.subheader("🏅 Badges")

    badges = data["profiles"][kid].get(
        "badges",
        []
    )

    if not badges:

        st.info(
            "No badges yet. Start earning!"
        )

    else:

        cols = st.columns(2)

        for i, badge_id in enumerate(
            badges
        ):

            badge = next(
                (
                    b
                    for b in BADGES
                    if b["id"] == badge_id
                ),
                None
            )

            if badge:

                with cols[i % 2]:

                    st.success(
                        f"{badge['emoji']} "
                        f"**{badge['name']}**"
                    )

                    st.caption(
                        badge["description"]
                    )

    # --------------------------------------------------------
    # Personal best
    # --------------------------------------------------------

    previous_best = 0

    for result in data["weekly_results"]:

        previous_best = max(
            previous_best,
            int(
                result["points"].get(
                    kid,
                    0
                )
            )
        )

    personal_best = max(
        previous_best,
        weekly_points(kid)
    )

    st.metric(
        "🏅 Personal Best Week",
        f"{personal_best} pts"
    )


# ============================================================
# EARN
# ============================================================

elif page == "✅ Earn":

    st.header("✅ Earn Points")

    # --------------------------------------------------------
    # Available tasks
    # --------------------------------------------------------

    eligible_tasks = []

    for task in data["tasks"]:

        if kid := None:
            pass

    kid = st.selectbox(
        "Who completed it?",
        KIDS,
        key="earn_kid"
    )

    if not is_available(
        kid,
        today
    ):

        st.warning(
            f"Today isn't one of {kid}'s "
            f"normal availability days."
        )

        st.caption(
            "A parent can still approve the task."
        )

    categories = sorted(
        set(
            task["category"]
            for task in data["tasks"]
        )
    )

    category = st.selectbox(
        "Category",
        categories
    )

    tasks = [
        task
        for task in data["tasks"]
        if task["category"] == category
        and kid in task.get(
            "eligible",
            KIDS
        )
    ]

    if not tasks:

        st.info(
            "No tasks available in this category."
        )

    else:

        task_names = [
            task["name"]
            for task in tasks
        ]

        task_name = st.selectbox(
            "Task",
            task_names
        )

        selected = next(
            t
            for t in tasks
            if t["name"] == task_name
        )

        points = int(
            selected["points"]
        )

        st.markdown(
            f"""
            <div class="hero">

            <div class="hero-number">
            ⭐ {points}
            </div>

            <p>{task_name}</p>

            </div>
            """,
            unsafe_allow_html=True
        )

        note = st.text_input(
            "Optional note"
        )

        if selected.get(
            "approval",
            False
        ):

            st.info(
                "This task requires parent approval."
            )

        if st.button(
            "🎉 Complete Task",
            type="primary",
            use_container_width=True
        ):

            if selected.get(
                "approval",
                False
            ):

                data["pending_tasks"].append(
                    {
                        "date": today.isoformat(),
                        "kid": kid,
                        "task": task_name,
                        "points": points,
                        "note": note,
                    }
                )

                save_data()

                st.success(
                    "⏳ Sent to Parent Mode for approval."
                )

            else:

                add_transaction(
                    kid,
                    points,
                    task_name,
                    "task",
                    note
                )

                data["challenge_progress"][kid] += 1

                new_badges = award_badges(
                    kid
                )

                save_data()

                st.balloons()

                st.success(
                    f"🎉 {kid} earned "
                    f"{points} points!"
                )

                for badge_id in new_badges:

                    badge = next(
                        b for b in BADGES
                        if b["id"] == badge_id
                    )

                    st.success(
                        f"{badge['emoji']} "
                        f"NEW BADGE — "
                        f"{badge['name']}!"
                    )

                st.rerun()


# ============================================================
# REWARDS
# ============================================================

elif page == "🎁 Rewards":

    st.header("🎁 Reward Shop")

    kid = st.selectbox(
        "Who's spending points?",
        KIDS,
        key="reward_kid"
    )

    current_balance = balance(
        kid
    )

    st.metric(
        f"{kid}'s Points",
        current_balance
    )

    st.divider()

    for index, reward in enumerate(
        data["rewards"]
    ):

        cost = int(
            reward["points"]
        )

        affordable = (
            current_balance >= cost
        )

        with st.container(
            border=True
        ):

            st.subheader(
                f"{reward['emoji']} "
                f"{reward['name']}"
            )

            st.write(
                reward["description"]
            )

            st.write(
                f"⭐ **{cost} points**"
            )

            if current_balance < cost:

                st.caption(
                    f"🔒 "
                    f"{cost - current_balance} "
                    f"more points needed"
                )

            else:

                if st.button(
                    "🎁 Redeem",
                    key=f"reward_{index}",
                    use_container_width=True
                ):

                    data["transactions"].append(
                        {
                            "date": today.isoformat(),
                            "kid": kid,
                            "type": "redemption",
                            "description": reward["name"],
                            "points": -cost,
                            "approved": True,
                        }
                    )

                    data["redemptions"].append(
                        {
                            "date": today.isoformat(),
                            "kid": kid,
                            "reward": reward["name"],
                            "points_spent": cost,
                        }
                    )

                    save_data()

                    st.balloons()

                    st.success(
                        f"🎉 {reward['name']} redeemed!"
                    )

                    st.rerun()


# ============================================================
# HOUSE CUP
# ============================================================

elif page == "🏆 House Cup":

    st.header("🏆 House Cup")

    st.caption(
        f"Week beginning "
        f"{week_start().strftime('%d %B %Y')}"
    )

    scores = {
        kid: fair_score(kid)
        for kid in KIDS
    }

    overall = max(
        KIDS,
        key=lambda k: scores[k]
    )

    st.markdown(
        f"""
        <div class="hero">

        <h2>🏆 Overall Leader</h2>

        <div class="hero-number">
        {overall}
        </div>

        <p>Fair Score: <strong>{scores[overall]}/100</strong></p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Champions
    # --------------------------------------------------------

    points_winner = max(
        KIDS,
        key=lambda k: weekly_points(k)
    )

    consistency_winner = max(
        KIDS,
        key=lambda k: points_per_available_day(k)
    )

    improvement_winner = max(
        KIDS,
        key=lambda k: improvement_percent(k)
    )

    challenge_winner = max(
        KIDS,
        key=lambda k:
        data["challenge_progress"].get(
            k,
            0
        )
    )

    st.subheader("🏅 This Week's Titles")

    titles = [
        (
            "⭐ Points Champion",
            points_winner,
            f"{weekly_points(points_winner)} points"
        ),
        (
            "⚖️ Consistency Champion",
            consistency_winner,
            f"{points_per_available_day(consistency_winner):.1f} pts/day"
        ),
        (
            "📈 Biggest Improver",
            improvement_winner,
            f"{improvement_percent(improvement_winner):+.0f}%"
        ),
        (
            "🎯 Challenge Leader",
            challenge_winner,
            f"{data['challenge_progress'].get(challenge_winner, 0)}/{data['challenge']['target']}"
        ),
    ]

    for title, winner, value in titles:

        with st.container(
            border=True
        ):

            st.subheader(title)

            st.write(
                f"🏆 **{winner}**"
            )

            st.caption(
                value
            )

    # --------------------------------------------------------
    # Scoreboard
    # --------------------------------------------------------

    st.divider()

    st.subheader("📊 Scoreboard")

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
                "Raw Points",
                weekly_points(kid)
            )

        st.write(
            f"📅 {available_days_this_week(kid)} "
            f"available days"
        )

        st.write(
            f"⚖️ {points_per_available_day(kid):.1f} "
            f"points per available day"
        )

        st.write(
            f"📈 {improvement_percent(kid):+.0f}% "
            f"vs previous week"
        )

        st.divider()

    # --------------------------------------------------------
    # Previous winners
    # --------------------------------------------------------

    st.subheader("📜 Previous House Cups")

    if not data["weekly_results"]:

        st.info(
            "Your first completed week will appear here."
        )

    else:

        for result in reversed(
            data["weekly_results"][-12:]
        ):

            st.markdown(
                f"""
                **Week beginning {result['week']}**

                🏆 Overall: **{result['overall_champion']}**

                ⭐ Points: **{result['points_champion']}**

                ⚖️ Consistency: **{result['consistency_champion']}**

                📈 Improver: **{result['improvement_champion']}**
                """
            )

            st.divider()


# ============================================================
# HISTORY
# ============================================================

elif page == "📜 History":

    st.header("📜 Activity History")

    filter_kid = st.selectbox(
        "Show",
        ["Everyone"] + KIDS
    )

    events = []

    # Transactions

    for transaction in data["transactions"]:

        if (
            filter_kid != "Everyone"
            and transaction["kid"] != filter_kid
        ):
            continue

        events.append(
            transaction
        )

    # Pending tasks

    for pending in data["pending_tasks"]:

        if (
            filter_kid != "Everyone"
            and pending["kid"] != filter_kid
        ):
            continue

        events.append(
            {
                "date": pending["date"],
                "kid": pending["kid"],
                "type": "pending",
                "description": pending["task"],
                "points": pending["points"],
                "approved": False,
            }
        )

    events.sort(
        key=lambda x: x.get(
            "date",
            ""
        ),
        reverse=True
    )

    if not events:

        st.info(
            "No activity yet."
        )

    else:

        for event in events[:150]:

            points = int(
                event.get(
                    "points",
                    0
                )
            )

            if event.get(
                "approved",
                True
            ):

                if points > 0:

                    st.success(
                        f"⭐ **{event['date']}** — "
                        f"{event['kid']} — "
                        f"{event['description']} "
                        f"**+{points}**"
                    )

                elif points < 0:

                    st.info(
                        f"🎁 **{event['date']}** — "
                        f"{event['kid']} — "
                        f"{event['description']} "
                        f"**{points}**"
                    )

            else:

                st.warning(
                    f"⏳ **{event['date']}** — "
                    f"{event['kid']} — "
                    f"{event['description']} "
                    f"awaiting approval"
                )


# ============================================================
# PARENT
# ============================================================

elif page == "🔐 Parent":

    st.header("🔐 Parent Area")

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.parent_mode:

        pin = st.text_input(
            "Parent PIN",
            type="password"
        )

        if st.button(
            "🔓 Unlock Parent Mode",
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

    # --------------------------------------------------------
    # PARENT DASHBOARD
    # --------------------------------------------------------

    else:

        st.success(
            "🔓 Parent Mode unlocked"
        )

        if st.button(
            "🔒 Lock Parent Mode"
        ):

            st.session_state.parent_mode = False

            st.rerun()

        # ====================================================
        # PENDING APPROVALS
        # ====================================================

        st.divider()

        st.subheader("⏳ Pending Tasks")

        if not data["pending_tasks"]:

            st.info(
                "Nothing waiting for approval."
            )

        else:

            for index, pending in enumerate(
                data["pending_tasks"]
            ):

                with st.container(
                    border=True
                ):

                    st.write(
                        f"**{pending['kid']}**"
                    )

                    st.write(
                        pending["task"]
                    )

                    st.write(
                        f"⭐ {pending['points']} points"
                    )

                    if pending.get("note"):

                        st.caption(
                            pending["note"]
                        )

                    c1, c2 = st.columns(2)

                    with c1:

                        if st.button(
                            "✅ Approve",
                            key=f"approve_{index}"
                        ):

                            add_transaction(
                                pending["kid"],
                                pending["points"],
                                pending["task"],
                                "task",
                                pending.get(
                                    "note",
                                    ""
                                )
                            )

                            data["challenge_progress"][
                                pending["kid"]
                            ] += 1

                            data["pending_tasks"].pop(
                                index
                            )

                            award_badges(
                                pending["kid"]
                            )

                            save_data()

                            st.rerun()

                    with c2:

                        if st.button(
                            "❌ Reject",
                            key=f"reject_{index}"
                        ):

                            data["pending_tasks"].pop(
                                index
                            )

                            save_data()

                            st.rerun()

        # ====================================================
        # BONUS
        # ====================================================

        st.divider()

        st.subheader("⭐ Award Bonus")

        bonus_kid = st.selectbox(
            "Child",
            KIDS,
            key="bonus_kid"
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
            "⭐ Award Bonus"
        ):

            add_transaction(
                bonus_kid,
                int(bonus_points),
                bonus_reason,
                "bonus"
            )

            st.success(
                f"{bonus_kid} received "
                f"{bonus_points} points."
            )

            st.rerun()

        # ====================================================
        # DEDUCT
        # ====================================================

        st.subheader("➖ Deduct Points")

        deduct_kid = st.selectbox(
            "Child",
            KIDS,
            key="deduct_kid"
        )

        deduct_points = st.number_input(
            "Points to deduct",
            min_value=1,
            max_value=100,
            value=5,
            key="deduct_points"
        )

        deduct_reason = st.text_input(
            "Reason",
            value="Parent adjustment",
            key="deduct_reason"
        )

        if st.button(
            "➖ Deduct Points"
        ):

            if balance(deduct_kid) >= deduct_points:

                add_transaction(
                    deduct_kid,
                    -int(deduct_points),
                    deduct_reason,
                    "deduction"
                )

                st.success(
                    f"{deduct_points} points deducted."
                )

                st.rerun()

            else:

                st.error(
                    "They don't have enough points."
                )

        # ====================================================
        # HELPER OF WEEK
        # ====================================================

        st.divider()

        st.subheader("🤝 Helper of the Week")

        helper_kid = st.selectbox(
            "Winner",
            KIDS,
            key="helper_kid"
        )

        helper_reason = st.text_input(
            "Reason",
            value="Fantastic helping this week"
        )

        if st.button(
            "🏆 Award Helper of the Week"
        ):

            current_week = week_start().isoformat()

            for result in data["weekly_results"]:

                if result.get(
                    "week"
                ) == current_week:

                    result["helper"] = helper_kid

            add_transaction(
                helper_kid,
                10,
                "Helper of the Week",
                "helper_bonus",
                helper_reason
            )

            save_data()

            st.success(
                f"🏆 {helper_kid} is Helper of the Week!"
            )

            st.rerun()

        # ====================================================
        # AVAILABILITY
        # ====================================================

        st.divider()

        st.subheader("📅 Normal Availability")

        st.caption(
            "This is what makes the House Cup fair. "
            "The app compares performance against "
            "the days each child actually has available."
        )

        for kid in KIDS:

            selected = st.multiselect(
                f"{kid}'s normal days",
                range(7),
                default=data["availability"].get(
                    kid,
                    []
                ),
                format_func=lambda x:
                DAY_NAMES[x],
                key=f"availability_{kid}"
            )

            data["availability"][kid] = selected

        if st.button(
            "💾 Save Availability"
        ):

            save_data()

            st.success(
                "Availability saved."
            )

            st.rerun()

        # ====================================================
        # SPECIAL DATES
        # ====================================================

        st.subheader("🗓️ Extra / Special Dates")

        st.caption(
            "Useful for Brodie's extra weekends, "
            "holidays or changes to the normal schedule."
        )

        special_kid = st.selectbox(
            "Child",
            KIDS,
            key="special_kid"
        )

        special_date = st.date_input(
            "Extra available date",
            value=today + timedelta(days=7)
        )

        if st.button(
            "➕ Add Special Date"
        ):

            value = special_date.isoformat()

            if value not in data["special_dates"][special_kid]:

                data["special_dates"][
                    special_kid
                ].append(
                    value
                )

                save_data()

                st.success(
                    f"{special_date.strftime('%d %B %Y')} "
                    f"added for {special_kid}."
                )

                st.rerun()

        for kid in KIDS:

            dates = data["special_dates"].get(
                kid,
                []
            )

            if dates:

                st.write(
                    f"**{kid} special dates:**"
                )

                for d in sorted(dates):

                    st.write(
                        f"• {d}"
                    )

        # ====================================================
        # CHALLENGE
        # ====================================================

        st.divider()

        st.subheader("🎯 Weekly Challenge")

        st.write(
            f"**{data['challenge']['title']}**"
        )

        st.write(
            data["challenge"]["description"]
        )

        st.write(
            f"Target: "
            f"{data['challenge']['target']} "
            f"tasks"
        )

        st.write(
            f"Bonus: "
            f"{data['challenge']['bonus']} points"
        )

        if st.button(
            "🔄 Generate New Challenge"
        ):

            data["challenge"] = generate_challenge()

            data["challenge_progress"] = {
                kid: 0
                for kid in KIDS
            }

            save_data()

            st.success(
                "New challenge generated!"
            )

            st.rerun()

        # ====================================================
        # CUSTOM TASKS
        # ====================================================

        st.divider()

        st.subheader("🧹 Add Custom Task")

        custom_name = st.text_input(
            "Task name"
        )

        custom_points = st.number_input(
            "Points",
            min_value=1,
            max_value=50,
            value=3
        )

        custom_category = st.selectbox(
            "Category",
            [
                "Quick Jobs",
                "Medium Jobs",
                "Bigger Jobs",
                "Personal Growth",
                "Own Room",
                "Custom",
            ]
        )

        custom_kids = st.multiselect(
            "Who can do it?",
            KIDS,
            default=KIDS
        )

        custom_approval = st.checkbox(
            "Requires parent approval"
        )

        if st.button(
            "➕ Add Task"
        ):

            if custom_name and custom_kids:

                data["tasks"].append(
                    {
                        "name": custom_name,
                        "points": int(custom_points),
                        "category": custom_category,
                        "eligible": custom_kids,
                        "approval": custom_approval,
                    }
                )

                save_data()

                st.success(
                    "Custom task added."
                )

                st.rerun()

            else:

                st.error(
                    "Enter a name and choose at least one child."
                )

        # ====================================================
        # REWARDS
        # ====================================================

        st.divider()

        st.subheader("🎁 Add Reward")

        reward_name = st.text_input(
            "Reward name"
        )

        reward_description = st.text_input(
            "Reward description"
        )

        reward_cost = st.number_input(
            "Point cost",
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
                        "points": int(reward_cost),
                        "description": reward_description,
                        "emoji": reward_emoji,
                        "approval": False,
                    }
                )

                save_data()

                st.success(
                    "Reward added."
                )

                st.rerun()

        # ====================================================
        # REWARD MANAGEMENT
        # ====================================================

        st.subheader("🛠️ Manage Rewards")

        for index, reward in enumerate(
            data["rewards"]
        ):

            c1, c2 = st.columns(
                [4, 1]
            )

            with c1:

                st.write(
                    f"{reward['emoji']} "
                    f"**{reward['name']}** — "
                    f"{reward['points']} pts"
                )

            with c2:

                if st.button(
                    "🗑️",
                    key=f"delete_reward_{index}"
                ):

                    data["rewards"].pop(
                        index
                    )

                    save_data()

                    st.rerun()

        # ====================================================
        # RESET CHALLENGE
        # ====================================================

        st.divider()

        st.subheader(
            "🔄 Reset Challenge Progress"
        )

        if st.button(
            "Reset This Week's Challenge"
        ):

            data["challenge_progress"] = {
                kid: 0
                for kid in KIDS
            }

            save_data()

            st.success(
                "Challenge progress reset."
            )

            st.rerun()

        # ====================================================
        # PIN
        # ====================================================

        st.divider()

        st.subheader("🔑 Change Parent PIN")

        new_pin = st.text_input(
            "New PIN",
            type="password"
        )

        if st.button(
            "Change PIN"
        ):

            if len(new_pin) >= 4:

                data["settings"][
                    "parent_pin"
                ] = new_pin

                save_data()

                st.success(
                    "PIN changed."
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
    "🏠 House Points 3.0 • "
    "Fair competition • "
    "Different ways to win"
)

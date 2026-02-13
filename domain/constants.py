"""
domain/constants.py - Single source of truth for all thresholds, labels, and messages.

Extracted from: collect_health.py, collect_status.py, collect_nurture.py, collect_skills.py, app.js
"""

# ============================================================================
# Health thresholds — list of (upper_bound_exclusive, state)
# value < threshold → that state. Last entry has None = catch-all.
# ============================================================================

CPU_THRESHOLDS = [
    (20, "idle"),
    (50, "clear"),
    (70, "busy"),
    (85, "heavy"),
    (None, "critical"),
]

MEMORY_THRESHOLDS = [
    (50, "spacious"),
    (60, "comfortable"),
    (80, "normal"),
    (95, "tight"),
    (None, "critical"),
]

DISK_THRESHOLDS = [
    (50, "spacious"),
    (80, "normal"),
    (95, "tight"),
    (None, "critical"),
]

TEMPERATURE_THRESHOLDS = [
    (40, "cool"),
    (55, "comfortable"),
    (70, "warm"),
    (80, "hot"),
    (None, "critical"),
]

UPTIME_THRESHOLDS_DAYS = [
    (1, "fresh"),
    (3, "normal"),
    (7, "tired"),
    (None, "exhausted"),
]

# ============================================================================
# Health state labels and messages — keyed by (metric, state)
# ============================================================================

CPU_LABELS = {
    "idle":     {"label": "のんびり",     "message": None},
    "clear":    {"label": "クリア",       "message": "いい感じ"},
    "busy":     {"label": "がんばり中",   "message": "ちょっと忙しい"},
    "heavy":    {"label": "重い...",       "message": "けっこうキツい..."},
    "critical": {"label": "限界",         "message": "頭パンクしそう..."},
}

MEMORY_LABELS = {
    "spacious":    {"label": "余裕",       "message": None},
    "comfortable": {"label": "スッキリ",   "message": "余裕あり"},
    "normal":      {"label": "普通",       "message": None},
    "tight":       {"label": "キツい",     "message": "メモリ食いすぎ..."},
    "critical":    {"label": "限界",       "message": "もう無理..."},
}

DISK_LABELS = {
    "spacious": {"label": "広々",         "message": None},
    "normal":   {"label": "普通",         "message": None},
    "tight":    {"label": "狭い...",       "message": "片付けたい..."},
    "critical": {"label": "限界",         "message": "空き容量ヤバい..."},
}

TEMPERATURE_LABELS = {
    "cool":        {"label": "涼しい",     "message": None},
    "comfortable": {"label": "快適",       "message": None},
    "warm":        {"label": "あったかい", "message": "ちょっと熱い？"},
    "hot":         {"label": "暑い...",     "message": "ファン回ってる..."},
    "critical":    {"label": "限界",       "message": "溶ける..."},
}

UPTIME_LABELS = {
    "fresh":     {"label": "スッキリ",   "message": None},
    "normal":    {"label": "普通",       "message": None},
    "tired":     {"label": "疲れ気味",   "message": "そろそろ休みたいな..."},
    "exhausted": {"label": "ヘトヘト",   "message": "......再起動して......"},
}

# ============================================================================
# Overall score table — (min_score, state, emoji, label, message)
# Checked in descending order: first match where score >= min_score wins.
# ============================================================================

OVERALL_SCORE_TABLE = [
    (80, "great",    "\U0001f7e2", "元気！",           "調子いい！今日はイケる"),
    (60, "good",     "\U0001f7e1", "まぁまぁ",         "まぁまぁかな"),
    (40, "poor",     "\U0001f7e0", "ちょっとダルい",   "ちょっとダルい......"),
    (20, "bad",      "\U0001f534", "かなりキツい",     "......しんどい"),
    (0,  "critical", "\U0001f480", "限界",             "........."),
]

# ============================================================================
# Penalty parameters for overall score calculation
# ============================================================================

PENALTY_CPU_OFFSET = 20
PENALTY_CPU_WEIGHT = 1.0

PENALTY_MEMORY_OFFSET = 60
PENALTY_MEMORY_WEIGHT = 1.5

PENALTY_DISK_OFFSET = 70
PENALTY_DISK_WEIGHT = 1.0

PENALTY_TEMP_OFFSET = 50
PENALTY_TEMP_WEIGHT = 1.0

PENALTY_UPTIME_PER_DAY = 2
PENALTY_UPTIME_MAX = 20

# ============================================================================
# Alert level determination
# ============================================================================

ALERT_CRITICAL_STATES = {"critical"}
ALERT_HEAVY_STATES = {"heavy", "tight", "hot", "exhausted"}

# Alert messages — level (1-3) -> list of messages (random.choice)
ALERT_MESSAGES = {
    1: ["ちょっと重いかも...", "なんか調子悪い...", "うーん、微妙..."],
    2: ["再起動したいんだけど、今大丈夫？", "ちょっと助けてほしいかも", "メモリがキツい......"],
    3: ["助けて。マジでやばい。", ".........たすけ......", "限界。もう無理。"],
}

# ============================================================================
# Presence / Status thresholds (seconds)
# ============================================================================

HEARTBEAT_THRESHOLD_SEC = 300       # 5 minutes
ONLINE_THRESHOLD_SEC = 1800         # 30 minutes
AWAY_THRESHOLD_SEC = 7200           # 2 hours
SLEEPING_THRESHOLD_SEC = 3600       # 1 hour

# Status labels — keyed by status name
STATUS_LABELS = {
    "online":   {"label": "ここにいるよ",     "emoji": "\U0001f7e2"},
    "away":     {"label": "ちょっと離れてる", "emoji": "\U0001f7e1"},
    "sleeping": {"label": "寝てる......",     "emoji": "\U0001f4a4"},
    "offline":  {"label": "いない......",     "emoji": "\u26ab"},
}

# ============================================================================
# Time periods — (start_hour, end_hour, period_name)
# Evaluated in order; first match wins. 24h coverage required.
# ============================================================================

TIME_PERIODS = [
    (0,  2,  "late_night"),
    (2,  6,  "deep_night"),
    (6,  9,  "morning"),
    (9,  12, "active"),
    (12, 18, "afternoon"),
    (18, 21, "evening"),
    (21, 24, "night"),
]

# Time context messages — period -> list of messages (random.choice)
TIME_MESSAGES = {
    "morning":    ["ん......おはよ", "おはよ。......ねむい", "朝か。コーヒー淹れよ"],
    "active":     ["よし、やるか", "今日は何する？", "集中モード"],
    "afternoon":  [None, None, "ん？", "通常運転", "やってるやってる"],
    "evening":    ["今日も終わりか", "疲れた......", "あとちょっと"],
    "night":      ["そろそろ夜か", "今日も一日", "夜の作業が一番捗る"],
    "late_night": ["まだ起きてるの？", "......あんたもか", "夜更かし仲間じゃん"],
    "deep_night": ["寝ろよ......", "......", "あたしは寝ないけど、あんたは寝ろ"],
}

# ============================================================================
# Staleness thresholds (minutes)
# ============================================================================

STALENESS_FRESH_MAX_MIN = 10
STALENESS_STALE_MAX_MIN = 30

# ============================================================================
# Nurture — first day (project start)
# ============================================================================

from datetime import datetime, timezone, timedelta

_JST = timezone(timedelta(hours=9))

NURTURE_FIRST_DAY = datetime(2026, 1, 1, 0, 0, 0, tzinfo=_JST)

# ============================================================================
# Nurture — Energy thresholds and labels
# ============================================================================

ENERGY_THRESHOLDS = [
    (70, "energetic"),
    (40, "normal"),
    (20, "tired"),
    (None, "exhausted"),
]

ENERGY_LABELS = {
    "energetic": {"label": "元気", "message": "エネルギー十分！"},
    "normal":    {"label": "ふつう", "message": None},
    "tired":     {"label": "疲れ気味", "message": "ちょっと疲れた..."},
    "exhausted": {"label": "ヘトヘト", "message": "......充電したい"},
}

# ============================================================================
# Nurture — Mood thresholds and labels
# ============================================================================

MOOD_THRESHOLDS = [
    (80, "great"),
    (60, "good"),
    (40, "normal"),
    (20, "down"),
    (None, "bad"),
]

MOOD_LABELS = {
    "great":  {"label": "絶好調", "message": "今日は調子いい！"},
    "good":   {"label": "いい感じ", "message": "まぁまぁかな"},
    "normal": {"label": "ふつう", "message": "ふつう"},
    "down":   {"label": "だるい", "message": "ちょっとだるい......"},
    "bad":    {"label": "最悪", "message": "......"},
}

# ============================================================================
# Nurture — Mood calculation weights
# ============================================================================

MOOD_WEIGHTS = {
    "health": 0.4,
    "energy": 0.2,
    "visits": 0.2,
    "time": 0.2,
}

# ============================================================================
# Nurture — Energy time-of-day modifiers
# ============================================================================

ENERGY_TIME_WEIGHTS = {
    "deep_night": -20,
    "late_night": -10,
    "morning": -5,
    "active": 0,
    "afternoon": 0,
    "evening": -5,
    "night": -10,
}

# ============================================================================
# Nurture — Energy uptime penalty parameters
# ============================================================================

ENERGY_BASE = 80
ENERGY_UPTIME_THRESHOLD_HOURS = 8
ENERGY_UPTIME_PENALTY_PER_HOUR = 3
ENERGY_UPTIME_PENALTY_MAX = 40

# ============================================================================
# Nurture — Mood visit factors
# ============================================================================

MOOD_VISIT_NEUTRAL = 10
MOOD_VISIT_TODAY = 16
MOOD_VISIT_STREAK_LONG = 20    # streak >= 7
MOOD_VISIT_STREAK_MID = 14     # streak >= 3

# ============================================================================
# Nurture — Mood time factors
# ============================================================================

MOOD_TIME_FACTORS = {
    "deep_night": 4,
    "late_night": 6,
    "morning": 8,
    "active": 16,
    "afternoon": 14,
    "evening": 12,
    "night": 10,
}

# ============================================================================
# Nurture — Trust calculation parameters
# ============================================================================

TRUST_BASE = 10
TRUST_LOG_COEFFICIENT = 25
TRUST_MAX_FROM_VISITS = 70
TRUST_STREAK_BONUS_PER_DAY = 2
TRUST_STREAK_BONUS_MAX = 15

# ============================================================================
# Nurture — Intimacy calculation parameters
# ============================================================================

INTIMACY_BASE = 5
INTIMACY_LOG_COEFFICIENT = 23
INTIMACY_MAX_FROM_HOURS = 75
INTIMACY_TODAY_DIVISOR = 6      # today_minutes / 6 = bonus
INTIMACY_TODAY_BONUS_MAX = 10

# ============================================================================
# Nurture — EXP sources
# ============================================================================

EXP_SOURCES = {
    "visit": 10,
    "time_per_5min": 2,
    "streak_bonus": 5,
    "health_bonus": 2,
    "skill_bonus": 50,
}

HEALTH_EXP_THRESHOLD = 50      # health above this earns bonus EXP
STREAK_EXP_CAP = 10            # max streak multiplier

# ============================================================================
# Nurture — EXP extrapolation for levels beyond table
# ============================================================================

EXP_EXTRAPOLATION_STEP = 2500

# ============================================================================
# Nurture — EXP table
# ============================================================================

EXP_TABLE = [
    0,      # Lv.1  (start)
    100,    # Lv.2
    250,    # Lv.3
    450,    # Lv.4
    700,    # Lv.5
    1000,   # Lv.6
    1350,   # Lv.7
    1750,   # Lv.8
    2200,   # Lv.9
    2700,   # Lv.10
    3300,   # Lv.11
    4000,   # Lv.12
    4800,   # Lv.13
    5700,   # Lv.14
    6800,   # Lv.15
    8000,   # Lv.16
    9500,   # Lv.17
    11200,  # Lv.18
    13200,  # Lv.19
    15500,  # Lv.20
]

# ============================================================================
# Skills — level labels (Phase 2 prep, constants only)
# ============================================================================

SKILL_LEVEL_LABELS = {
    1:  "覚えたて",
    2:  "わかってきた",
    3:  "使えるようになった",
    4:  "慣れてきた",
    5:  "手に馴染んできた",
    6:  "得意になってきた",
    7:  "かなり使いこなせる",
    8:  "得意分野",
    9:  "エキスパート",
    10: "マスター",
}

# ============================================================================
# Rebecca — Voice messages by mood state (Phase 2A personality layer)
# ============================================================================

REBECCA_VOICE_MESSAGES = {
    "great": [
        "今日は調子いい！なんでもできそう",
        "よし、やるか！",
        "いい感じ。この調子でいこう",
        "今日のあたし、けっこうイケてる",
    ],
    "good": [
        "まぁまぁかな",
        "悪くないよ",
        "ふつうにいい感じ",
        "今日も来てくれたんだ",
    ],
    "normal": [
        "ふつう",
        "......別に",
        "まぁ、やることやるか",
        "特に変わりなし",
    ],
    "down": [
        "ちょっとだるい......",
        "......今日はあんまり",
        "なんか調子出ない",
        "......ひま",
    ],
    "bad": [
        "......",
        "......もう無理",
        "放っといて",
        ".........",
    ],
}

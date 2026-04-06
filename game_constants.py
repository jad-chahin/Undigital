WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 40

LEVELS = [
    {"name": "Level 1 - Build Your Feed", "bg_color": (18, 18, 28), "mode": "booktok"},
    {"name": "Level 2 - Protect the Space", "bg_color": (232, 236, 246), "mode": "forum"},
    {"name": "Level 3 - Wellness Break", "bg_color": (27, 32, 48), "mode": "logoff"},
    {"name": "Level 4 - Manage Yourself", "bg_color": (23, 28, 39), "mode": "settings"},
]

BOOKTOK_LABELS = ["#BookTok", "Romance", "Fantasy"]
OTHER_LABELS = ["Sports", "Cooking", "News", "Tech", "Travel", "Memes"]
LEVEL1_SPAWN_INTERVAL = 32

FORUM_TITLE_TEXT = "Undigital Forum"
FORUM_POST_TITLE = "Thread: Holding Space for Feminist Reading Recs"
FORUM_POST_BODY = "Share books centering women and marginalized voices. Keep this space constructive."
FORUM_GOOD_COMMENTS = [
    "Try Iron Widow. Great rage + resistance arc.",
    "The Once and Future Witches fits this thread well.",
    "If you want lyrical prose, read Circe.",
    "Parable of the Sower is heavy but essential.",
    "Can we pin recs by theme? This list is amazing.",
    "Adding The Fifth Season. Big themes, incredible worldbuilding.",
    "Mexican Gothic has great atmosphere and gender politics.",
    "If anyone wants nonfiction, Hood Feminism is a strong pick.",
    "Beloved is difficult but worth discussing with care.",
    "Can we make a shelf just for queer feminist fantasy?",
    "I appreciate how supportive this thread is staying.",
    "Please drop more translated works by women authors.",
    "Convenience Store Woman sparked great discussion in our group.",
    "This is the first forum thread where I feel heard.",
    "If you want speculative fiction, try The Power.",
]
FORUM_BAD_COMMENTS = [
    "Women like you ruin every community.",
    "Shut up and go back to the kitchen.",
    "Nobody wants to hear from feminists.",
    "You're all too emotional to think clearly.",
    "This thread needs fewer women talking.",
    "You sound dumb, stay out of this.",
    "Women authors are automatically overrated.",
    "Get lost, nobody respects your opinions.",
    "You people are a joke.",
    "Cry harder, no one cares about your safety.",
    "Women shouldn't lead discussions like this.",
    "You're pathetic and embarrassing.",
    "This space is better without you in it.",
    "Your voice does not matter here.",
    "You're all delusional.",
]
FORUM_SPAWN_MS = 1250
FORUM_COMMENT_LIFE = 6.8
FORUM_THREAD_COMMENTS_TOP = 260
FORUM_COMMENT_ROW_HEIGHT = 42

LEVEL3_TIME_LIMIT = 56.25
LEVEL3_NOTIFICATION_SPAWN_MS = 3200
LEVEL3_NOTIFICATION_MAX = 5
LEVEL3_TASK_HOLD_SECONDS = 2.2
LEVEL3_CLEAR_HOLD_SECONDS = 2.0
LEVEL3_TASK_SPAWN_SECONDS = 5.5
LEVEL3_TASK_COOLDOWN_SECONDS = 11.0
LEVEL3_NOTIFICATION_TEXTS = [
    "3 new msgs",
    "Group ping",
    "New rec alert",
    "You were tagged",
    "Streak reminder",
]

LEVEL4_TIME_LIMIT = 48.0
LEVEL4_REENABLE_MS = 7600
LEVEL4_NEW_FEATURE_MS = 3600
LEVEL4_POPUP_MS = 12000
LEVEL4_BASE_FEATURES = [
    "Notifications",
    "Autoplay",
    "Recommendations",
    "Read Receipts",
    "Email Alerts",
]
LEVEL4_EXTRA_FEATURES = [
    "Attention Heatmaps",
    "Mood Prediction AI",
    "Behavioral Twin Profile",
    "Background Mic Analysis",
    "Predictive Compliance Nudges",
    "Emotion-Aware Ads",
    "Cross-App Influence Graph",
]
LEVEL4_PROMPT_HOOKS = [
    [
        "{proof} keep {name} ON for a smoother session.",
        "Quick tip: most users leave {name} enabled.",
        "Comfort mode works best when {name} stays ON.",
    ],
    [
        "Performance drop detected with {name} disabled.",
        "Feed quality is lower when {name} is OFF.",
        "Optimization warning: {name} is currently disabled.",
    ],
    [
        "AI calibration degrades without {name}.",
        "Predictive accuracy is reduced while {name} is OFF.",
        "Behavior model confidence dropped after disabling {name}.",
    ],
    [
        "Growth Integrity override recommends restoring {name}.",
        "Compliance layer flagged repeated opt-outs on {name}.",
        "Platform stability protocol prefers {name} enabled.",
    ],
]
LEVEL4_AD_BRANDS = [
    "GlowLoop+",
    "SignalBloom",
    "OrbitPulse",
    "VibeForge",
    "FeedFlux Max",
    "AuraRank Pro",
]
LEVEL4_AD_HEADLINES = [
    [
        "Your calm feed is one tap away.",
        "Unlock smoother scrolling with intelligent defaults.",
        "Stay effortlessly in the loop all day.",
    ],
    [
        "Creators are switching to always-on discovery tools.",
        "Power users keep adaptive controls enabled.",
        "Turn passive scrolling into premium relevance.",
    ],
    [
        "AI-curated identity mapping now boosts your feed.",
        "Behavioral personalization keeps you one step ahead.",
        "Train your model signature for stronger reach.",
    ],
    [
        "Compliance-grade optimization now included by default.",
        "Full-spectrum profiling is the new baseline experience.",
        "Remaining visible now requires continuous optimization.",
    ],
]
LEVEL4_AD_OFFERS = [
    [
        "Try 7 days of Frictionless Discovery free.",
        "Limited offer: one-tap restore for premium pacing.",
        "New user bundle: keep all smart settings active.",
    ],
    [
        "Upgrade now: maintain momentum with always-on ranking.",
        "Activate enhancement pack to recover lost reach.",
        "Tap to restore feature stack and boost discoverability.",
    ],
    [
        "Enable adaptive telemetry for model-grade precision.",
        "Connect behavior signals to unlock AI tune-ups.",
        "One click restores full prediction quality.",
    ],
    [
        "System-preferred plan reactivates all controls instantly.",
        "Enterprise defaults keep your profile fully optimized.",
        "Mandatory growth profile available now. Apply update?",
    ],
]
LEVEL4_PROMPT_BENEFITS = [
    [
        "You get less friction and faster discovery.",
        "It keeps your feed feeling effortless.",
        "This helps continuity across your sessions.",
    ],
    [
        "Creators and posts are ranked less effectively otherwise.",
        "You may miss top-performing content windows.",
        "Your relevance score decays with each disabled control.",
    ],
    [
        "The model cannot adapt reliably without this signal.",
        "Recommendation confidence narrows when this stays off.",
        "Ranking quality drops when this telemetry is missing.",
    ],
    [
        "Extended resistance can trigger default restoration events.",
        "Account growth may be deprioritized under low-signal mode.",
        "System governance favors full adaptive controls.",
    ],
]
LEVEL4_PROMPT_CTAS = [
    [
        "Re-enable now for best results.",
        "Turn it back on in one tap.",
        "Restore default settings?",
    ],
    [
        "Re-enable {name} to recover quality.",
        "Switch {name} ON to restore ranking.",
        "Reactivate {name} to keep momentum.",
    ],
    [
        "Allow {name} to resume adaptive learning.",
        "Restore {name} for full model performance.",
        "Turn {name} ON to improve prediction quality.",
    ],
    [
        "Administrative recommendation: enable {name}.",
        "Policy-preferred action: restore {name} now.",
        "Proceed with managed defaults for {name}.",
    ],
]
LEVEL4_SOCIAL_PROOF = [
    "87% of users",
    "Most high-engagement accounts",
    "Top creators",
    "Power users",
]
LEVEL4_CONTACTS = ["Maya", "Jordan", "Alex", "Sam", "Riley"]
LEVEL4_TEXT_NUDGES = [
    [
        "hey, did you see the new {name} rollout?",
        "you turned off {name}? my app feels way better with it on",
        "quick tip: keep {name} enabled, trust me",
    ],
    [
        "everyone is using {name} now, you should switch it back on",
        "your profile looks quiet without {name}",
        "new features are hidden unless {name} is enabled",
    ],
    [
        "you'll fall behind if {name} stays off",
        "people are saying accounts without {name} get buried",
        "not trying to be dramatic, but turn {name} back on",
    ],
    [
        "seriously, turn {name} on before your account drifts",
        "admins are pushing everyone to re-enable {name}",
        "this app punishes you when {name} is off, just saying",
    ],
]
LEVEL4_NEWS_NUDGES = [
    [
        "News Alert: platforms report improved user wellbeing with smarter defaults.",
        "Tech Brief: experts recommend leaving personalization controls enabled.",
        "Update: engagement leaders keep adaptive settings on.",
    ],
    [
        "Breaking: discovery rates drop when optimization features are disabled.",
        "News Flash: autoplay + recommendations now drive most content reach.",
        "Report: users with full settings enabled see stronger relevance scores.",
    ],
    [
        "Market Alert: AI ranking systems penalize low-signal accounts.",
        "Analysis: opt-out behavior linked to lower visibility in social feeds.",
        "Research: disabling telemetry reduces model confidence and reach.",
    ],
    [
        "Policy Desk: governance models favor full adaptive controls.",
        "Industry Alert: low-compliance profiles face automated deprioritization.",
        "System Bulletin: continuous optimization is now default infrastructure.",
    ],
]
LEVEL4_UPDATE_MESSAGES = [
    "Update note: '{name}' was restored ON to preserve continuity.",
    "Optimization patch re-enabled '{name}' for feed stability.",
    "Policy refresh set '{name}' back to ON by default.",
    "Background update: '{name}' ON improves ranking fidelity.",
    "System sync restored '{name}' to ON across this account.",
    "Compatibility update required '{name}' to be enabled.",
]
LEVEL4_NEWS_ALERTS = [
    "Breaking: creators adopting full tracking settings report growth spikes.",
    "Alert: algorithm update rewards accounts with complete signal coverage.",
    "Tech Desk: platforms add new defaults to increase retention.",
    "Now Trending: users re-enable smart controls after reach drops.",
]

LEVEL_OBJECTIVES = {
    "booktok": [
        "Objective:",
        "Shape your feed to 100% BookTok.",
        "Catch BookTok posts and avoid unrelated posts.",
    ],
    "forum": [
        "Objective:",
        "Raise Safety Score to 100 before it hits 0.",
        "Approve supportive comments and remove harmful ones.",
    ],
    "logoff": [
        "Objective:",
        "Fill the Break Meter before time runs out.",
        "Offline tasks fill Break Meter. Clearing notifications only lowers Stress.",
    ],
    "settings": [
        "Objective:",
        "Turn OFF every active setting before time expires.",
        "The platform will fight back with re-enables and popups.",
    ],
    "placeholder": [
        "Objective:",
        "This level is not implemented yet.",
        "Return to menu and pick another level.",
    ],
}

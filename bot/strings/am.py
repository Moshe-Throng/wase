"""
Amharic strings for Wase (ዋሴ) bot.
All user-facing text lives here for easy review and editing.

NOTE TO REVIEWER: Please review all Amharic text below.
The bot name is Wase (ዋሴ) — meaning "my guarantor".
"""

# ══════════════════════════════════════════════════════════════
# WELCOME & MENU
# ══════════════════════════════════════════════════════════════

WELCOME_TITLE = "✦ ዋሴ"
WELCOME_SUBTITLE = "ታማኝነትህ ዋጋ አለው"
WELCOME_BODY = "በጓደኞች መካከል ያለውን ገንዘብ በቀላሉ ይከታተሉ።"
FEATURE_IOU = "🤝 እዳ — ማን ምን ያህል እንደሚያበድር ይመዝግቡ"
FEATURE_COLLECT = "💰 ማሰባሰብ — ከቡድን ገንዘብ ይሰብስቡ"
FEATURE_DASH = "📊 ዳሽቦርድ — ሁሉንም ይመልከቱ"
FREE_NOTE = "ሁሉም ነገር ነፃ ነው። ሁለቱም ወገኖች ያረጋግጣሉ።"

# ══════════════════════════════════════════════════════════════
# LANGUAGE SELECTION
# ══════════════════════════════════════════════════════════════

LANG_PROMPT = "🌍 ቋንቋ ይምረጡ:"
LANG_CHANGED = "✅ ቋንቋ ወደ አማርኛ ተቀይሯል"

# Full welcome message (assembled in handler)
WELCOME_MESSAGE = (
    f"{WELCOME_TITLE}\n"
    f"{WELCOME_SUBTITLE}\n\n"
    f"{WELCOME_BODY}\n\n"
    f"{FEATURE_IOU}\n"
    f"{FEATURE_COLLECT}\n"
    f"{FEATURE_DASH}\n\n"
    f"{FREE_NOTE}"
)

# ══════════════════════════════════════════════════════════════
# IOU MESSAGES
# ══════════════════════════════════════════════════════════════

IOU_NEW = "🤝 አዲስ እዳ #{id}"
IOU_LENT = "{lender} ➜ አበደረ ➜ {borrower}"
IOU_AMOUNT = "💰 መጠን: {amount} ብር"
IOU_REASON = "📝 ምክንያት: {desc}"
IOU_DUE = "📅 የመክፈያ ቀን: {date}"
IOU_WAITING = "⏳ {name} እስኪያረጋግጥ በመጠበቅ ላይ..."
IOU_CONFIRMED = "✅ እዳ #{id} ተረጋግጧል!"
IOU_DISPUTED = "⚠️ እዳ #{id} ተቃውሟል"
IOU_PAID = "🎉 እዳ #{id} — ተከፍሏል!"
IOU_PAID_DETAIL = "{amount} ብር ተፈጽሟል። ሁለቱም አረጋግጠዋል።"
IOU_TRUST_NOTE = "በሁለቱም የአስተማማኝነት ነጥብ ላይ ተመዝግቧል።"
IOU_NOT_PAID = "❌ እዳ #{id} — ክፍያ አልተረጋገጠም። እርስ በራሳችሁ ተነጋገሩ።"
IOU_PAY_SENT = "💸 የመክፈያ ጥያቄ ለ{name} ተልኳል። ማረጋገጫ እስኪሰጥ ጠብቅ።"
IOU_CONFIRMED_NOTIFY = "✅ {borrower} እዳ #{id} ({amount}) አረጋግጧል!"

# IOU confirmation request sent to borrower
IOU_CONFIRM_REQUEST = (
    "🤝 {lender} {amount} ብር አበድሬሃለው ይላል።\n"
    "📝 ምክንያት: {desc}\n\n"
    "ይህን ታረጋግጣለህ?"
)

# IOU dispute notification to lender
IOU_DISPUTE_NOTIFY = "⚠️ {borrower} እዳ #{id} ተቃውሟል። ስለ ጉዳዩ እርስ በራሳችሁ ተነጋገሩ።"

# IOU payment request to other party
IOU_PAY_REQUEST = "💰 {name} እዳ #{id} ({amount} ብር) ተከፍሏል ይላል። ታረጋግጣለህ?"

# IOU list header
IOU_LIST_HEADER = "📋 የእዳ ዝርዝር — {name}\n"
IOU_LIST_EMPTY = "✨ ምንም ንቁ እዳ የለም!"
IOU_LIST_AS_LENDER = "💚 አበድረሃል:"
IOU_LIST_AS_BORROWER = "🔴 ትበደራለህ:"
IOU_LIST_ITEM = "  #{id} | {other} | {amount} ብር | {status}"

# ══════════════════════════════════════════════════════════════
# BUTTON LABELS
# ══════════════════════════════════════════════════════════════

BTN_CONFIRM = "✅ አረጋግጣለሁ"
BTN_DISPUTE = "❌ አልስማማም"
BTN_PAID = "✅ ከፍያለሁ"
BTN_STATUS = "📊 ሁኔታ"
BTN_CONFIRM_PAY = "✅ ተከፍሏል አረጋግጣለሁ"
BTN_NOT_PAID = "❌ አልተከፈለም"
BTN_NEW_IOU = "🤝 አዲስ እዳ"
BTN_NEW_COLLECT = "💰 ማሰባሰብ"
BTN_DASHBOARD = "📊 ዳሽቦርድ"
BTN_SCORE = "🛡 ነጥብ"
BTN_OPEN_APP = "📱 ዋሴ ክፈት"

# ══════════════════════════════════════════════════════════════
# COLLECTION MESSAGES
# ══════════════════════════════════════════════════════════════

COL_NEW = "💰 አዲስ ማሰባሰብ #{id}"
COL_TITLE = "📋 {title}"
COL_AMOUNT_EACH = "💰 መጠን: {amount} ብር ለእያንዳንዱ"
COL_TARGET = "🎯 ዒላማ: {amount} ብር"
COL_STARTED_BY = "👤 የጀመረው: {name}"
COL_USER_PAID = "✅ {name} ለ{title} ከፍለዋል"
COL_COUNT = "📊 እስካሁን {count} ሰዎች ከፍለዋል"
COL_COMPLETE = "🎉 ማሰባሰብ ተጠናቋል!"
COL_PROGRESS = "📊 {paid}/{total} ከፍለዋል — {amount} ብር ተሰብስቧል"

# Collection list
COL_LIST_HEADER = "📋 ንቁ ማሰባሰቦች\n"
COL_LIST_EMPTY = "✨ ምንም ንቁ ማሰባሰብ የለም!"
COL_LIST_ITEM = "  #{id} | {title} | {count} ከፍለዋል"

# Collection status board
COL_STATUS_HEADER = "📊 ማሰባሰብ #{id} — {title}\n"
COL_STATUS_PAID = "  ✅ {name}"
COL_STATUS_UNPAID = "  ⬜ {name}"

# ══════════════════════════════════════════════════════════════
# DASHBOARD MESSAGES
# ══════════════════════════════════════════════════════════════

DASH_TITLE = "📊 ዳሽቦርድ — {name}"
DASH_OWED_TO = "💚 የሚያበድሩህ: {amount} ብር"
DASH_YOU_OWE = "🔴 የምታበድር: {amount} ብር"
DASH_NET_POS = "ጠቅላላ: {amount} ብር ይበልጥልሃል"
DASH_NET_NEG = "ጠቅላላ: {amount} ብር ታበድራለህ"
DASH_NET_ZERO = "ጠቅላላ: ሁሉም ተስተካክሏል ✨"
DASH_OVERDUE = "⚠️ ያለፈ: {count} እዳዎች ቀናቸው አልፏል"
DASH_COMPLETED = "✅ ተጠናቅቀዋል: {count} እዳዎች (ሁሌ)"
DASH_CONTRIBUTIONS = "💰 ማሰባሰብ ተሳትፎ: {count} (ሁሌ)"

# ══════════════════════════════════════════════════════════════
# TRUST SCORE MESSAGES
# ══════════════════════════════════════════════════════════════

SCORE_TITLE = "🛡 የአስተማማኝነት ነጥብ — {name}"
SCORE_VALUE = "ነጥብ: {score}/100"
SCORE_TIER = "ደረጃ: {tier}"
SCORE_REPAID = "💸 የተከፈሉ እዳዎች: {done}/{total}"
SCORE_COLLECT = "💰 ማሰባሰብ ተሳትፎ: {count}"
SCORE_CONNECT = "👥 ግንኙነቶች: {count}"
SCORE_HISTORY = "📋 ታሪክ: {status}"
SCORE_OVERDUE_PENALTY = "⚠️ የዘገየ ቅጣት: -{points}"
SCORE_IMPROVE = "💡 ነጥብህን ለማሻሻል: እዳዎችን በወቅቱ ክፈል፣ ማሰባሰብ ላይ ተሳተፍ"

# Trust tiers
TIER_NEW = "🌟 አዲስ"
TIER_RISING = "⭐ እየተሻሻለ"
TIER_TRUSTED = "🏆 አስተማማኝ"
TIER_EXCELLENT = "💎 በጣም ጥሩ"

# Progress bar helper (used in score display)
# Example: "████████░░ 80%"
BAR_FILLED = "█"
BAR_EMPTY = "░"

# ══════════════════════════════════════════════════════════════
# ERROR MESSAGES
# ══════════════════════════════════════════════════════════════

ERR_INVALID_AMOUNT = "❌ ልክ ያልሆነ መጠን"
ERR_SELF_IOU = "❌ ለራስህ እዳ መመዝገብ አትችልም!"
ERR_NOT_FOUND = "❌ አልተገኘም"
ERR_NOT_YOURS = "❌ ይህ የእርስዎ አይደለም"
ERR_ALREADY_PAID = "ቀድሞ ከፍለዋል!"
ERR_USER_NOT_STARTED = "⚠️ @{username} ገና ዋሴ አልጀመረም"
ERR_GROUP_ONLY = "💰 ማሰባሰብ በቡድን ውስጥ ብቻ ይሠራል!\n\nእንዴት?\n1. @{bot_username} ቦትን ወደ ቡድንዎ ጨምሩ\n2. በቡድኑ ውስጥ /sebeseb ይላኩ\n\nምሳሌ: /sebeseb ለሃና ስጦታ - 500 ሰው"
ERR_DM_FAILED = "⚠️ @{username} ዋሴን ገና አልጀመረም። እባክህ ይህንን መልእክት ላክለት።"
ERR_USAGE_IOU = "📝 አጠቃቀም: /eda @ተጠቃሚ መጠን [ምክንያት]\nምሳሌ: /eda @dawit_k 5000 ለምሳ"
ERR_USAGE_COLLECT = "📝 አጠቃቀም: /sebeseb ርዕስ - መጠን ሰው\nምሳሌ: /sebeseb ለሃና ስጦታ - 500 ሰው"
ERR_USAGE_PAYBACK = "📝 አጠቃቀም: /kefel [የእዳ ቁጥር]\nምሳሌ: /kefel 42"

# ══════════════════════════════════════════════════════════════
# NEW STRINGS (for bilingual support)
# ══════════════════════════════════════════════════════════════

IOU_NOT_PAID = "❌ እዳ #{id} — ክፍያ አልተረጋገጠም። እርስ በራሳችሁ ተነጋገሩ።"
IOU_PAY_SENT = "💸 የመክፈያ ጥያቄ ለ{name} ተልኳል።"
IOU_CONFIRMED_NOTIFY = "✅ {borrower} እዳ #{id} ({amount}) አረጋግጧል!"
MENU_DASHBOARD_HINT = "📊 /dashboard ይጻፉ"
MENU_SCORE_HINT = "🛡 /netib ይጻፉ"

# ══════════════════════════════════════════════════════════════
# CONVERSATIONAL IOU FLOW
# ══════════════════════════════════════════════════════════════

CONV_DIRECTION = "🤝 ምን ሆነ?"
BTN_I_LENT = "💸 አበድሬያለሁ"
BTN_I_BORROWED = "🤲 ተበድሬያለሁ"
CONV_WHO_BORROWED = "👤 ማን ተበድሮ? @username ላክ"
CONV_WHO_LENT = "👤 ማን አበድሮህ? @username ላክ"
CONV_AMOUNT = "💰 ስንት ብር?"
CONV_AMOUNT_RETRY = "ቁጥር ብቻ ላክ (ምሳሌ: 5000)"
CONV_REASON = "📝 ምክንያት? (ምሳሌ: ለምሳ)\nለመዝለል ⏩ ተጫን"
CONV_DEADLINE = "📅 መቼ ይመለስ?"
CONV_DEADLINE_RETRY = "📅 ከታች ይምረጡ ወይም ቀን ይጻፉ (2026-04-15)"
CONV_CANCELLED = "❌ ተሰርዟል"
BTN_SKIP = "⏩ ዝለል"
BTN_1_WEEK = "1 ሳምንት"
BTN_2_WEEKS = "2 ሳምንት"
BTN_1_MONTH = "1 ወር"
BTN_NO_DEADLINE = "⏩ ቀን የለም"

# Borrower-initiated IOU: lender sees this
IOU_CONFIRM_LENDER_REQUEST = (
    "🤲 {borrower} {amount} ብር ተበድሬሃለው ይላል።\n"
    "📝 ምክንያት: {desc}\n\n"
    "ይህን ታረጋግጣለህ?"
)

# ══════════════════════════════════════════════════════════════
# REMINDER MESSAGES
# ══════════════════════════════════════════════════════════════

REMINDER = "🔔 ማስታወሻ: እዳ #{id} — ለ{lender} {amount} ብር — ቀሩ {days} ቀናት"
REMINDER_OVERDUE = "🔴 ያለፈ! እዳ #{id} — ለ{lender} {amount} ብር — {days} ቀናት ዘግይቷል"
REMINDER_OVERDUE_LENDER = "🔴 @{borrower} እዳ #{id} ({amount} ብር) {days} ቀናት ዘግይቷል"

# ══════════════════════════════════════════════════════════════
# HELP / COMMAND LIST
# ══════════════════════════════════════════════════════════════

HELP_TITLE = "📖 ዋሴ — ትዕዛዞች\n"
HELP_COMMANDS = (
    "🤝 /eda @ተጠቃሚ መጠን [ምክንያት] — አዲስ እዳ\n"
    "📋 /edawoch — የእዳ ዝርዝር\n"
    "💸 /kefel [ቁጥር] — እዳ ከፍያለሁ\n"
    "💰 /sebeseb ርዕስ - መጠን ሰው — ማሰባሰብ (ቡድን)\n"
    "📋 /mesebeboch — ንቁ ማሰባሰቦች (ቡድን)\n"
    "📊 /dashboard — ዳሽቦርድ\n"
    "🛡 /netib — የአስተማማኝነት ነጥብ\n"
    "🌍 /language — ቋንቋ ቀይር\n"
    "📖 /erdata — ይህ ዝርዝር\n"
)

# Invite message (forwarded to borrower who hasn't started bot)
INVITE_MESSAGE = (
    "👋 ዋሴ (Wase) — የገንዘብ ክትትል ቦት\n\n"
    "ጓደኛህ ዋሴ ቦትን ይጠቀማል። ለመጀመር ይህንን ተጫን:\n"
    "👉 https://t.me/{bot_username}?start=invite"
)

MENU_DASHBOARD_HINT = "📊 /dashboard ለማየት ይጻፉ"
MENU_SCORE_HINT = "🛡 /netib ለማየት ይጻፉ"

# ══════════════════════════════════════════════════════════════
# STATUS LABELS (for IOU list display)
# ══════════════════════════════════════════════════════════════

STATUS_PENDING = "⏳ በመጠበቅ"
STATUS_CONFIRMED = "✅ ተረጋግጧል"
STATUS_COMPLETED = "🎉 ተከፍሏል"
STATUS_DISPUTED = "⚠️ ተቃውሟል"

STATUS_MAP = {
    "pending": STATUS_PENDING,
    "confirmed": STATUS_CONFIRMED,
    "completed": STATUS_COMPLETED,
    "disputed": STATUS_DISPUTED,
}

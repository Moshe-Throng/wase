"""
English strings for Wase bot.
"""

# ══════════════════════════════════════════════════════════════
# WELCOME & MENU
# ══════════════════════════════════════════════════════════════

WELCOME_TITLE = "✦ Wase"
WELCOME_SUBTITLE = "Your trust has value"
WELCOME_BODY = "Easily track money between friends."
FEATURE_IOU = "🤝 IOU — Record who owes what"
FEATURE_COLLECT = "💰 Collect — Gather money from a group"
FEATURE_DASH = "📊 Dashboard — See everything at a glance"
FREE_NOTE = "Everything is free. Both parties confirm."

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
# LANGUAGE SELECTION
# ══════════════════════════════════════════════════════════════

LANG_PROMPT = "🌍 Choose your language:"
LANG_CHANGED = "✅ Language set to English"

# ══════════════════════════════════════════════════════════════
# IOU MESSAGES
# ══════════════════════════════════════════════════════════════

IOU_NEW = "🤝 New IOU #{id}"
IOU_LENT = "{lender} ➜ lent ➜ {borrower}"
IOU_AMOUNT = "💰 Amount: {amount} Birr"
IOU_REASON = "📝 Reason: {desc}"
IOU_DUE = "📅 Due date: {date}"
IOU_WAITING = "⏳ Waiting for {name} to confirm..."
IOU_CONFIRMED = "✅ IOU #{id} confirmed!"
IOU_DISPUTED = "⚠️ IOU #{id} disputed"
IOU_PAID = "🎉 IOU #{id} — Paid!"
IOU_PAID_DETAIL = "{amount} Birr settled. Both parties confirmed."
IOU_TRUST_NOTE = "Recorded on both trust scores."
IOU_NOT_PAID = "❌ IOU #{id} — Payment not confirmed. Please sort it out between yourselves."
IOU_PAY_SENT = "💸 Payment request sent to {name}. Waiting for confirmation."
IOU_CONFIRMED_NOTIFY = "✅ {borrower} confirmed IOU #{id} ({amount})!"

IOU_CONFIRM_REQUEST = (
    "🤝 {lender} says you owe {amount} Birr.\n"
    "📝 Reason: {desc}\n\n"
    "Do you confirm?"
)

IOU_DISPUTE_NOTIFY = "⚠️ {borrower} disputed IOU #{id}. Please sort it out between yourselves."
IOU_PAY_REQUEST = "💰 {name} says IOU #{id} ({amount} Birr) is paid. Do you confirm?"

IOU_LIST_HEADER = "📋 IOUs — {name}\n"
IOU_LIST_EMPTY = "✨ No active IOUs!"
IOU_LIST_AS_LENDER = "💚 You lent:"
IOU_LIST_AS_BORROWER = "🔴 You owe:"
IOU_LIST_ITEM = "  #{id} | {other} | {amount} Birr | {status}"

# ══════════════════════════════════════════════════════════════
# BUTTON LABELS
# ══════════════════════════════════════════════════════════════

BTN_CONFIRM = "✅ Confirm"
BTN_DISPUTE = "❌ Dispute"
BTN_PAID = "✅ I Paid"
BTN_STATUS = "📊 Status"
BTN_CONFIRM_PAY = "✅ Confirm Payment"
BTN_NOT_PAID = "❌ Not Paid"
BTN_NEW_IOU = "🤝 New IOU"
BTN_NEW_COLLECT = "💰 Collect"
BTN_DASHBOARD = "📊 Dashboard"
BTN_SCORE = "🛡 Score"
BTN_OPEN_APP = "📱 Open Wase"

# ══════════════════════════════════════════════════════════════
# COLLECTION MESSAGES
# ══════════════════════════════════════════════════════════════

COL_NEW = "💰 New Collection #{id}"
COL_TITLE = "📋 {title}"
COL_AMOUNT_EACH = "💰 Amount: {amount} Birr each"
COL_TARGET = "🎯 Target: {amount} Birr"
COL_STARTED_BY = "👤 Started by: {name}"
COL_USER_PAID = "✅ {name} paid for {title}"
COL_COUNT = "📊 {count} people paid so far"
COL_COMPLETE = "🎉 Collection complete!"
COL_PROGRESS = "📊 {paid}/{total} paid — {amount} Birr collected"

COL_LIST_HEADER = "📋 Active Collections\n"
COL_LIST_EMPTY = "✨ No active collections!"
COL_LIST_ITEM = "  #{id} | {title} | {count} paid"

COL_STATUS_HEADER = "📊 Collection #{id} — {title}\n"
COL_STATUS_PAID = "  ✅ {name}"
COL_STATUS_UNPAID = "  ⬜ {name}"

# ══════════════════════════════════════════════════════════════
# DASHBOARD MESSAGES
# ══════════════════════════════════════════════════════════════

DASH_TITLE = "📊 Dashboard — {name}"
DASH_OWED_TO = "💚 Owed to you: {amount} Birr"
DASH_YOU_OWE = "🔴 You owe: {amount} Birr"
DASH_NET_POS = "Net: +{amount} Birr"
DASH_NET_NEG = "Net: -{amount} Birr"
DASH_NET_ZERO = "Net: All settled ✨"
DASH_OVERDUE = "⚠️ Overdue: {count} IOUs past due"
DASH_COMPLETED = "✅ Completed: {count} IOUs (lifetime)"
DASH_CONTRIBUTIONS = "💰 Collections: {count} contributions (lifetime)"

# ══════════════════════════════════════════════════════════════
# TRUST SCORE MESSAGES
# ══════════════════════════════════════════════════════════════

SCORE_TITLE = "🛡 Trust Score — {name}"
SCORE_VALUE = "Score: {score}/100"
SCORE_TIER = "Tier: {tier}"
SCORE_REPAID = "💸 IOUs Repaid: {done}/{total}"
SCORE_COLLECT = "💰 Collections: {count}"
SCORE_CONNECT = "👥 Connections: {count}"
SCORE_HISTORY = "📋 History: {status}"
SCORE_OVERDUE_PENALTY = "⚠️ Overdue penalty: -{points}"
SCORE_IMPROVE = "💡 To improve: pay IOUs on time, contribute to collections"

TIER_NEW = "🌟 New"
TIER_RISING = "⭐ Rising"
TIER_TRUSTED = "🏆 Trusted"
TIER_EXCELLENT = "💎 Excellent"

BAR_FILLED = "█"
BAR_EMPTY = "░"

# ══════════════════════════════════════════════════════════════
# ERROR MESSAGES
# ══════════════════════════════════════════════════════════════

ERR_INVALID_AMOUNT = "❌ Invalid amount"
ERR_SELF_IOU = "❌ You can't create an IOU with yourself!"
ERR_NOT_FOUND = "❌ Not found"
ERR_NOT_YOURS = "❌ This isn't yours"
ERR_ALREADY_PAID = "Already paid!"
ERR_USER_NOT_STARTED = "⚠️ @{username} hasn't started Wase yet"
ERR_GROUP_ONLY = "💰 Collections only work in group chats!\n\nHow to use:\n1. Add @{bot_username} to your group\n2. Send /sebeseb in the group\n\nExample: /sebeseb Birthday gift for Sara - 500 each"
ERR_DM_FAILED = "⚠️ @{username} hasn't started Wase yet. Please forward them this invite."
ERR_USAGE_IOU = "📝 Usage: /eda @user amount [reason]\nExample: /eda @dawit_k 5000 for lunch"
ERR_USAGE_COLLECT = "📝 Usage: /sebeseb title - amount each\nExample: /sebeseb Gift for Hanna - 500 each"
ERR_USAGE_PAYBACK = "📝 Usage: /kefel [IOU number]\nExample: /kefel 42"

# ══════════════════════════════════════════════════════════════
# CONVERSATIONAL IOU FLOW
# ══════════════════════════════════════════════════════════════

CONV_DIRECTION = "🤝 What happened?"
CONV_DIRECTION_HINT = "👆 Type /eda to start recording a loan"
BTN_I_LENT = "💸 I lent money"
BTN_I_BORROWED = "🤲 I borrowed money"
CONV_WHO_BORROWED = "👤 Who borrowed from you? Send their @username"
CONV_WHO_LENT = "👤 Who lent you money? Send their @username"
CONV_AMOUNT = "💰 How much? (in Birr)"
CONV_AMOUNT_RETRY = "Send a number only (e.g. 5000)"
CONV_REASON = "📝 Reason? (e.g. for lunch)\nTap ⏩ to skip"
CONV_DEADLINE = "📅 When should it be repaid?"
CONV_DEADLINE_RETRY = "📅 Pick a button or type a date like 2026-04-15"
CONV_CANCELLED = "❌ Cancelled"
BTN_SKIP = "⏩ Skip"
BTN_1_WEEK = "1 week"
BTN_2_WEEKS = "2 weeks"
BTN_1_MONTH = "1 month"
BTN_NO_DEADLINE = "⏩ No deadline"

# Borrower-initiated IOU: lender sees this confirmation
IOU_CONFIRM_LENDER_REQUEST = (
    "🤲 {borrower} says they borrowed {amount} Birr from you.\n"
    "📝 Reason: {desc}\n\n"
    "Do you confirm?"
)

# ══════════════════════════════════════════════════════════════
# REMINDER MESSAGES
# ══════════════════════════════════════════════════════════════

REMINDER = "🔔 Reminder: IOU #{id} — {amount} Birr to {lender} — {days} days left"
REMINDER_OVERDUE = "🔴 Overdue! IOU #{id} — {amount} Birr to {lender} — {days} days late"
REMINDER_OVERDUE_LENDER = "🔴 @{borrower} IOU #{id} ({amount} Birr) is {days} days overdue"

# ══════════════════════════════════════════════════════════════
# HELP / COMMAND LIST
# ══════════════════════════════════════════════════════════════

HELP_TITLE = "📖 Wase — Commands\n"
HELP_COMMANDS = (
    "🤝 /eda @user amount [reason] — New IOU\n"
    "📋 /edawoch — List IOUs\n"
    "💸 /kefel [number] — Mark IOU as paid\n"
    "💰 /sebeseb title - amount each — Collection (group)\n"
    "📋 /mesebeboch — Active collections (group)\n"
    "📊 /dashboard — Dashboard\n"
    "🛡 /netib — Trust score\n"
    "🌍 /language — Change language\n"
    "📖 /erdata — This list\n"
)

INVITE_MESSAGE = (
    "👋 Wase — Money tracking bot\n\n"
    "Your friend uses Wase. Tap to start:\n"
    "👉 https://t.me/{bot_username}?start=invite"
)

MENU_DASHBOARD_HINT = "📊 Type /dashboard"
MENU_SCORE_HINT = "🛡 Type /netib"

# ══════════════════════════════════════════════════════════════
# STATUS LABELS
# ══════════════════════════════════════════════════════════════

STATUS_PENDING = "⏳ Pending"
STATUS_CONFIRMED = "✅ Confirmed"
STATUS_COMPLETED = "🎉 Paid"
STATUS_DISPUTED = "⚠️ Disputed"

STATUS_MAP = {
    "pending": STATUS_PENDING,
    "confirmed": STATUS_CONFIRMED,
    "completed": STATUS_COMPLETED,
    "disputed": STATUS_DISPUTED,
}

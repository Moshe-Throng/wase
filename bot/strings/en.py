"""
English strings for Wase bot.
"""

# ══════════════════════════════════════════════════════════════
# WELCOME & MENU
# ══════════════════════════════════════════════════════════════

WELCOME_TITLE = "✦ Wase"
WELCOME_SUBTITLE = "Your trust has value"
WELCOME_BODY = "Easily track IOUs between friends."

WELCOME_MESSAGE = (
    f"{WELCOME_TITLE}\n"
    f"{WELCOME_SUBTITLE}\n\n"
    f"{WELCOME_BODY}\n"
    "Pick an action below 👇"
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

# Borrower-initiated IOU: lender sees this confirmation
IOU_CONFIRM_LENDER_REQUEST = (
    "🤲 {borrower} says they borrowed {amount} Birr from you.\n"
    "📝 Reason: {desc}\n\n"
    "Do you confirm?"
)

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

# Navigation buttons
BTN_GO_HOME = "🏠 Home"
BTN_MY_IOUS = "📋 My IOUs"
BTN_PAY_IOU = "💸 Mark as paid"

# Amount quick-pick
BTN_AMT_OTHER = "✏️ Other amount"

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

# Collection guided flow
COL_ASK_TITLE = "📝 What's the collection for?\n\nReply with a title (e.g. Birthday gift for Sara)"
COL_ASK_AMOUNT = "💰 How much per person? (in Birr)\n\nReply with the amount (e.g. 500)"
COL_TITLE_PLACEHOLDER = "e.g. Birthday gift for Sara"
COL_AMOUNT_PLACEHOLDER = "e.g. 500"

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
ERR_GROUP_ONLY = "💰 Collections only work in group chats!\n\nHow to use:\n1. Add @{bot_username} to your group\n2. Send /sebseb in the group\n\nExample: /sebseb Birthday gift for Sara - 500 each"
ERR_DM_FAILED = "⚠️ @{username} hasn't started Wase yet. Please forward them this invite."
ERR_USAGE_IOU = "📝 Usage: /eda @<username> amount [reason]\nExample: /eda @dawit_k 5000 for lunch\n\n(Replace <username> with the person's actual Telegram username)"
ERR_USAGE_COLLECT = "📝 Usage: /sebseb title - amount each\nExample: /sebseb Gift for Hanna - 500 each"
ERR_USAGE_PAYBACK = "📝 Usage: /kefel [IOU number]\nExample: /kefel 42"

# ══════════════════════════════════════════════════════════════
# CONVERSATIONAL IOU FLOW
# ══════════════════════════════════════════════════════════════

CONV_DIRECTION = "🤝 What happened?"
CONV_DIRECTION_HINT = "👆 Type /eda to start recording a loan"
BTN_I_LENT = "💸 I lent money"
BTN_I_BORROWED = "🤲 I borrowed money"
CONV_WHO_BORROWED = "👤 Who borrowed from you?\n\nSend their @username"
CONV_WHO_LENT = "👤 Who lent you money?\n\nSend their @username"
CONV_WHO_RETRY = "⚠️ @{username} hasn't joined Wase yet.\n\nTry another @username, or forward them the invite below:"
CONV_AMOUNT = "💰 How much? (in Birr)"
CONV_AMOUNT_PICK = "💰 How much? Pick or type amount:"
CONV_AMOUNT_CUSTOM = "✏️ Type the exact amount (e.g. 7500)"
CONV_AMOUNT_RETRY = "Send a number only (e.g. 5000)"
CONV_REASON = "📝 Reason? (e.g. for lunch)\nOr tap Skip 👇"
CONV_DEADLINE = "📅 When should it be repaid?"
CONV_DEADLINE_RETRY = "📅 Pick a button below, or type:\n• A date: 2026-04-15\n• A period: 10 days, 3 weeks, 2 months"
CONV_DEADLINE_CUSTOM = "✏️ Type a repayment period:\n• Date: 2026-04-15\n• Days: 10 days\n• Weeks: 3 weeks\n• Months: 2 months"
CONV_CANCELLED = "❌ Cancelled"
BTN_SKIP = "⏩ Skip"
BTN_3_DAYS = "3 days"
BTN_1_WEEK = "1 week"
BTN_2_WEEKS = "2 weeks"
BTN_1_MONTH = "1 month"
BTN_3_MONTHS = "3 months"
BTN_OTHER_DEADLINE = "✏️ Other"
BTN_NO_DEADLINE = "⏩ No deadline"

# ══════════════════════════════════════════════════════════════
# KEFEL BUTTON FLOW
# ══════════════════════════════════════════════════════════════

KEFEL_PICK = "💸 Which IOU was paid? Pick one:"
KEFEL_NO_IOUS = "✨ No confirmed IOUs to mark as paid."

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
    "🤝 /eda — New IOU (guided flow)\n"
    "📋 /edawoch — List IOUs\n"
    "💸 /kefel — Mark IOU as paid\n"
    "💰 /sebseb — Start a collection (group)\n"
    "📋 /mewachoch — Active collections (group)\n"
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

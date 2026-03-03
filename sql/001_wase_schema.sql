-- 001_wase_schema.sql
-- Wase (ዋሴ) — Ethiopian Social Trust Platform
-- Run in Supabase SQL Editor
-- Supabase project: ysrzmvsrvtovmiqtokqu (shared with devidends + intel-platform)

-- ══════════════════════════════════════════════════════════════
-- 1. USERS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS wase_users (
  user_id    BIGINT PRIMARY KEY,          -- Telegram user ID
  username   TEXT,                         -- @username (nullable, may change)
  first_name TEXT,                         -- Telegram display name
  language   TEXT DEFAULT 'am',            -- UI language
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ══════════════════════════════════════════════════════════════
-- 2. IOUs
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS wase_ious (
  id                   SERIAL PRIMARY KEY,
  lender_id            BIGINT NOT NULL REFERENCES wase_users(user_id),
  borrower_id          BIGINT NOT NULL REFERENCES wase_users(user_id),
  amount               DECIMAL NOT NULL CHECK (amount > 0),
  description          TEXT,
  due_date             DATE,
  status               TEXT NOT NULL DEFAULT 'pending'
                         CHECK (status IN ('pending', 'confirmed', 'completed', 'disputed')),
  confirmed_by_borrower BOOLEAN DEFAULT false,
  created_at           TIMESTAMPTZ DEFAULT now(),
  completed_at         TIMESTAMPTZ,
  reminder_count       INT DEFAULT 0,

  CONSTRAINT no_self_iou CHECK (lender_id != borrower_id)
);

CREATE INDEX IF NOT EXISTS idx_wase_ious_lender    ON wase_ious(lender_id);
CREATE INDEX IF NOT EXISTS idx_wase_ious_borrower  ON wase_ious(borrower_id);
CREATE INDEX IF NOT EXISTS idx_wase_ious_status    ON wase_ious(status);
CREATE INDEX IF NOT EXISTS idx_wase_ious_due_date  ON wase_ious(due_date);

-- ══════════════════════════════════════════════════════════════
-- 3. COLLECTIONS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS wase_collections (
  id                SERIAL PRIMARY KEY,
  creator_id        BIGINT NOT NULL REFERENCES wase_users(user_id),
  chat_id           BIGINT NOT NULL,               -- Telegram group chat ID
  title             TEXT NOT NULL,
  amount_per_person DECIMAL,                        -- Fixed per-person amount (nullable)
  target_amount     DECIMAL,                        -- Total target (nullable)
  status            TEXT NOT NULL DEFAULT 'active'
                      CHECK (status IN ('active', 'completed', 'cancelled')),
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_wase_collections_chat   ON wase_collections(chat_id);
CREATE INDEX IF NOT EXISTS idx_wase_collections_status ON wase_collections(status);

-- ══════════════════════════════════════════════════════════════
-- 4. CONTRIBUTIONS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS wase_contributions (
  id            SERIAL PRIMARY KEY,
  collection_id INT NOT NULL REFERENCES wase_collections(id),
  user_id       BIGINT NOT NULL REFERENCES wase_users(user_id),
  amount        DECIMAL,
  status        TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'paid')),
  confirmed_at  TIMESTAMPTZ,

  UNIQUE(collection_id, user_id)
);

-- ══════════════════════════════════════════════════════════════
-- 5. TRUST EVENTS
-- ══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS wase_trust_events (
  id           SERIAL PRIMARY KEY,
  user_id      BIGINT NOT NULL REFERENCES wase_users(user_id),
  event_type   TEXT NOT NULL,              -- iou_repaid | iou_overdue | collection_paid | iou_created | iou_early
  score_delta  DECIMAL NOT NULL,
  reference_id INT,                        -- IOU or collection ID
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_wase_trust_events_user ON wase_trust_events(user_id);
CREATE INDEX IF NOT EXISTS idx_wase_trust_events_type ON wase_trust_events(event_type);

-- ══════════════════════════════════════════════════════════════
-- 6. RLS — Service role only (bot + API use service key)
-- ══════════════════════════════════════════════════════════════

ALTER TABLE wase_users         ENABLE ROW LEVEL SECURITY;
ALTER TABLE wase_ious          ENABLE ROW LEVEL SECURITY;
ALTER TABLE wase_collections   ENABLE ROW LEVEL SECURITY;
ALTER TABLE wase_contributions ENABLE ROW LEVEL SECURITY;
ALTER TABLE wase_trust_events  ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS automatically.
-- No anon/public policies needed — all access goes through bot or Vercel API (both use service key).

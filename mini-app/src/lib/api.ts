/**
 * API client for Wase Mini App.
 * All requests include Telegram initData for authentication.
 */

import { getInitData } from "./telegram";

const API_BASE = "/api";

async function request<T>(endpoint: string): Promise<T> {
  const initData = getInitData();

  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "X-Telegram-Init-Data": initData,
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || `API error: ${res.status}`);
  }

  return res.json();
}

// ── Types ─────────────────────────────────────────────────────

export interface DashboardData {
  owed_to_user: number;
  user_owes: number;
  net: number;
  overdue_count: number;
  completed_count: number;
  contribution_count: number;
  active_ious: {
    as_lender: IOU[];
    as_borrower: IOU[];
  };
}

export interface IOU {
  id: number;
  lender_id: number;
  borrower_id: number;
  amount: number;
  description: string | null;
  due_date: string | null;
  status: string;
  created_at: string;
  other_name?: string;
}

export interface ScoreData {
  score: number;
  tier: string;
  components: {
    repaid: { score: number; max: number; done: number; total: number };
    collections: { score: number; max: number; count: number };
    connections: { score: number; max: number; count: number };
    history: { score: number; max: number; has_history: boolean };
    overdue: { penalty: number; count: number };
  };
}

export interface CollectionData {
  id: number;
  title: string;
  amount_per_person: number | null;
  target_amount: number | null;
  status: string;
  created_at: string;
  contributions: {
    user_id: number;
    name: string;
    amount: number | null;
    status: string;
  }[];
  paid_count: number;
  total_amount: number;
}

// ── API Calls ─────────────────────────────────────────────────

export function fetchDashboard(): Promise<DashboardData> {
  return request<DashboardData>("/dashboard");
}

export function fetchScore(): Promise<ScoreData> {
  return request<ScoreData>("/score");
}

export function fetchCollection(id: number): Promise<CollectionData> {
  return request<CollectionData>(`/collection?id=${id}`);
}

import type { VercelRequest, VercelResponse } from "@vercel/node";
import { createHmac } from "crypto";
import { createClient } from "@supabase/supabase-js";

// ── Auth (same pattern as dashboard.ts) ───────────────────────

function verifyInitData(initDataRaw: string): { id: number } | null {
  try {
    const botToken = process.env.BOT_TOKEN;
    if (!botToken) return null;

    const params = new URLSearchParams(initDataRaw);
    const hash = params.get("hash");
    if (!hash) return null;
    params.delete("hash");

    const dataCheckString = Array.from(params.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}=${v}`)
      .join("\n");

    const secretKey = createHmac("sha256", "WebAppData").update(botToken).digest();
    const computed = createHmac("sha256", secretKey).update(dataCheckString).digest("hex");
    if (computed !== hash) return null;

    const userStr = params.get("user");
    if (!userStr) return null;
    const user = JSON.parse(userStr);

    const authDate = parseInt(params.get("auth_date") || "0", 10);
    if (Math.floor(Date.now() / 1000) - authDate > 86400) return null;

    return { id: user.id };
  } catch {
    return null;
  }
}

function getSupabase() {
  return createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_KEY!);
}

// ── Handler ───────────────────────────────────────────────────

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const initData = req.headers["x-telegram-init-data"] as string;
  if (!initData) return res.status(401).json({ error: "Missing init data" });

  const user = verifyInitData(initData);
  if (!user) return res.status(401).json({ error: "Invalid init data" });

  const supabase = getSupabase();
  const userId = user.id;
  const today = new Date().toISOString().split("T")[0];

  // IOUs as borrower (confirmed + completed)
  const { count: totalAsBorrower } = await supabase
    .from("wase_ious")
    .select("id", { count: "exact", head: true })
    .eq("borrower_id", userId)
    .in("status", ["confirmed", "completed"]);

  const { count: repaid } = await supabase
    .from("wase_ious")
    .select("id", { count: "exact", head: true })
    .eq("borrower_id", userId)
    .eq("status", "completed");

  // Collection contributions
  const { count: contributions } = await supabase
    .from("wase_contributions")
    .select("id", { count: "exact", head: true })
    .eq("user_id", userId)
    .eq("status", "paid");

  // Unique connections
  const { data: asLender } = await supabase
    .from("wase_ious")
    .select("borrower_id")
    .eq("lender_id", userId);
  const { data: asBorrowerData } = await supabase
    .from("wase_ious")
    .select("lender_id")
    .eq("borrower_id", userId);

  const uniquePeople = new Set<number>();
  (asLender || []).forEach((i) => uniquePeople.add(i.borrower_id));
  (asBorrowerData || []).forEach((i) => uniquePeople.add(i.lender_id));

  const hasHistory = (totalAsBorrower || 0) > 0 || (asLender || []).length > 0;

  // Overdue IOUs
  const { data: overdueData } = await supabase
    .from("wase_ious")
    .select("id")
    .eq("borrower_id", userId)
    .eq("status", "confirmed")
    .lt("due_date", today);

  const overdueCount = (overdueData || []).length;

  // Calculate score components
  const total = totalAsBorrower || 0;
  const done = repaid || 0;
  const contribCount = contributions || 0;
  const connections = uniquePeople.size;

  const repaidScore = total > 0 ? Math.round((done / total) * 40) : 0;
  const collectScore = Math.min(contribCount * 3, 30);
  const connectScore = Math.min(connections * 3, 20);
  const historyScore = hasHistory ? 10 : 0;
  const overduePenalty = overdueCount * 5;

  const rawScore = repaidScore + collectScore + connectScore + historyScore - overduePenalty;
  const score = Math.max(0, Math.min(100, rawScore));

  // Tier
  const tiers = [
    { min: 85, label: "💎 በጣም ጥሩ" },
    { min: 60, label: "🏆 አስተማማኝ" },
    { min: 30, label: "⭐ እየተሻሻለ" },
    { min: 0, label: "🌟 አዲስ" },
  ];
  const tier = tiers.find((t) => score >= t.min)!.label;

  return res.status(200).json({
    score,
    tier,
    components: {
      repaid: { score: repaidScore, max: 40, done, total },
      collections: { score: collectScore, max: 30, count: contribCount },
      connections: { score: connectScore, max: 20, count: connections },
      history: { score: historyScore, max: 10, has_history: hasHistory },
      overdue: { penalty: overduePenalty, count: overdueCount },
    },
  });
}

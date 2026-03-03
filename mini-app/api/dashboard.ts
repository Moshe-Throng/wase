import type { VercelRequest, VercelResponse } from "@vercel/node";
import { createHmac } from "crypto";
import { createClient } from "@supabase/supabase-js";

// ── Auth ──────────────────────────────────────────────────────

interface TelegramUser {
  id: number;
  first_name: string;
  username?: string;
}

function verifyInitData(initDataRaw: string): TelegramUser | null {
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

    const user: TelegramUser = JSON.parse(userStr);
    const authDate = parseInt(params.get("auth_date") || "0", 10);
    const now = Math.floor(Date.now() / 1000);
    if (now - authDate > 86400) return null;

    return user;
  } catch {
    return null;
  }
}

// ── Supabase ──────────────────────────────────────────────────

function getSupabase() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_KEY!
  );
}

// ── Handler ───────────────────────────────────────────────────

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const initData = req.headers["x-telegram-init-data"] as string;
  if (!initData) {
    return res.status(401).json({ error: "Missing init data" });
  }

  const user = verifyInitData(initData);
  if (!user) {
    return res.status(401).json({ error: "Invalid init data" });
  }

  const supabase = getSupabase();
  const userId = user.id;

  // Fetch active IOUs where user is lender
  const { data: asLender } = await supabase
    .from("wase_ious")
    .select("*")
    .eq("lender_id", userId)
    .neq("status", "completed")
    .order("created_at", { ascending: false });

  // Fetch active IOUs where user is borrower
  const { data: asBorrower } = await supabase
    .from("wase_ious")
    .select("*")
    .eq("borrower_id", userId)
    .neq("status", "completed")
    .order("created_at", { ascending: false });

  const lenderIOUs = asLender || [];
  const borrowerIOUs = asBorrower || [];

  // Resolve other party names
  const otherIds = new Set<number>();
  lenderIOUs.forEach((i) => otherIds.add(i.borrower_id));
  borrowerIOUs.forEach((i) => otherIds.add(i.lender_id));

  const nameMap: Record<number, string> = {};
  if (otherIds.size > 0) {
    const { data: users } = await supabase
      .from("wase_users")
      .select("user_id, first_name, username")
      .in("user_id", Array.from(otherIds));

    (users || []).forEach((u) => {
      nameMap[u.user_id] = u.first_name || `@${u.username}` || String(u.user_id);
    });
  }

  // Calculate totals
  const owed_to_user = lenderIOUs
    .filter((i) => ["pending", "confirmed"].includes(i.status))
    .reduce((sum, i) => sum + Number(i.amount), 0);

  const user_owes = borrowerIOUs
    .filter((i) => ["pending", "confirmed"].includes(i.status))
    .reduce((sum, i) => sum + Number(i.amount), 0);

  const today = new Date().toISOString().split("T")[0];
  const overdue_count = [...lenderIOUs, ...borrowerIOUs].filter(
    (i) => i.due_date && i.due_date < today && ["pending", "confirmed"].includes(i.status)
  ).length;

  // Lifetime stats
  const { count: completed_count } = await supabase
    .from("wase_ious")
    .select("id", { count: "exact", head: true })
    .eq("status", "completed")
    .or(`lender_id.eq.${userId},borrower_id.eq.${userId}`);

  const { count: contribution_count } = await supabase
    .from("wase_contributions")
    .select("id", { count: "exact", head: true })
    .eq("user_id", userId)
    .eq("status", "paid");

  return res.status(200).json({
    owed_to_user,
    user_owes,
    net: owed_to_user - user_owes,
    overdue_count,
    completed_count: completed_count || 0,
    contribution_count: contribution_count || 0,
    active_ious: {
      as_lender: lenderIOUs.map((i) => ({
        ...i,
        other_name: nameMap[i.borrower_id] || String(i.borrower_id),
      })),
      as_borrower: borrowerIOUs.map((i) => ({
        ...i,
        other_name: nameMap[i.lender_id] || String(i.lender_id),
      })),
    },
  });
}

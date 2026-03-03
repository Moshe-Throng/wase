import type { VercelRequest, VercelResponse } from "@vercel/node";
import { createHmac } from "crypto";
import { createClient } from "@supabase/supabase-js";

// ── Auth ──────────────────────────────────────────────────────

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

  const collectionId = parseInt(req.query.id as string);
  if (!collectionId || isNaN(collectionId)) {
    return res.status(400).json({ error: "Missing collection id" });
  }

  const supabase = getSupabase();

  // Fetch collection
  const { data: collection } = await supabase
    .from("wase_collections")
    .select("*")
    .eq("id", collectionId)
    .single();

  if (!collection) {
    return res.status(404).json({ error: "Collection not found" });
  }

  // Fetch contributions
  const { data: contributions } = await supabase
    .from("wase_contributions")
    .select("*")
    .eq("collection_id", collectionId)
    .order("confirmed_at");

  // Resolve names
  const userIds = (contributions || []).map((c) => c.user_id);
  const nameMap: Record<number, string> = {};

  if (userIds.length > 0) {
    const { data: users } = await supabase
      .from("wase_users")
      .select("user_id, first_name, username")
      .in("user_id", userIds);

    (users || []).forEach((u) => {
      nameMap[u.user_id] = u.first_name || `@${u.username}` || String(u.user_id);
    });
  }

  const paidContribs = (contributions || []).filter((c) => c.status === "paid");
  const totalAmount = paidContribs.reduce((sum, c) => sum + Number(c.amount || 0), 0);

  return res.status(200).json({
    id: collection.id,
    title: collection.title,
    amount_per_person: collection.amount_per_person,
    target_amount: collection.target_amount,
    status: collection.status,
    created_at: collection.created_at,
    contributions: (contributions || []).map((c) => ({
      user_id: c.user_id,
      name: nameMap[c.user_id] || String(c.user_id),
      amount: c.amount,
      status: c.status,
    })),
    paid_count: paidContribs.length,
    total_amount: totalAmount,
  });
}

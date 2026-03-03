import { useEffect, useState } from "react";
import type { TelegramUser } from "../lib/telegram";
import { fetchScore, type ScoreData } from "../lib/api";
import ScoreRing from "../components/ScoreRing";
import ProgressBar from "../components/ProgressBar";

interface Props {
  user: TelegramUser;
}

export default function TrustScore({ user }: Props) {
  const [data, setData] = useState<ScoreData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchScore()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-wase-hint">ይጫኑ...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-wase-danger">
        <p>❌ {error}</p>
      </div>
    );
  }

  if (!data) return null;

  const c = data.components;

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div className="text-center pt-2">
        <h1 className="text-lg font-bold">🛡 የአስተማማኝነት ነጥብ</h1>
        <p className="text-wase-hint text-sm">{user.first_name}</p>
      </div>

      {/* Score Ring */}
      <div className="flex justify-center relative">
        <ScoreRing score={data.score} tier={data.tier} />
      </div>

      {/* Component Breakdown */}
      <div className="space-y-4 bg-wase-secondary-bg rounded-2xl p-4">
        {/* IOUs Repaid */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm">💸 የተከፈሉ እዳዎች</span>
            <span className="text-xs text-wase-hint">
              {c.repaid.done}/{c.repaid.total}
            </span>
          </div>
          <ProgressBar value={c.repaid.score} max={c.repaid.max} color="bg-wase-success" />
        </div>

        {/* Collection Contributions */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm">💰 ማሰባሰብ ተሳትፎ</span>
            <span className="text-xs text-wase-hint">{c.collections.count}</span>
          </div>
          <ProgressBar value={c.collections.score} max={c.collections.max} color="bg-wase-accent" />
        </div>

        {/* Connections */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm">👥 ግንኙነቶች</span>
            <span className="text-xs text-wase-hint">{c.connections.count}</span>
          </div>
          <ProgressBar value={c.connections.score} max={c.connections.max} color="bg-wase-primary" />
        </div>

        {/* History */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm">📋 ታሪክ</span>
            <span className="text-xs text-wase-hint">
              {c.history.has_history ? "✅" : "—"}
            </span>
          </div>
          <ProgressBar value={c.history.score} max={c.history.max} color="bg-gray-400" />
        </div>

        {/* Overdue Penalty */}
        {c.overdue.count > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3">
            <p className="text-sm text-red-700">
              ⚠️ የዘገየ ቅጣት: -{c.overdue.penalty} ({c.overdue.count} እዳዎች)
            </p>
          </div>
        )}
      </div>

      {/* Improvement Tip */}
      <div className="bg-wase-secondary-bg rounded-xl p-3 text-center">
        <p className="text-xs text-wase-hint">
          💡 ነጥብህን ለማሻሻል: እዳዎችን በወቅቱ ክፈል፣ ማሰባሰብ ላይ ተሳተፍ
        </p>
      </div>
    </div>
  );
}

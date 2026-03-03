import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { TelegramUser } from "../lib/telegram";
import { fetchCollection, type CollectionData } from "../lib/api";
import ProgressBar from "../components/ProgressBar";

interface Props {
  user: TelegramUser;
}

function birr(amount: number): string {
  if (amount === Math.floor(amount)) {
    return `${amount.toLocaleString()} ብር`;
  }
  return `${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} ብር`;
}

export default function Collection({ user }: Props) {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<CollectionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchCollection(parseInt(id))
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

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

  const target = data.target_amount || (data.amount_per_person ? data.amount_per_person * data.contributions.length : 0);

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="text-center pt-2 pb-2">
        <h1 className="text-lg font-bold">💰 ማሰባሰብ #{data.id}</h1>
        <p className="text-xl font-semibold mt-1">{data.title}</p>
        {data.amount_per_person && (
          <p className="text-sm text-wase-hint mt-1">{birr(data.amount_per_person)} ለእያንዳንዱ</p>
        )}
      </div>

      {/* Progress */}
      <div className="bg-wase-secondary-bg rounded-2xl p-4">
        <div className="flex justify-between items-end mb-3">
          <div>
            <p className="text-2xl font-bold text-wase-primary">{birr(data.total_amount)}</p>
            <p className="text-xs text-wase-hint">ተሰብስቧል</p>
          </div>
          {target > 0 && (
            <div className="text-right">
              <p className="text-sm text-wase-hint">ከ {birr(target)}</p>
            </div>
          )}
        </div>

        {target > 0 && (
          <ProgressBar value={data.total_amount} max={target} color="bg-wase-success" />
        )}

        <p className="text-center text-sm text-wase-hint mt-3">
          {data.paid_count} ሰዎች ከፍለዋል
        </p>
      </div>

      {/* Contributors List */}
      <div>
        <h2 className="text-sm font-semibold text-wase-hint mb-2">ተሳታፊዎች</h2>
        <div className="space-y-1">
          {data.contributions.map((c) => (
            <div
              key={c.user_id}
              className={`flex items-center justify-between p-3 rounded-xl ${
                c.status === "paid" ? "bg-green-50" : "bg-wase-secondary-bg"
              }`}
            >
              <div className="flex items-center gap-2">
                <span>{c.status === "paid" ? "✅" : "⬜"}</span>
                <span className="text-sm font-medium">{c.name}</span>
              </div>
              {c.amount && (
                <span className="text-sm text-wase-hint">{birr(c.amount)}</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Complete badge */}
      {data.status === "completed" && (
        <div className="text-center py-4">
          <p className="text-2xl">🎉</p>
          <p className="text-sm font-semibold text-wase-success">ማሰባሰብ ተጠናቋል!</p>
        </div>
      )}
    </div>
  );
}

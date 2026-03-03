import { useEffect, useState } from "react";
import type { TelegramUser } from "../lib/telegram";
import { fetchDashboard, type DashboardData, type IOU } from "../lib/api";

interface Props {
  user: TelegramUser;
}

function birr(amount: number): string {
  if (amount === Math.floor(amount)) {
    return `${amount.toLocaleString()} ብር`;
  }
  return `${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} ብር`;
}

const statusLabels: Record<string, string> = {
  pending: "⏳ በመጠበቅ",
  confirmed: "✅ ተረጋግጧል",
  completed: "🎉 ተከፍሏል",
  disputed: "⚠️ ተቃውሟል",
};

export default function Dashboard({ user }: Props) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard()
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

  const net = data.net;

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="text-center pt-2 pb-4">
        <h1 className="text-2xl font-bold">✦ ዋሴ</h1>
        <p className="text-wase-hint text-sm">{user.first_name}</p>
      </div>

      {/* Net Position Card */}
      <div className="bg-wase-secondary-bg rounded-2xl p-5">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-wase-hint mb-1">💚 የሚያበድሩህ</p>
            <p className="text-lg font-semibold text-wase-success">{birr(data.owed_to_user)}</p>
          </div>
          <div>
            <p className="text-xs text-wase-hint mb-1">🔴 የምታበድር</p>
            <p className="text-lg font-semibold text-wase-danger">{birr(data.user_owes)}</p>
          </div>
        </div>

        <div className="border-t border-gray-300 pt-3">
          <p className="text-sm text-wase-hint">ጠቅላላ</p>
          <p className={`text-xl font-bold ${net >= 0 ? "text-wase-success" : "text-wase-danger"}`}>
            {net >= 0 ? "+" : ""}{birr(Math.abs(net))}
          </p>
        </div>
      </div>

      {/* Overdue Warning */}
      {data.overdue_count > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-2">
          <span className="text-lg">⚠️</span>
          <p className="text-sm text-red-700">
            {data.overdue_count} እዳዎች ቀናቸው አልፏል
          </p>
        </div>
      )}

      {/* Stats Row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-wase-secondary-bg rounded-xl p-3 text-center">
          <p className="text-2xl font-bold text-wase-text">{data.completed_count}</p>
          <p className="text-xs text-wase-hint">✅ ተጠናቅቀዋል</p>
        </div>
        <div className="bg-wase-secondary-bg rounded-xl p-3 text-center">
          <p className="text-2xl font-bold text-wase-text">{data.contribution_count}</p>
          <p className="text-xs text-wase-hint">💰 ማሰባሰብ</p>
        </div>
      </div>

      {/* Active IOUs */}
      {(data.active_ious.as_lender.length > 0 || data.active_ious.as_borrower.length > 0) && (
        <div>
          <h2 className="text-sm font-semibold text-wase-hint mb-2">ንቁ እዳዎች</h2>

          {data.active_ious.as_lender.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-wase-success mb-1">💚 አበድረሃል</p>
              {data.active_ious.as_lender.map((iou) => (
                <IOUCard key={iou.id} iou={iou} />
              ))}
            </div>
          )}

          {data.active_ious.as_borrower.length > 0 && (
            <div>
              <p className="text-xs text-wase-danger mb-1">🔴 ትበደራለህ</p>
              {data.active_ious.as_borrower.map((iou) => (
                <IOUCard key={iou.id} iou={iou} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {data.active_ious.as_lender.length === 0 &&
        data.active_ious.as_borrower.length === 0 && (
          <div className="text-center py-8 text-wase-hint">
            <p className="text-3xl mb-2">✨</p>
            <p>ምንም ንቁ እዳ የለም!</p>
          </div>
        )}
    </div>
  );
}

function IOUCard({ iou }: { iou: IOU }) {
  const isOverdue =
    iou.due_date && new Date(iou.due_date) < new Date() && iou.status !== "completed";

  return (
    <div
      className={`bg-wase-bg border rounded-xl p-3 mb-2 ${
        isOverdue ? "border-red-300" : "border-gray-200"
      }`}
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="font-medium text-sm">
            #{iou.id} — {iou.other_name || "..."}
          </p>
          {iou.description && (
            <p className="text-xs text-wase-hint mt-0.5">{iou.description}</p>
          )}
        </div>
        <p className="font-semibold text-sm">{birr(iou.amount)}</p>
      </div>
      <div className="flex justify-between items-center mt-2">
        <span className="text-xs">{statusLabels[iou.status] || iou.status}</span>
        {iou.due_date && (
          <span className={`text-xs ${isOverdue ? "text-red-500 font-medium" : "text-wase-hint"}`}>
            📅 {new Date(iou.due_date).toLocaleDateString("en-GB")}
          </span>
        )}
      </div>
    </div>
  );
}

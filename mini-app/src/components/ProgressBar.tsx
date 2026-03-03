interface Props {
  value: number;
  max: number;
  color?: string;
  label?: string;
}

export default function ProgressBar({ value, max, color = "bg-wase-primary", label }: Props) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-xs text-wase-hint mb-1">
          <span>{label}</span>
          <span>{Math.round(pct)}%</span>
        </div>
      )}
      <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full animate-fill ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

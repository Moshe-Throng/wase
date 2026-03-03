interface Props {
  score: number;
  tier: string;
  size?: number;
}

export default function ScoreRing({ score, tier, size = 160 }: Props) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  // Color based on score
  const getColor = () => {
    if (score >= 85) return "#10B981"; // Excellent — green
    if (score >= 60) return "#0D9488"; // Trusted — teal
    if (score >= 30) return "#F59E0B"; // Rising — amber
    return "#8E8E93";                  // New — gray
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="10"
        />
        {/* Score ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
      </svg>
      {/* Score text centered on ring */}
      <div className="absolute flex flex-col items-center justify-center" style={{ width: size, height: size }}>
        <span className="text-4xl font-bold text-wase-text">{score}</span>
        <span className="text-sm text-wase-hint">{tier}</span>
      </div>
    </div>
  );
}

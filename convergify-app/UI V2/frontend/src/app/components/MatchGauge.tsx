import { useEffect, useState } from "react";

interface MatchGaugeProps {
  score: number;
  size?: number;
}

export function MatchGauge({ score, size = 180 }: MatchGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (animatedScore / 100) * circumference;
  const dashOffset = circumference - progress;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 300);
    return () => clearTimeout(timer);
  }, [score]);

  const getColor = () => {
    if (score >= 80) return "#22C55E";
    if (score >= 60) return "#2563EB";
    if (score >= 40) return "#F59E0B";
    return "#EF4444";
  };

  const getLabel = () => {
    if (score >= 80) return "Strong Match";
    if (score >= 60) return "Good Match";
    if (score >= 40) return "Moderate";
    return "Needs Work";
  };

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E2E8F0"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: "stroke-dashoffset 1.5s ease-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="tabular-nums"
          style={{ fontSize: size * 0.22, color: getColor(), fontFamily: "Inter, sans-serif" }}
        >
          {animatedScore}%
        </span>
        <span className="text-xs text-[#64748B] mt-0.5">{getLabel()}</span>
      </div>
    </div>
  );
}

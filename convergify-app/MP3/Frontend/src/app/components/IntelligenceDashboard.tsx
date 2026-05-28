import { useState } from 'react';
import { ChevronDown, ChevronUp, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { AnalysisResult, SkillMatch } from '@/app/data/mockAnalysis';
import { Button } from '@/app/components/ui/button';
import { CircularGauge } from '@/app/components/ui/circular-gauge';
import { InfoTooltip } from '@/app/components/ui/info-tooltip';

interface IntelligenceDashboardProps {
  data: AnalysisResult;
  onBack: () => void;
}

function SkillCard({ skill }: { skill: SkillMatch }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getBorderColor = () => {
    if (skill.matchType === 'strong') return 'var(--success-green)';
    if (skill.matchType === 'foundational') return 'var(--warning-amber)';
    return 'var(--critical-red)';
  };

  const getIcon = () => {
    if (skill.matchType === 'strong') return <CheckCircle2 className="w-5 h-5" />;
    if (skill.matchType === 'foundational') return <TrendingUp className="w-5 h-5" />;
    return <AlertTriangle className="w-5 h-5" />;
  };

  const getBadgeLabel = () => {
    if (skill.matchType === 'strong') return 'Match';
    if (skill.matchType === 'foundational') return 'Foundational';
    return 'Critical Gap';
  };

  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-lg border-l-4 border-r border-t border-b overflow-hidden transition-all"
      style={{
        borderLeftColor: getBorderColor(),
        borderRightColor: '#E5E7EB',
        borderTopColor: '#E5E7EB',
        borderBottomColor: '#E5E7EB',
      }}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-5 flex items-center gap-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        {/* Icon */}
        <div style={{ color: getBorderColor() }}>
          {getIcon()}
        </div>

        {/* Skill Name */}
        <div className="flex-1 min-w-0">
          <h4 className="font-bold text-base dark:text-white">{skill.skillName}</h4>
        </div>

        {/* Badge */}
        <div
          className="px-3 py-1 rounded text-xs font-semibold"
          style={{
            backgroundColor: `${getBorderColor()}15`,
            color: getBorderColor(),
          }}
        >
          {getBadgeLabel()}
        </div>

        {/* Experience */}
        <div className="text-sm text-gray-600 dark:text-gray-400 min-w-[100px] text-right">
          {skill.experienceLevel}
        </div>

        {/* Chevron */}
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-5 pb-5 pt-2 space-y-4 bg-gray-50 dark:bg-gray-750">
          {/* Bridge (Reasoning) */}
          <div>
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
              Analysis
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {skill.substitutionReasoning}
            </p>
          </div>

          {/* Snippet (Evidence) */}
          {skill.textSnippet && (
            <div>
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                Evidence from Resume
              </p>
              <div
                className="p-3 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                style={{ fontFamily: 'Monaco, Consolas, monospace' }}
              >
                <p className="text-xs text-gray-800 dark:text-gray-300 leading-relaxed">
                  "{skill.textSnippet}"
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SemanticGroupChart({ data }: { data: AnalysisResult }) {
  const mustHavePercentage = (data.mustHaveScore / 100) * 100;
  const niceToHavePercentage = (data.niceToHaveScore / 100) * 100;

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Must-Have Skills</span>
          <span className="text-sm font-semibold">{data.mustHaveScore}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{
              width: `${mustHavePercentage}%`,
              backgroundColor: 'var(--success-green)',
            }}
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Nice-to-Have Skills</span>
          <span className="text-sm font-semibold">{data.niceToHaveScore}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-1000"
            style={{
              width: `${niceToHavePercentage}%`,
              backgroundColor: 'var(--primary-blue)',
            }}
          />
        </div>
      </div>
    </div>
  );
}

export function IntelligenceDashboard({ data, onBack }: IntelligenceDashboardProps) {
  return (
    <div className="flex-1 flex bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Left Sidebar - Fit Score */}
      <div className="w-[400px] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-8 overflow-y-auto">
        <div className="space-y-8">
          {/* Hero Score with Circular Gauge */}
          <div
            className="rounded-xl p-8 text-center bg-blue-50 dark:bg-blue-900/20"
          >
            <div className="flex items-center justify-center gap-1 mb-4">
              <p className="text-sm font-semibold text-gray-600 dark:text-gray-300">
                OVERALL MARKET FIT
              </p>
              <InfoTooltip content="This score represents how well your resume matches the requirements across all analyzed jobs. Higher scores indicate stronger alignment with market demands." />
            </div>
            <div className="flex justify-center mb-4">
              <CircularGauge 
                value={data.overallScore} 
                size={180}
                strokeWidth={14}
                color="var(--primary-blue)"
              />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Based on {data.jobsAnalyzed} job{data.jobsAnalyzed > 1 ? 's' : ''}
            </p>
          </div>

          {/* Semantic Groups */}
          <div>
            <h3 className="font-semibold mb-4 dark:text-white">Skill Breakdown</h3>
            <SemanticGroupChart data={data} />
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center border border-green-200 dark:border-green-800">
              <p className="text-2xl font-bold" style={{ color: 'var(--success-green)' }}>
                {data.skills.filter((s) => s.matchType === 'strong').length}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Strong Matches</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 text-center border border-red-200 dark:border-red-800">
              <p className="text-2xl font-bold" style={{ color: 'var(--critical-red)' }}>
                {data.skills.filter((s) => s.matchType === 'missing').length}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Gaps Found</p>
            </div>
          </div>

          {/* Back Button */}
          <Button variant="outline" onClick={onBack} className="w-full">
            Back to Job Pool
          </Button>
        </div>
      </div>

      {/* Right Side - Evidence Feed */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[900px] mx-auto p-4 sm:p-6 lg:p-8 xl:p-12">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-semibold mb-3 dark:text-white">Market Intelligence Report</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Detailed analysis of your skill alignment across the market
            </p>
          </div>

          {/* Must-Have Skills */}
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-xl font-semibold dark:text-white">Must-Have Skills</h2>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-medium text-gray-600 dark:text-gray-300">
                {data.skills.filter((s) => s.category === 'must-have').length} skills
              </span>
            </div>
            <div className="space-y-3">
              {data.skills
                .filter((s) => s.category === 'must-have')
                .map((skill) => (
                  <SkillCard key={skill.id} skill={skill} />
                ))}
            </div>
          </div>

          {/* Nice-to-Have Skills */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-xl font-semibold dark:text-white">Nice-to-Have Skills</h2>
              <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm font-medium text-gray-600 dark:text-gray-300">
                {data.skills.filter((s) => s.category === 'nice-to-have').length} skills
              </span>
            </div>
            <div className="space-y-3">
              {data.skills
                .filter((s) => s.category === 'nice-to-have')
                .map((skill) => (
                  <SkillCard key={skill.id} skill={skill} />
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
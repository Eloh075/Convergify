import { useState, useMemo } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Award, 
  BookOpen, 
  DollarSign, 
  MapPin, 
  Clock, 
  Star, 
  ArrowUp, 
  ArrowDown, 
  Minus,
  Download,
  Share2,
  Eye,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Info,
  ExternalLink,
  Filter,
  Search,
  SortAsc,
  SortDesc,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Badge } from '@/app/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Progress } from '@/app/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/components/ui/dropdown-menu';
import { 
  useAnalysisResults,
  useAnalysis
} from '@/hooks/useApi';
import type { 
  AnalysisResults as AnalysisResultsType,
  SkillGap,
  SkillOverlap,
  MarketInsights,
  Recommendation,
  CareerPathSuggestion
} from '@/types/api';

interface AnalysisResultsProps {
  analysisId: string;
  onExport?: (format: 'pdf' | 'json') => void;
  onOptimizeResume?: () => void;
  onNewAnalysis?: () => void;
}

// Skill Gap Visualization Component with Priority Tiers
function SkillGapAnalysis({ skillGaps }: { skillGaps: SkillGap[] }) {
  const [sortBy, setSortBy] = useState<'importance' | 'demand' | 'alphabetical'>('importance');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterImportance, setFilterImportance] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [expandedTiers, setExpandedTiers] = useState<Set<'high' | 'medium' | 'low'>>(
    new Set(['high', 'medium']) // Low tier collapsed by default
  );

  // Debounce search query (300ms delay)
  useMemo(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Organize gaps into priority tiers based on importance value
  const organizedGaps = useMemo(() => {
    const high: SkillGap[] = [];
    const medium: SkillGap[] = [];
    const low: SkillGap[] = [];

    skillGaps.forEach(gap => {
      if (gap.importance >= 0.8) {
        high.push(gap);
      } else if (gap.importance >= 0.6) {
        medium.push(gap);
      } else {
        low.push(gap);
      }
    });

    return { high, medium, low };
  }, [skillGaps]);

  // Filter and sort gaps
  const getFilteredAndSortedGaps = (gaps: SkillGap[]) => {
    let filtered = gaps.filter(gap => {
      const matchesSearch = gap.skill.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
                           (gap.category && gap.category.toLowerCase().includes(debouncedSearchQuery.toLowerCase()));
      const matchesImportance = filterImportance === 'all' || gap.importance_level === filterImportance;
      return matchesSearch && matchesImportance;
    });

    return filtered.sort((a, b) => {
      let aValue: number, bValue: number;
      
      switch (sortBy) {
        case 'importance':
          aValue = a.importance;
          bValue = b.importance;
          break;
        case 'demand':
          aValue = a.market_demand;
          bValue = b.market_demand;
          break;
        case 'alphabetical':
          return sortOrder === 'asc' 
            ? a.skill.localeCompare(b.skill)
            : b.skill.localeCompare(a.skill);
        default:
          aValue = a.importance;
          bValue = b.importance;
      }
      
      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    });
  };

  const filteredTiers = useMemo(() => ({
    high: getFilteredAndSortedGaps(organizedGaps.high),
    medium: getFilteredAndSortedGaps(organizedGaps.medium),
    low: getFilteredAndSortedGaps(organizedGaps.low)
  }), [organizedGaps, debouncedSearchQuery, filterImportance, sortBy, sortOrder]);

  const totalFilteredGaps = filteredTiers.high.length + filteredTiers.medium.length + filteredTiers.low.length;

  const toggleTier = (tier: 'high' | 'medium' | 'low') => {
    const newExpanded = new Set(expandedTiers);
    if (newExpanded.has(tier)) {
      newExpanded.delete(tier);
    } else {
      newExpanded.add(tier);
    }
    setExpandedTiers(newExpanded);
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 0.8) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
    if (importance >= 0.6) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
    return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
  };

  const getTierConfig = (tier: 'high' | 'medium' | 'low') => {
    switch (tier) {
      case 'high':
        return {
          label: 'High Priority',
          description: 'Critical skills (importance ≥ 80%)',
          color: 'border-red-300 dark:border-red-700',
          bgColor: 'bg-red-50 dark:bg-red-900/10',
          badgeColor: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
          icon: <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
        };
      case 'medium':
        return {
          label: 'Medium Priority',
          description: 'Important skills (60% ≤ importance < 80%)',
          color: 'border-yellow-300 dark:border-yellow-700',
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/10',
          badgeColor: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
          icon: <Info className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
        };
      case 'low':
        return {
          label: 'Low Priority',
          description: 'Nice-to-have skills (importance < 60%)',
          color: 'border-green-300 dark:border-green-700',
          bgColor: 'bg-green-50 dark:bg-green-900/10',
          badgeColor: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
          icon: <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
        };
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold dark:text-white">Skill Gaps</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Skills organized by priority level
          </p>
        </div>
        <Badge variant="secondary">{totalFilteredGaps} gaps identified</Badge>
      </div>

      {/* Search, Filter, and Sort Controls */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <Input
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select value={filterImportance} onValueChange={setFilterImportance}>
          <SelectTrigger className="w-[180px]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Importance</SelectItem>
            <SelectItem value="Must-have">Must-have</SelectItem>
            <SelectItem value="Nice-to-have">Nice-to-have</SelectItem>
            <SelectItem value="Preferred">Preferred</SelectItem>
          </SelectContent>
        </Select>

        <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
          const [field, order] = value.split('_');
          setSortBy(field as 'importance' | 'demand' | 'alphabetical');
          setSortOrder(order as 'asc' | 'desc');
        }}>
          <SelectTrigger className="w-[200px]">
            {sortOrder === 'desc' ? <SortDesc className="w-4 h-4 mr-2" /> : <SortAsc className="w-4 h-4 mr-2" />}
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="importance_desc">Importance (High to Low)</SelectItem>
            <SelectItem value="importance_asc">Importance (Low to High)</SelectItem>
            <SelectItem value="demand_desc">Demand (High to Low)</SelectItem>
            <SelectItem value="demand_asc">Demand (Low to High)</SelectItem>
            <SelectItem value="alphabetical_asc">Alphabetical (A-Z)</SelectItem>
            <SelectItem value="alphabetical_desc">Alphabetical (Z-A)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Priority Tiers */}
      <div className="space-y-4">
        {(['high', 'medium', 'low'] as const).map(tier => {
          const config = getTierConfig(tier);
          const gaps = filteredTiers[tier];
          const isExpanded = expandedTiers.has(tier);

          if (gaps.length === 0) return null;

          return (
            <Card key={tier} className={`border-2 ${config.color}`}>
              {/* Tier Header */}
              <div
                className={`p-4 ${config.bgColor} cursor-pointer hover:opacity-80 transition-opacity`}
                onClick={() => toggleTier(tier)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <ChevronRight 
                      className={`w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                    />
                    {config.icon}
                    <div>
                      <h4 className="font-semibold text-lg dark:text-white">{config.label}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{config.description}</p>
                    </div>
                  </div>
                  <Badge className={config.badgeColor}>
                    {gaps.length} skill{gaps.length !== 1 ? 's' : ''}
                  </Badge>
                </div>
              </div>

              {/* Gap Cards */}
              {isExpanded && (
                <CardContent className="p-4 space-y-3">
                  {gaps.map((gap, index) => (
                    <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      {/* Gap Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h5 className="font-semibold dark:text-white">{gap.skill}</h5>
                            <Badge className={`text-xs ${getImportanceColor(gap.importance)}`}>
                              {gap.importance_level}
                            </Badge>
                            {gap.category && (
                              <Badge variant="outline" className="text-xs">
                                {gap.category}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600 dark:text-gray-300">Importance</div>
                          <div className="text-xl font-bold text-gray-900 dark:text-white">
                            {Math.round(gap.importance * 100)}%
                          </div>
                        </div>
                      </div>

                      {/* Market Demand */}
                      <div className="mb-3">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="text-gray-600 dark:text-gray-300">Market Demand</span>
                          <span className="font-medium dark:text-white">{Math.round(gap.market_demand * 100)}%</span>
                        </div>
                        <Progress value={gap.market_demand * 100} className="h-2" />
                      </div>

                      {/* Why This Matters */}
                      {gap.why_matters && (
                        <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                          <div className="flex items-start gap-2">
                            <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                            <div>
                              <div className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-1">
                                Why this matters
                              </div>
                              <p className="text-sm text-gray-700 dark:text-gray-300">
                                {gap.why_matters}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Jobs Requiring This Skill */}
                      {gap.jobs_requiring && gap.jobs_requiring.length > 0 && (
                        <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                          <div className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                            Required by {gap.jobs_requiring.length} job{gap.jobs_requiring.length !== 1 ? 's' : ''}
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {gap.jobs_requiring.slice(0, 5).map((job, jobIndex) => (
                              <Badge key={jobIndex} variant="outline" className="text-xs">
                                {job}
                              </Badge>
                            ))}
                            {gap.jobs_requiring.length > 5 && (
                              <Badge variant="outline" className="text-xs">
                                +{gap.jobs_requiring.length - 5} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      {/* Empty State */}
      {totalFilteredGaps === 0 && (
        <div className="text-center py-12">
          <Target className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">No skill gaps found matching your criteria</p>
        </div>
      )}
    </div>
  );
}

// Skill Matches Tab Component with Hierarchical Organization
function SkillMatchesTab({ skillMatches }: { skillMatches: SkillMatch[] }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterImportance, setFilterImportance] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'match' | 'demand' | 'importance'>('match');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  // Group skills by canonical_group
  const groupedSkills = useMemo(() => {
    const groups = new Map<string, SkillMatch[]>();
    
    skillMatches.forEach(skill => {
      const group = skill.canonical_group || 'Other';
      if (!groups.has(group)) {
        groups.set(group, []);
      }
      groups.get(group)!.push(skill);
    });
    
    return groups;
  }, [skillMatches]);

  // Calculate category-level metrics
  const categoryMetrics = useMemo(() => {
    const metrics = new Map<string, { demand: number; coverage: number }>();
    
    groupedSkills.forEach((skills, group) => {
      // Average demand across skills in this category
      const avgDemand = skills.reduce((sum, s) => sum + (s.market_demand || 0), 0) / skills.length;
      
      // Average match percentage as coverage
      const avgCoverage = skills.reduce((sum, s) => sum + (s.match_percentage || 0), 0) / skills.length;
      
      metrics.set(group, { demand: avgDemand * 100, coverage: avgCoverage });
    });
    
    return metrics;
  }, [groupedSkills]);

  // Filter and sort skills
  const filteredSkills = useMemo(() => {
    let filtered = skillMatches.filter(skill => {
      const matchesSearch = skill.skill.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           (skill.category && skill.category.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesImportance = filterImportance === 'all' || skill.importance_level === filterImportance;
      return matchesSearch && matchesImportance;
    });

    // Sort skills
    filtered.sort((a, b) => {
      let aValue: number, bValue: number;
      
      switch (sortBy) {
        case 'match':
          aValue = a.match_percentage || 0;
          bValue = b.match_percentage || 0;
          break;
        case 'demand':
          aValue = a.market_demand || 0;
          bValue = b.market_demand || 0;
          break;
        case 'importance':
          const importanceMap = { 'Must-have': 3, 'Nice-to-have': 2, 'Preferred': 1 };
          aValue = importanceMap[a.importance_level] || 0;
          bValue = importanceMap[b.importance_level] || 0;
          break;
        default:
          aValue = a.match_percentage || 0;
          bValue = b.match_percentage || 0;
      }
      
      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
    });

    return filtered;
  }, [skillMatches, searchQuery, filterImportance, sortBy, sortOrder]);

  // Regroup filtered skills
  const filteredGroupedSkills = useMemo(() => {
    const groups = new Map<string, SkillMatch[]>();
    
    filteredSkills.forEach(skill => {
      const group = skill.canonical_group || 'Other';
      if (!groups.has(group)) {
        groups.set(group, []);
      }
      groups.get(group)!.push(skill);
    });
    
    return groups;
  }, [filteredSkills]);

  // Pagination
  const groupsArray = Array.from(filteredGroupedSkills.entries());
  const totalPages = Math.ceil(groupsArray.length / itemsPerPage);
  const paginatedGroups = groupsArray.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const toggleGroup = (group: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(group)) {
      newExpanded.delete(group);
    } else {
      newExpanded.add(group);
    }
    setExpandedGroups(newExpanded);
  };

  const toggleEvidence = (skillKey: string) => {
    const newExpanded = new Set(expandedEvidence);
    if (newExpanded.has(skillKey)) {
      newExpanded.delete(skillKey);
    } else {
      newExpanded.add(skillKey);
    }
    setExpandedEvidence(newExpanded);
  };

  const getCoverageIndicator = (coverage: number) => {
    if (coverage > 60) {
      return { icon: <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />, label: 'Strong', color: 'text-green-600 dark:text-green-400' };
    } else if (coverage >= 30) {
      return { icon: <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />, label: 'Partial', color: 'text-yellow-600 dark:text-yellow-400' };
    } else {
      return { icon: <Info className="w-5 h-5 text-red-600 dark:text-red-400" />, label: 'Weak', color: 'text-red-600 dark:text-red-400' };
    }
  };

  const getImportanceColor = (level: string) => {
    switch (level) {
      case 'Must-have':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      case 'Nice-to-have':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'Preferred':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold dark:text-white">Skill Matches</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Skills organized by category with match details
          </p>
        </div>
        <Badge variant="secondary">{filteredSkills.length} matching skills</Badge>
      </div>

      {/* Search, Filter, and Sort Controls */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <Input
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            className="pl-10"
          />
        </div>

        <Select value={filterImportance} onValueChange={(value) => {
          setFilterImportance(value);
          setCurrentPage(1);
        }}>
          <SelectTrigger className="w-[180px]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Importance</SelectItem>
            <SelectItem value="Must-have">Must-have</SelectItem>
            <SelectItem value="Nice-to-have">Nice-to-have</SelectItem>
            <SelectItem value="Preferred">Preferred</SelectItem>
          </SelectContent>
        </Select>

        <Select value={`${sortBy}_${sortOrder}`} onValueChange={(value) => {
          const [field, order] = value.split('_');
          setSortBy(field as 'match' | 'demand' | 'importance');
          setSortOrder(order as 'asc' | 'desc');
        }}>
          <SelectTrigger className="w-[200px]">
            {sortOrder === 'desc' ? <SortDesc className="w-4 h-4 mr-2" /> : <SortAsc className="w-4 h-4 mr-2" />}
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="match_desc">Match % (High to Low)</SelectItem>
            <SelectItem value="match_asc">Match % (Low to High)</SelectItem>
            <SelectItem value="demand_desc">Demand (High to Low)</SelectItem>
            <SelectItem value="demand_asc">Demand (Low to High)</SelectItem>
            <SelectItem value="importance_desc">Importance (High to Low)</SelectItem>
            <SelectItem value="importance_asc">Importance (Low to High)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Skill Groups */}
      <div className="space-y-4">
        {paginatedGroups.map(([group, skills]) => {
          const isExpanded = expandedGroups.has(group);
          const metrics = categoryMetrics.get(group) || { demand: 0, coverage: 0 };
          const coverageIndicator = getCoverageIndicator(metrics.coverage);

          return (
            <Card key={group} className="overflow-hidden">
              {/* Category Header */}
              <div
                className="p-4 bg-gray-50 dark:bg-gray-800 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
                onClick={() => toggleGroup(group)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <ChevronRight 
                      className={`w-5 h-5 text-gray-600 dark:text-gray-300 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                    />
                    <h4 className="font-semibold text-lg dark:text-white">{group}</h4>
                    <Badge variant="outline" className="text-xs">
                      {skills.length} skill{skills.length !== 1 ? 's' : ''}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm text-gray-600 dark:text-gray-300">Market Demand</div>
                      <div className="font-semibold dark:text-white">{Math.round(metrics.demand)}%</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {coverageIndicator.icon}
                      <span className={`font-medium ${coverageIndicator.color}`}>
                        {coverageIndicator.label}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Individual Skills */}
              {isExpanded && (
                <CardContent className="p-4 space-y-3">
                  {skills.map((skill, index) => {
                    const skillKey = `${group}-${skill.skill}-${index}`;
                    const evidenceExpanded = expandedEvidence.has(skillKey);
                    const hasEvidence = skill.evidence && skill.evidence.text_snippets && skill.evidence.text_snippets.length > 0;

                    return (
                      <div key={skillKey} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        {/* Skill Header */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h5 className="font-semibold dark:text-white">{skill.skill}</h5>
                              <Badge className={`text-xs ${getImportanceColor(skill.importance_level)}`}>
                                {skill.importance_level}
                              </Badge>
                              {skill.category && (
                                <Badge variant="outline" className="text-xs">
                                  {skill.category}
                                </Badge>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                              {Math.round(skill.match_percentage || 0)}%
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-300">Match</div>
                          </div>
                        </div>

                        {/* Skill Metadata */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                          <div>
                            <div className="text-xs text-gray-600 dark:text-gray-300 mb-1">Market Demand</div>
                            <div className="flex items-center gap-2">
                              <Progress value={(skill.market_demand || 0) * 100} className="h-2 flex-1" />
                              <span className="text-sm font-medium dark:text-white">
                                {Math.round((skill.market_demand || 0) * 100)}%
                              </span>
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600 dark:text-gray-300 mb-1">Confidence</div>
                            <div className="flex items-center gap-2">
                              <Progress value={(skill.confidence_score || 0) * 100} className="h-2 flex-1" />
                              <span className="text-sm font-medium dark:text-white">
                                {Math.round((skill.confidence_score || 0) * 100)}%
                              </span>
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600 dark:text-gray-300 mb-1">Resume Mentions</div>
                            <div className="text-sm font-medium dark:text-white">
                              {skill.resume_mentions || 0}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-600 dark:text-gray-300 mb-1">Job Mentions</div>
                            <div className="text-sm font-medium dark:text-white">
                              {skill.job_mentions || 0}
                            </div>
                          </div>
                        </div>

                        {/* Evidence Section */}
                        {hasEvidence && (
                          <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                            <button
                              onClick={() => toggleEvidence(skillKey)}
                              className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
                            >
                              <ChevronRight 
                                className={`w-4 h-4 transition-transform ${evidenceExpanded ? 'rotate-90' : ''}`}
                              />
                              {evidenceExpanded ? 'Hide' : 'Show'} Evidence ({skill.evidence.text_snippets.length} excerpt{skill.evidence.text_snippets.length !== 1 ? 's' : ''})
                            </button>
                            {evidenceExpanded && (
                              <div className="mt-3 space-y-2">
                                {skill.evidence.text_snippets.map((snippet, idx) => (
                                  <div key={idx} className="bg-gray-50 dark:bg-gray-800 p-3 rounded text-sm">
                                    <p className="text-gray-700 dark:text-gray-300 italic">"{snippet}"</p>
                                    {skill.evidence.origin_locations && skill.evidence.origin_locations[idx] && (
                                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        From: {skill.evidence.origin_locations[idx]}
                                      </p>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600 dark:text-gray-300">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredSkills.length === 0 && (
        <div className="text-center py-12">
          <Target className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">No skill matches found matching your criteria</p>
        </div>
      )}
    </div>
  );
}

// Market Insights Component with Comprehensive Visualizations
function MarketInsightsDisplay({ 
  insights, 
  skillMatches, 
  analyzedJobs, 
  overallMatchScore 
}: { 
  insights: MarketInsights;
  skillMatches: SkillMatch[];
  analyzedJobs: JobMatchScore[];
  overallMatchScore: number;
}) {
  // Calculate skill demand by category (heatmap data)
  const categoryDemandData = useMemo(() => {
    const categoryMap = new Map<string, { demand: number; coverage: number; skillCount: number }>();
    
    skillMatches.forEach(skill => {
      const category = skill.canonical_group || skill.category || 'Other';
      if (!categoryMap.has(category)) {
        categoryMap.set(category, { demand: 0, coverage: 0, skillCount: 0 });
      }
      const data = categoryMap.get(category)!;
      data.demand += (skill.market_demand || 0);
      data.coverage += (skill.match_percentage || 0);
      data.skillCount += 1;
    });
    
    // Calculate averages
    const categories = Array.from(categoryMap.entries()).map(([category, data]) => ({
      category,
      demand: Math.round((data.demand / data.skillCount) * 100),
      coverage: Math.round(data.coverage / data.skillCount)
    }));
    
    // Sort by demand descending
    return categories.sort((a, b) => b.demand - a.demand);
  }, [skillMatches]);

  // Calculate top 10 most in-demand skills
  const topDemandSkills = useMemo(() => {
    // Combine skill matches with their demand data
    const skillsWithDemand = skillMatches.map(skill => ({
      skill: skill.skill,
      demand: (skill.market_demand || 0) * 100,
      jobCount: skill.job_mentions || 0
    }));
    
    // Sort by demand and take top 10
    return skillsWithDemand
      .sort((a, b) => b.demand - a.demand)
      .slice(0, 10);
  }, [skillMatches]);

  // Sort jobs by match score (highest first)
  const sortedJobs = useMemo(() => {
    return [...analyzedJobs].sort((a, b) => b.match_score - a.match_score);
  }, [analyzedJobs]);

  // Competition gauge helpers
  const competitionThreshold = 60;
  const getCompetitionLevel = (score: number) => {
    if (score > competitionThreshold + 5) return { level: 'Low', color: 'text-green-600 dark:text-green-400', bgColor: 'bg-green-100 dark:bg-green-900/30' };
    if (score >= competitionThreshold - 5) return { level: 'Medium', color: 'text-yellow-600 dark:text-yellow-400', bgColor: 'bg-yellow-100 dark:bg-yellow-900/30' };
    return { level: 'High', color: 'text-red-600 dark:text-red-400', bgColor: 'bg-red-100 dark:bg-red-900/30' };
  };

  const competition = getCompetitionLevel(overallMatchScore);

  // Get color for match score
  const getMatchScoreColor = (score: number) => {
    if (score >= 81) return 'text-green-700 dark:text-green-300';
    if (score >= 61) return 'text-green-600 dark:text-green-400';
    if (score >= 41) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold dark:text-white">Market Insights</h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Market demand analysis and competitive positioning
        </p>
      </div>

      {/* Skill Demand Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Skill Category Demand vs Coverage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {categoryDemandData.length > 0 ? (
              categoryDemandData.map((category, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h5 className="font-medium dark:text-white">{category.category}</h5>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-600 dark:text-gray-300">
                        Demand: <span className="font-semibold dark:text-white">{category.demand}%</span>
                      </span>
                      <span className="text-gray-600 dark:text-gray-300">
                        Coverage: <span className="font-semibold dark:text-white">{category.coverage}%</span>
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Market Demand</div>
                      <Progress value={category.demand} className="h-2" />
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Your Coverage</div>
                      <Progress value={category.coverage} className="h-2" />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No category data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Top 10 Most In-Demand Skills */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Top 10 Most In-Demand Skills
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topDemandSkills.length > 0 ? (
              topDemandSkills.map((skill, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-500 dark:text-gray-400 w-6">
                        #{index + 1}
                      </span>
                      <span className="font-medium dark:text-white">{skill.skill}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {skill.jobCount} job{skill.jobCount !== 1 ? 's' : ''}
                      </span>
                      <span className="text-sm font-semibold dark:text-white min-w-[45px] text-right">
                        {Math.round(skill.demand)}%
                      </span>
                    </div>
                  </div>
                  <Progress value={skill.demand} className="h-2" />
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No demand data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Competition Gauge */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Competition Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                  Your match score compared to the competitive threshold
                </p>
                <div className="flex items-center gap-3">
                  <span className="text-lg font-semibold dark:text-white">Competition Level:</span>
                  <Badge className={`text-sm ${competition.bgColor} ${competition.color}`}>
                    {competition.level}
                  </Badge>
                </div>
              </div>
              <div className="text-center">
                <div className={`text-4xl font-bold ${getMatchScoreColor(overallMatchScore)}`}>
                  {Math.round(overallMatchScore)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">Your Score</div>
              </div>
            </div>

            {/* Visual Gauge */}
            <div className="relative">
              <div className="h-8 bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 dark:from-red-900/30 dark:via-yellow-900/30 dark:to-green-900/30 rounded-full overflow-hidden">
                {/* Threshold marker */}
                <div 
                  className="absolute top-0 bottom-0 w-1 bg-gray-800 dark:bg-gray-200"
                  style={{ left: `${competitionThreshold}%` }}
                >
                  <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                    Threshold
                  </div>
                </div>
                {/* User position indicator */}
                <div 
                  className="absolute top-1/2 transform -translate-y-1/2 transition-all duration-500"
                  style={{ left: `${Math.min(Math.max(overallMatchScore, 0), 100)}%` }}
                >
                  <div className="relative">
                    <div className="absolute left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                      <div className="w-4 h-4 bg-blue-600 dark:bg-blue-400 rounded-full border-2 border-white dark:border-gray-800 shadow-lg"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Below Threshold</div>
                <div className="text-lg font-bold text-red-600 dark:text-red-400">
                  {overallMatchScore < competitionThreshold ? '✓' : '—'}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">At Threshold</div>
                <div className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                  {Math.abs(overallMatchScore - competitionThreshold) <= 5 ? '✓' : '—'}
                </div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Above Threshold</div>
                <div className="text-lg font-bold text-green-600 dark:text-green-400">
                  {overallMatchScore > competitionThreshold ? '✓' : '—'}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analyzed Jobs with Match Scores */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Job Match Scores ({sortedJobs.length} jobs analyzed)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {sortedJobs.length > 0 ? (
              sortedJobs.map((job, index) => (
                <div 
                  key={index} 
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h5 className="font-medium dark:text-white">{job.title}</h5>
                      <Badge variant="outline" className="text-xs">
                        {job.company}
                      </Badge>
                    </div>
                    {job.location && (
                      <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300">
                        <MapPin className="w-3 h-3" />
                        <span>{job.location}</span>
                      </div>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <div className={`text-2xl font-bold ${getMatchScoreColor(job.match_score)}`}>
                      {Math.round(job.match_score)}%
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Match</div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No job data available
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
// Recommendations Component
function RecommendationsDisplay({ recommendations }: { recommendations: Recommendation[] }) {
  const [filterType, setFilterType] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const types = useMemo(() => {
    const typeSet = new Set(recommendations.map(rec => rec.type).filter(Boolean));
    return Array.from(typeSet);
  }, [recommendations]);

  const categories = useMemo(() => {
    const catSet = new Set(recommendations.map(rec => rec.category).filter(Boolean));
    return Array.from(catSet);
  }, [recommendations]);

  const filteredRecommendations = useMemo(() => {
    return recommendations.filter(rec => {
      const matchesType = filterType === 'all' || rec.type === filterType;
      const matchesCategory = filterCategory === 'all' || rec.category === filterCategory;
      return matchesType && matchesCategory;
    });
  }, [recommendations, filterType, filterCategory]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low':
        return 'text-green-600 bg-green-100 border-green-200';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'immediate':
        return <AlertTriangle className="w-4 h-4" />;
      case 'short_term':
        return <Clock className="w-4 h-4" />;
      case 'long_term':
        return <Target className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'skills':
        return <Award className="w-4 h-4" />;
      case 'experience':
        return <Star className="w-4 h-4" />;
      case 'education':
        return <BookOpen className="w-4 h-4" />;
      case 'networking':
        return <Share2 className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold dark:text-white">Recommendations</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Actionable steps to improve your career prospects
          </p>
        </div>
        <Badge variant="secondary">{filteredRecommendations.length} recommendations</Badge>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {types.map(type => (
              <SelectItem key={type} value={type}>
                {type ? type.replace('_', ' ') : 'Unknown'}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Filter by category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map(category => (
              <SelectItem key={category} value={category}>
                {category || 'Unknown'}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {filteredRecommendations.map((recommendation, index) => (
          <Card key={index} className="hover:shadow-sm transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="flex items-center gap-2 flex-shrink-0">
                  <div className="p-2 bg-blue-100 rounded-full">
                    {getCategoryIcon(recommendation.category)}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold mb-1 dark:text-white">{recommendation.title}</h4>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getPriorityColor(recommendation.priority)} dark:text-white`}
                        >
                          {getTypeIcon(recommendation.type)}
                          <span className="ml-1">{recommendation.type ? recommendation.type.replace('_', ' ') : 'General'}</span>
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {recommendation.category}
                        </Badge>
                        <Badge 
                          className={`text-xs ${getPriorityColor(recommendation.priority)} dark:text-white`}
                          variant="secondary"
                        >
                          {recommendation.priority} priority
                        </Badge>
                      </div>
                    </div>
                    {recommendation.estimated_time && (
                      <div className="text-right">
                        <div className="text-xs text-gray-500 dark:text-gray-400">Estimated time</div>
                        <div className="text-sm font-medium dark:text-white">{recommendation.estimated_time}</div>
                      </div>
                    )}
                  </div>

                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{recommendation.description}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-gray-400 dark:text-gray-500" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">Mark as completed</span>
                    </div>
                    <Button variant="outline" size="sm" className="gap-2">
                      <ExternalLink className="w-4 h-4" />
                      Learn More
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRecommendations.length === 0 && (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">No recommendations found matching your criteria</p>
        </div>
      )}
    </div>
  );
}

// Career Path Suggestions Component
function CareerPathSuggestions({ suggestions }: { suggestions: CareerPathSuggestion[] }) {
  const sortedSuggestions = useMemo(() => {
    return [...suggestions].sort((a, b) => b.probability - a.probability);
  }, [suggestions]);

  const getProbabilityColor = (probability: number) => {
    if (probability >= 0.8) return 'text-green-600 bg-green-100';
    if (probability >= 0.6) return 'text-blue-600 bg-blue-100';
    if (probability >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700';
  };

  const getProbabilityLabel = (probability: number) => {
    if (probability >= 0.8) return 'High Match';
    if (probability >= 0.6) return 'Good Match';
    if (probability >= 0.4) return 'Moderate Match';
    return 'Low Match';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold dark:text-white">Career Path Suggestions</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Potential career opportunities based on your skills
          </p>
        </div>
        <Badge variant="secondary">{sortedSuggestions.length} paths identified</Badge>
      </div>

      <div className="grid gap-4">
        {sortedSuggestions.map((suggestion, index) => (
          <Card key={index} className="hover:shadow-sm transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-lg font-semibold mb-1 dark:text-white">{suggestion.role}</h4>
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                    <MapPin className="w-4 h-4" />
                    <span>{suggestion.company_type}</span>
                    <Clock className="w-4 h-4 ml-2" />
                    <span>{suggestion.timeline}</span>
                  </div>
                </div>
                <div className="text-right">
                  <Badge 
                    className={`text-sm ${getProbabilityColor(suggestion.probability)} dark:text-white`}
                    variant="secondary"
                  >
                    {getProbabilityLabel(suggestion.probability)}
                  </Badge>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    {Math.round(suggestion.probability * 100)}% match
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <Progress value={suggestion.probability * 100} className="h-2" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h5 className="font-medium mb-2 dark:text-white">Required Skills</h5>
                  <div className="flex flex-wrap gap-1">
                    {suggestion.required_skills.slice(0, 6).map((skill, skillIndex) => (
                      <Badge key={skillIndex} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                    {suggestion.required_skills.length > 6 && (
                      <Badge variant="outline" className="text-xs">
                        +{suggestion.required_skills.length - 6} more
                      </Badge>
                    )}
                  </div>
                </div>

                {suggestion.salary_range && (
                  <div>
                    <h5 className="font-medium mb-2 dark:text-white">Salary Range</h5>
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <span className="text-sm dark:text-white">
                        ${suggestion.salary_range.min?.toLocaleString()} - ${suggestion.salary_range.max?.toLocaleString()}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {suggestion.salary_range.period}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  Timeline: {suggestion.timeline}
                </div>
                <Button variant="outline" size="sm" className="gap-2">
                  <ChevronRight className="w-4 h-4" />
                  Explore Path
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// Main Analysis Results Component
export function AnalysisResults({ analysisId, onExport, onOptimizeResume, onNewAnalysis }: AnalysisResultsProps) {
  const { data: analysis, isLoading: analysisLoading, refetch: refetchAnalysis } = useAnalysis(analysisId);
  const { data: results, isLoading: resultsLoading, error, refetch: refetchResults } = useAnalysisResults(analysisId);

  const isLoading = analysisLoading || resultsLoading;
  
  const handleRefresh = () => {
    refetchAnalysis();
    refetchResults();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 animate-pulse text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-300">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 dark:text-red-400 mx-auto mb-4" />
        <p className="text-red-600 dark:text-red-400 font-medium mb-2">Failed to load analysis results</p>
        <p className="text-sm text-gray-600 dark:text-gray-300">Please try refreshing the page</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-300">No analysis results available</p>
      </div>
    );
  }

  const getOverallScore = () => {
    // Check for overall_match_score from our simplified analysis
    if (results.results?.overall_match_score !== undefined) {
      return Math.round(results.results.overall_match_score);
    }
    // Fallback to match_score
    if (results.match_score !== undefined) {
      return Math.round(results.match_score * 100);
    }
    // Calculate based on skill matches vs gaps
    const matches = results.results?.skill_matches?.length || results.skill_overlaps?.length || 0;
    const gaps = results.results?.skill_gaps?.length || results.skill_gaps?.length || 0;
    const total = matches + gaps;
    return total > 0 ? Math.round((matches / total) * 100) : 0;
  };

  return (
    <div className="h-full w-full overflow-y-auto bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-semibold mb-2 dark:text-white">Analysis Results</h1>
            <p className="text-gray-600 dark:text-gray-300">
              Comprehensive analysis completed on {analysis?.completion_date ? 
                new Date(analysis.completion_date).toLocaleDateString() : 
                'recently'
              }
            </p>
          </div>
          <div className="flex items-center gap-3">
            {onNewAnalysis && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={onNewAnalysis}
                className="gap-2"
              >
                <Target className="w-4 h-4" />
                New Analysis
              </Button>
            )}
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleRefresh}
              disabled={isLoading}
              className="gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            {onOptimizeResume && (
              <Button onClick={onOptimizeResume} className="gap-2">
                <Target className="w-4 h-4" />
                Optimize Resume
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2">
                  <Download className="w-4 h-4" />
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => onExport?.('pdf')}>
                  Export as PDF
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onExport?.('json')}>
                  Export as JSON
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Overall Score */}
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2 dark:text-white">Overall Match Score</h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Based on skill alignment and market analysis
                </p>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  {getOverallScore()}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">Match Score</div>
              </div>
            </div>
            <Progress value={getOverallScore()} className="mt-4 h-3" />
          </CardContent>
        </Card>
      </div>

      {/* Analysis Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="skill-overlaps">Skill Matches</TabsTrigger>
          <TabsTrigger value="skill-gaps">Skill Gaps</TabsTrigger>
          <TabsTrigger value="market-insights">Market Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-6 text-center">
                <Award className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {results.results?.skill_matches?.length || results.skill_overlaps?.length || 0}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Skills Matched</div>
              </CardContent>
            </Card>

            <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <CardContent className="p-6 text-center">
                <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-red-600 dark:text-red-400">
                  {results.results?.skill_gaps?.length || results.skill_gaps?.length || 0}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Skill Gaps</div>
              </CardContent>
            </Card>

            <Card className="bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
              <CardContent className="p-6 text-center">
                <BarChart3 className="w-8 h-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {results.job_count || results.results?.analyzed_jobs?.length || 0}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Jobs Analyzed</div>
              </CardContent>
            </Card>

            <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
              <CardContent className="p-6 text-center">
                <Target className="w-8 h-8 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
                <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                  {getOverallScore()}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">Match Score</div>
              </CardContent>
            </Card>
          </div>

          {/* Match Breakdown Section */}
          {results.results?.match_breakdown && (
            <Card>
              <CardHeader>
                <CardTitle>Match Breakdown by Importance Level</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Must-have Skills */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300">
                        Must-have
                      </Badge>
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {results.results.match_breakdown.must_have.matched} of {results.results.match_breakdown.must_have.total} matched
                      </span>
                    </div>
                    <span className="text-sm font-medium dark:text-white">
                      {results.results.match_breakdown.must_have.total > 0 
                        ? Math.round((results.results.match_breakdown.must_have.matched / results.results.match_breakdown.must_have.total) * 100)
                        : 0}%
                    </span>
                  </div>
                  <Progress 
                    value={results.results.match_breakdown.must_have.total > 0 
                      ? (results.results.match_breakdown.must_have.matched / results.results.match_breakdown.must_have.total) * 100
                      : 0
                    } 
                    className="h-3"
                  />
                </div>

                {/* Nice-to-have Skills */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                        Nice-to-have
                      </Badge>
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {results.results.match_breakdown.nice_to_have.matched} of {results.results.match_breakdown.nice_to_have.total} matched
                      </span>
                    </div>
                    <span className="text-sm font-medium dark:text-white">
                      {results.results.match_breakdown.nice_to_have.total > 0 
                        ? Math.round((results.results.match_breakdown.nice_to_have.matched / results.results.match_breakdown.nice_to_have.total) * 100)
                        : 0}%
                    </span>
                  </div>
                  <Progress 
                    value={results.results.match_breakdown.nice_to_have.total > 0 
                      ? (results.results.match_breakdown.nice_to_have.matched / results.results.match_breakdown.nice_to_have.total) * 100
                      : 0
                    } 
                    className="h-3"
                  />
                </div>

                {/* Preferred Skills */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                        Preferred
                      </Badge>
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {results.results.match_breakdown.preferred.matched} of {results.results.match_breakdown.preferred.total} matched
                      </span>
                    </div>
                    <span className="text-sm font-medium dark:text-white">
                      {results.results.match_breakdown.preferred.total > 0 
                        ? Math.round((results.results.match_breakdown.preferred.matched / results.results.match_breakdown.preferred.total) * 100)
                        : 0}%
                    </span>
                  </div>
                  <Progress 
                    value={results.results.match_breakdown.preferred.total > 0 
                      ? (results.results.match_breakdown.preferred.matched / results.results.match_breakdown.preferred.total) * 100
                      : 0
                    } 
                    className="h-3"
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Competition Assessment */}
          <Card>
            <CardHeader>
              <CardTitle>Competition Assessment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                    Based on your {getOverallScore()}% match score compared to the 60% competitive threshold
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-semibold dark:text-white">Competition Level:</span>
                    <Badge 
                      className={`text-sm ${
                        getOverallScore() > 60 
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                          : getOverallScore() >= 55
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                          : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                      }`}
                    >
                      {getOverallScore() > 60 ? 'Low' : getOverallScore() >= 55 ? 'Medium' : 'High'}
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-gray-900 dark:text-white">
                    {getOverallScore() > 60 ? '✓' : getOverallScore() >= 55 ? '~' : '!'}
                  </div>
                </div>
              </div>
              <div className="mt-4">
                <Progress value={getOverallScore()} className="h-2" />
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-gray-500 dark:text-gray-400">0%</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">60% (threshold)</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">100%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top Strengths and Gaps */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top 5 Strengths */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                  Top 5 Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {(results.results?.top_strengths || []).slice(0, 5).map((strength, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-green-600 dark:bg-green-400 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium dark:text-white">{strength}</span>
                    </div>
                  ))}
                  {(!results.results?.top_strengths || results.results.top_strengths.length === 0) && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                      No strengths data available
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Top 5 Gaps */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  Top 5 Gaps
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {(results.results?.top_gaps || []).slice(0, 5).map((gap, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-red-600 dark:bg-red-400 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium dark:text-white">{gap}</span>
                    </div>
                  ))}
                  {(!results.results?.top_gaps || results.results.top_gaps.length === 0) && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                      No gaps data available
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Analysis Details */}
          <Card>
            <CardHeader>
              <CardTitle>Analysis Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Analysis Date</div>
                  <div className="font-medium dark:text-white">
                    {results.completed_at 
                      ? new Date(results.completed_at).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })
                      : analysis?.completion_date 
                      ? new Date(analysis.completion_date).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })
                      : 'N/A'
                    }
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Jobs Analyzed</div>
                  <div className="font-medium dark:text-white">
                    {results.job_count || results.results?.analyzed_jobs?.length || 0} jobs
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Resume</div>
                  <div className="font-medium dark:text-white truncate" title={results.resume_filename || 'N/A'}>
                    {results.resume_filename || 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Processing Time</div>
                  <div className="font-medium dark:text-white">
                    {results.completed_at && results.created_at
                      ? (() => {
                          const start = new Date(results.created_at).getTime();
                          const end = new Date(results.completed_at).getTime();
                          const seconds = Math.round((end - start) / 1000);
                          if (seconds < 60) return `${seconds}s`;
                          const minutes = Math.floor(seconds / 60);
                          const remainingSeconds = seconds % 60;
                          return `${minutes}m ${remainingSeconds}s`;
                        })()
                      : analysis?.duration || 'N/A'
                    }
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skill-gaps">
          {(results.results?.skill_gaps || results.skill_gaps) && (results.results?.skill_gaps?.length || results.skill_gaps?.length || 0) > 0 ? (
            <SkillGapAnalysis skillGaps={results.results?.skill_gaps || results.skill_gaps} />
          ) : (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-300">No significant skill gaps identified</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="skill-overlaps">
          {(results.results?.skill_matches || results.skill_overlaps) && (results.results?.skill_matches?.length || results.skill_overlaps?.length || 0) > 0 ? (
            <SkillMatchesTab skillMatches={results.results?.skill_matches || results.skill_overlaps} />
          ) : (
            <div className="text-center py-12">
              <AlertTriangle className="w-12 h-12 text-yellow-600 dark:text-yellow-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-300">No skill matches found</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="market-insights">
          {(results.results?.skill_matches || results.skill_overlaps) && 
           (results.results?.analyzed_jobs || results.job_count) ? (
            <MarketInsightsDisplay 
              insights={results.results?.market_insights || results.market_insights || { top_skills: [], industry_trends: [], competition_level: '' }}
              skillMatches={results.results?.skill_matches || results.skill_overlaps || []}
              analyzedJobs={results.results?.analyzed_jobs || []}
              overallMatchScore={getOverallScore()}
            />
          ) : (
            <div className="text-center py-12">
              <TrendingUp className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-300">Market insights not available</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Skill matches and job data are required to display market insights
              </p>
            </div>
          )}
        </TabsContent>
      </Tabs>
      </div>
    </div>
  );
}
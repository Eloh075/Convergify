export interface SkillMatch {
  id: string;
  skillName: string;
  confidence: number;
  experienceLevel: string;
  matchType: 'strong' | 'foundational' | 'missing';
  substitutionReasoning: string;
  textSnippet: string;
  category: 'must-have' | 'nice-to-have';
}

export interface AnalysisResult {
  overallScore: number;
  mustHaveScore: number;
  niceToHaveScore: number;
  jobsAnalyzed: number;
  skills: SkillMatch[];
  immediateActions: string[];
}

export const mockAnalysisData: AnalysisResult = {
  overallScore: 88.2,
  mustHaveScore: 90,
  niceToHaveScore: 86.5,
  jobsAnalyzed: 5,
  skills: [
    {
      id: '1',
      skillName: 'Strategic Account Management',
      confidence: 0.95,
      experienceLevel: '8+ years',
      matchType: 'strong',
      substitutionReasoning: 'Direct evidence of enterprise account ownership with strategic planning responsibilities across multiple product lines.',
      textSnippet: 'Led strategic initiatives for 12 enterprise accounts ($2M+ ARR), developing multi-year roadmaps aligned with client business objectives.',
      category: 'must-have'
    },
    {
      id: '2',
      skillName: 'Cross-functional Leadership',
      confidence: 0.92,
      experienceLevel: '5+ years',
      matchType: 'strong',
      substitutionReasoning: 'Demonstrated ability to coordinate between engineering, product, and sales teams to deliver client outcomes.',
      textSnippet: 'Collaborated with Engineering, Product, and Sales teams to deliver customized solutions, achieving 95% on-time delivery rate.',
      category: 'must-have'
    },
    {
      id: '3',
      skillName: 'Revenue Growth & Upselling',
      confidence: 0.88,
      experienceLevel: '6+ years',
      matchType: 'strong',
      substitutionReasoning: 'Quantifiable track record of expanding account revenue through strategic upselling and cross-selling initiatives.',
      textSnippet: 'Drove $1.2M in expansion revenue through strategic upselling, maintaining 120% net revenue retention across portfolio.',
      category: 'must-have'
    },
    {
      id: '4',
      skillName: 'SaaS Platform Expertise',
      confidence: 0.65,
      experienceLevel: '4+ years',
      matchType: 'foundational',
      substitutionReasoning: 'Experience with cloud-based platforms inferred from context, but not explicitly stated as "SaaS" expertise.',
      textSnippet: 'Managed implementation of cloud-based enterprise solutions for Fortune 500 clients across multiple verticals.',
      category: 'must-have'
    },
    {
      id: '5',
      skillName: 'Executive Relationship Building',
      confidence: 0.91,
      experienceLevel: '7+ years',
      matchType: 'strong',
      substitutionReasoning: 'Clear evidence of C-suite engagement and executive-level communication throughout career progression.',
      textSnippet: 'Established trusted advisor relationships with C-suite executives, conducting quarterly business reviews and strategic planning sessions.',
      category: 'nice-to-have'
    },
    {
      id: '6',
      skillName: 'Customer Success Metrics',
      confidence: 0.87,
      experienceLevel: '5+ years',
      matchType: 'strong',
      substitutionReasoning: 'Strong evidence of tracking and optimizing key customer success KPIs including retention and satisfaction.',
      textSnippet: 'Maintained 98% renewal rate and 92 NPS score through proactive engagement and data-driven success planning.',
      category: 'nice-to-have'
    },
    {
      id: '7',
      skillName: 'B2B Sales Experience',
      confidence: 0.0,
      experienceLevel: 'Not found',
      matchType: 'missing',
      substitutionReasoning: 'No direct evidence of quota-carrying sales experience or lead generation activities found in resume.',
      textSnippet: '',
      category: 'nice-to-have'
    },
    {
      id: '8',
      skillName: 'Change Management',
      confidence: 0.58,
      experienceLevel: '3+ years',
      matchType: 'foundational',
      substitutionReasoning: 'Inferred from implementation and training responsibilities, but not explicitly framed as organizational change management.',
      textSnippet: 'Led onboarding and training programs for new platform implementations, achieving 85% user adoption within first quarter.',
      category: 'nice-to-have'
    }
  ],
  immediateActions: [
    'Add "B2B Sales" to professional summary',
    'Reframe "SaaS Platform Expertise" more explicitly',
    'Quantify change management impact with adoption metrics',
    'Include specific CRM/Success platform tools (e.g., Salesforce, Gainsight)'
  ]
};

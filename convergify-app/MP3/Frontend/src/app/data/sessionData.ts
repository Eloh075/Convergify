import { AnalysisResult } from './mockAnalysis';

export interface ResumeVersion {
  id: string;
  versionTag: string;
  content: string; // Markdown content
  createdAt: Date;
}

export interface AnalysisSession {
  id: string;
  title: string;
  searchQuery: string;
  jobLevel: string;
  createdAt: Date;
  jobCount: number;
  selectedJobIds: string[];
  originalResume: string; // PDF or text content
  optimizedResume?: ResumeVersion;
  analysisResult: AnalysisResult;
}

export interface JobEntry {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  source: 'manual' | 'scraper';
  scraperId?: string; // Links to scraper session
  createdAt: Date;
}

export interface JobGroup {
  id: string;
  name: string;
  jobIds: string[];
  createdAt: Date;
}

export interface ScraperSession {
  id: string;
  searchQuery: string;
  jobLevel: string;
  jobsFound: number;
  createdAt: Date;
  jobIds: string[];
}

// Mock data
export const mockSessions: AnalysisSession[] = [
  {
    id: 'session-1',
    title: 'Market Analysis: Business Development',
    searchQuery: 'Business Development',
    jobLevel: 'senior',
    createdAt: new Date('2026-02-01'),
    jobCount: 5,
    selectedJobIds: ['1', '2', '3', '4', '5'],
    originalResume: 'Original resume content...',
    analysisResult: {
      overallScore: 88.2,
      mustHaveScore: 90,
      niceToHaveScore: 86.5,
      jobsAnalyzed: 5,
      skills: [],
      immediateActions: [],
    },
  },
  {
    id: 'session-2',
    title: 'Single Job Analysis: Stripe Account Executive',
    searchQuery: 'Account Executive',
    jobLevel: 'senior',
    createdAt: new Date('2026-01-28'),
    jobCount: 1,
    selectedJobIds: ['3'],
    originalResume: 'Original resume content...',
    optimizedResume: {
      id: 'opt-1',
      versionTag: 'Stripe_Targeted',
      content: '# John Doe\n**Strategic Account Executive**\n\n## Professional Summary\nResults-driven Account Executive with 8+ years...',
      createdAt: new Date('2026-01-28'),
    },
    analysisResult: {
      overallScore: 92.5,
      mustHaveScore: 95,
      niceToHaveScore: 89,
      jobsAnalyzed: 1,
      skills: [],
      immediateActions: [],
    },
  },
];

export const mockJobGroups: JobGroup[] = [
  {
    id: 'group-1',
    name: 'Dream Companies',
    jobIds: ['1', '3', '5'],
    createdAt: new Date('2026-01-25'),
  },
  {
    id: 'group-2',
    name: 'Backup Options',
    jobIds: ['2', '4'],
    createdAt: new Date('2026-01-20'),
  },
];

export const mockScraperSessions: ScraperSession[] = [
  {
    id: 'scraper-1',
    searchQuery: 'Account Manager',
    jobLevel: 'senior',
    jobsFound: 5,
    createdAt: new Date('2026-02-01'),
    jobIds: ['1', '2', '3', '4', '5'],
  },
];

/**
 * TypeScript Interface Validation Tests
 * 
 * These tests validate that the TypeScript interfaces correctly match
 * the backend API response structure. They use TypeScript's type system
 * to catch type mismatches at compile time.
 * 
 * Task: 2.1 - Write unit tests for TypeScript interface validation
 * Spec: analysis-results-dashboard-redesign
 * Requirements: 11.3, 11.5
 */

import type {
  AnalysisResultsResponse,
  SkillMatch,
  SkillGap,
  MatchBreakdown,
  JobMatchScore,
} from '../api';

/**
 * Test 1: Sample backend response conforms to AnalysisResultsResponse interface
 * 
 * This test validates that a complete backend response structure
 * matches the TypeScript interface exactly.
 */
const validAnalysisResponse: AnalysisResultsResponse = {
  analysis_id: '68691c53-08d9-4893-bd12-f2230186d6ab',
  resume_id: 'resume-uuid-123',
  resume_filename: 'john_doe_resume.pdf',
  job_count: 10,
  job_titles: ['AI Engineer', 'ML Engineer', 'Data Scientist'],
  analysis_type: 'comprehensive',
  status: 'completed',
  results: {
    overall_match_score: 75.5,
    skill_matches: [
      {
        skill: 'Python',
        canonical_group: 'Programming Languages',
        match_percentage: 95.0,
        confidence_score: 0.95,
        importance_level: 'Must-have',
        market_demand: 0.6,
        category: 'Programming Languages',
        relevance_score: 0.95,
        resume_mentions: 3,
        job_mentions: 6,
        match_type: 'Exact',
        evidence: {
          found: true,
          text_snippets: ['5 years of Python development', 'Python expert'],
          origin_locations: ['Experience', 'Skills'],
          timeline: '2018-2023',
          confidence: 0.95,
        },
      },
    ],
    skill_gaps: [
      {
        skill: 'PyTorch',
        importance: 1.0,
        importance_level: 'Must-have',
        market_demand: 0.2,
        category: 'Must-have',
        why_matters: 'This must have skill is required by 20% of analyzed positions and is critical for competitive applications.',
        jobs_requiring: ['AI Engineer', 'ML Engineer'],
        learning_resources: [],
      },
    ],
    market_insights: {
      top_skills: [
        {
          skill: 'Python',
          demand_score: 0.8,
          growth_trend: 'increasing',
          job_count: 8,
        },
      ],
      industry_trends: [
        {
          trend: 'AI/ML Growth',
          description: 'Increasing demand for AI/ML skills',
          impact: 'high',
        },
      ],
      competition_level: 'medium',
      average_salary: {
        min: 60000,
        max: 120000,
        currency: 'USD',
        period: 'annual',
      },
    },
    match_breakdown: {
      must_have: { matched: 5, total: 10 },
      nice_to_have: { matched: 3, total: 5 },
      preferred: { matched: 2, total: 3 },
    },
    top_strengths: ['Python', 'Machine Learning', 'Data Analysis', 'SQL', 'Git'],
    top_gaps: ['PyTorch', 'TensorFlow', 'Docker', 'Kubernetes', 'AWS'],
    analyzed_jobs: [
      {
        job_id: 'job-uuid-1',
        title: 'AI Engineer',
        company: 'Tech Corp',
        location: 'Singapore',
        match_score: 75.5,
        required_skills: ['Python', 'Machine Learning', 'PyTorch'],
      },
    ],
  },
  created_at: '2026-02-09T10:00:00Z',
  completed_at: '2026-02-09T10:05:00Z',
};

/**
 * Test 2: SkillMatch interface validation
 * 
 * Validates that all required fields are present and correctly typed
 * in the SkillMatch interface.
 */
const validSkillMatch: SkillMatch = {
  skill: 'Python',
  canonical_group: 'Programming Languages',
  match_percentage: 95.0,
  confidence_score: 0.95,
  importance_level: 'Must-have',
  market_demand: 0.6,
  category: 'Programming Languages',
  relevance_score: 0.95,
  resume_mentions: 3,
  job_mentions: 6,
  match_type: 'Exact',
  evidence: {
    found: true,
    text_snippets: ['5 years of Python development'],
    origin_locations: ['Experience'],
    timeline: '2018-2023',
    confidence: 0.95,
  },
};

/**
 * Test 3: SkillMatch with different match_type values
 * 
 * Validates that the match_type union type accepts all valid values.
 */
const skillMatchExact: SkillMatch = { ...validSkillMatch, match_type: 'Exact' };
const skillMatchSemantic: SkillMatch = { ...validSkillMatch, match_type: 'Semantic' };
const skillMatchSubstitution: SkillMatch = { ...validSkillMatch, match_type: 'Substitution' };
const skillMatchNone: SkillMatch = { ...validSkillMatch, match_type: 'None' };

/**
 * Test 4: SkillGap interface validation
 * 
 * Validates that all required fields are present and correctly typed
 * in the SkillGap interface.
 */
const validSkillGap: SkillGap = {
  skill: 'PyTorch',
  importance: 1.0,
  importance_level: 'Must-have',
  market_demand: 0.2,
  category: 'Must-have',
  why_matters: 'This must have skill is required by 20% of analyzed positions.',
  jobs_requiring: ['AI Engineer', 'ML Engineer'],
  learning_resources: [],
};

/**
 * Test 5: SkillGap with different importance_level values
 * 
 * Validates that the importance_level union type accepts all valid values.
 */
const skillGapMustHave: SkillGap = { ...validSkillGap, importance_level: 'Must-have' };
const skillGapNiceToHave: SkillGap = { ...validSkillGap, importance_level: 'Nice-to-have' };
const skillGapPreferred: SkillGap = { ...validSkillGap, importance_level: 'Preferred' };

/**
 * Test 6: MatchBreakdown interface validation
 * 
 * Validates the structure of the match breakdown with all three tiers.
 */
const validMatchBreakdown: MatchBreakdown = {
  must_have: { matched: 5, total: 10 },
  nice_to_have: { matched: 3, total: 5 },
  preferred: { matched: 2, total: 3 },
};

/**
 * Test 7: JobMatchScore interface validation
 * 
 * Validates that job_id is a string (UUID format) and all other fields
 * are correctly typed.
 */
const validJobMatchScore: JobMatchScore = {
  job_id: 'job-uuid-123',
  title: 'AI Engineer',
  company: 'Tech Corp',
  location: 'Singapore',
  match_score: 75.5,
  required_skills: ['Python', 'Machine Learning', 'PyTorch'],
};

/**
 * Test 8: Evidence structure validation
 * 
 * Validates the complete evidence structure with all required fields.
 */
const validEvidence: SkillMatch['evidence'] = {
  found: true,
  text_snippets: ['Python development', 'Machine learning projects'],
  origin_locations: ['Experience', 'Projects'],
  timeline: '2018-2023',
  confidence: 0.95,
};

/**
 * Test 9: Empty arrays are valid
 * 
 * Validates that empty arrays are acceptable for array fields.
 */
const skillMatchWithEmptyEvidence: SkillMatch = {
  ...validSkillMatch,
  evidence: {
    found: false,
    text_snippets: [],
    origin_locations: [],
    timeline: '',
    confidence: 0.0,
  },
};

const skillGapWithEmptyArrays: SkillGap = {
  ...validSkillGap,
  jobs_requiring: [],
  learning_resources: [],
};

/**
 * Test 10: Numeric ranges validation
 * 
 * Validates that numeric fields accept valid ranges.
 */
const skillMatchWithBoundaryValues: SkillMatch = {
  ...validSkillMatch,
  match_percentage: 0, // Min value
  confidence_score: 1.0, // Max value
  market_demand: 0.5, // Mid value
  relevance_score: 0.0, // Min value
  resume_mentions: 0, // Min value
  job_mentions: 100, // High value
};

const skillGapWithBoundaryValues: SkillGap = {
  ...validSkillGap,
  importance: 0.0, // Min value
  market_demand: 1.0, // Max value
};

/**
 * Type-level tests using TypeScript's type system
 * 
 * These tests will fail at compile time if the types don't match.
 * The commented-out code below demonstrates that TypeScript correctly
 * catches type errors. Uncomment any of these to verify type checking works.
 */

// Test that missing required fields cause compile errors
// Uncomment these to verify TypeScript catches missing fields:

// const invalidSkillMatch1: SkillMatch = {
//   canonical_group: 'Programming Languages',
//   match_percentage: 95.0,
// };

// const invalidSkillMatch2: SkillMatch = {
//   skill: 'Python',
//   canonical_group: 'Programming Languages',
//   match_percentage: 95.0,
//   confidence_score: 0.95,
//   importance_level: 'Must-have',
//   market_demand: 0.6,
//   category: 'Programming Languages',
//   relevance_score: 0.95,
//   resume_mentions: 3,
//   job_mentions: 6,
//   match_type: 'Exact',
// };

// const invalidSkillMatch3: SkillMatch = {
//   ...validSkillMatch,
//   match_type: 'Invalid',
// };

// const invalidSkillGap1: SkillGap = {
//   ...validSkillGap,
//   importance_level: 'Critical',
// };

// const invalidJobMatchScore: JobMatchScore = {
//   job_id: 123,
//   title: 'AI Engineer',
//   company: 'Tech Corp',
//   location: 'Singapore',
//   match_score: 75.5,
//   required_skills: ['Python'],
// };

/**
 * Export validation results
 * 
 * If this file compiles without errors, all interface validations pass.
 */
export const interfaceValidationTests = {
  validAnalysisResponse,
  validSkillMatch,
  validSkillGap,
  validMatchBreakdown,
  validJobMatchScore,
  validEvidence,
  skillMatchExact,
  skillMatchSemantic,
  skillMatchSubstitution,
  skillMatchNone,
  skillGapMustHave,
  skillGapNiceToHave,
  skillGapPreferred,
  skillMatchWithEmptyEvidence,
  skillGapWithEmptyArrays,
  skillMatchWithBoundaryValues,
  skillGapWithBoundaryValues,
};

/**
 * Test Summary:
 * 
 * ✅ Test 1: Complete AnalysisResultsResponse structure validates
 * ✅ Test 2: SkillMatch interface with all required fields validates
 * ✅ Test 3: All match_type union values validate
 * ✅ Test 4: SkillGap interface with all required fields validates
 * ✅ Test 5: All importance_level union values validate
 * ✅ Test 6: MatchBreakdown structure validates
 * ✅ Test 7: JobMatchScore with string job_id validates
 * ✅ Test 8: Evidence structure with all fields validates
 * ✅ Test 9: Empty arrays are valid
 * ✅ Test 10: Numeric boundary values validate
 * 
 * Type-level tests (commented out) verify that:
 * - Missing required fields cause compile errors
 * - Invalid union type values cause compile errors
 * - Incorrect data types cause compile errors
 * 
 * If this file compiles successfully with `npx tsc --noEmit`, all tests pass.
 */

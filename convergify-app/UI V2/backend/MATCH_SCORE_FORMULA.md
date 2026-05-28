# Match Score Calculation Formula

**Last Updated**: 2026-03-06  
**Status**: ✅ Implemented in `gap-analysis.ts`

---

## Strategic Evaluation Formula

The match score uses a two-part formula that rewards both core competency and differentiation:

### 1. Core Match Score (Base Score)
**Formula**: `(Must-Have Skills Matched / Total Must-Have Skills) × 100`

**Logic**: Calculate the percentage only against the "Must-Have" (>60% frequency) skills.

**Example**:
- Market demands 5 Must-Have skills: Python, Git, REST APIs, SQL, Docker
- User has 4 of them: Python, Git, REST APIs, SQL
- Base Score = (4 / 5) × 100 = **80%**

**Why**: Must-Have skills are the foundation. If you don't have these, you're not competitive regardless of how many Nice-to-Have skills you possess.

---

### 2. Differentiator Multiplier (Bonus)
**Formula**: `+2% for each Nice-to-Have skill possessed`

**Logic**: For every "Nice-to-Have" (30-59% frequency) skill they possess, add a +2% bonus to their overall score.

**Cap**: Maximum final score is **95%** (no resume is perfect)

**Example**:
- Base Score: 80%
- User has 5 Nice-to-Have skills: AWS, PostgreSQL, Redis, Kubernetes, GraphQL
- Differentiator Bonus = 5 × 2% = +10%
- Final Score = min(95%, 80% + 10%) = **90%**

**Why**: Nice-to-Have skills are differentiators that make you stand out. They shouldn't replace Must-Haves, but they should boost your competitiveness.

---

## Complete Formula

```typescript
// Step 1: Calculate base score from Must-Have skills
const baseMatchScore = (mustHaveMatches.length / mustHave.length) × 100;

// Step 2: Add differentiator bonus
const differentiatorBonus = niceToHaveMatches.length × 2;

// Step 3: Apply cap at 95%
const finalMatchScore = Math.min(95, Math.round(baseMatchScore + differentiatorBonus));
```

---

## Examples

### Example 1: Strong Core, Few Differentiators
- Must-Have: 10 skills, User has 9 → Base: 90%
- Nice-to-Have: User has 2 → Bonus: +4%
- **Final Score: 94%**

### Example 2: Weak Core, Many Differentiators
- Must-Have: 10 skills, User has 5 → Base: 50%
- Nice-to-Have: User has 15 → Bonus: +30%
- **Final Score: 80%** (50% + 30%)

### Example 3: Perfect Core, Many Differentiators
- Must-Have: 10 skills, User has 10 → Base: 100%
- Nice-to-Have: User has 10 → Bonus: +20%
- **Final Score: 95%** (capped, not 120%)

### Example 4: No Core Skills
- Must-Have: 10 skills, User has 0 → Base: 0%
- Nice-to-Have: User has 20 → Bonus: +40%
- **Final Score: 40%** (0% + 40%)

---

## Why This Formula Works

### 1. **Prioritizes Core Competency**
The base score ensures that Must-Have skills are the foundation. You can't compensate for missing core skills with differentiators alone.

### 2. **Rewards Differentiation**
The bonus recognizes that having Nice-to-Have skills makes you more competitive and versatile.

### 3. **Realistic Cap**
The 95% cap acknowledges that no resume is perfect and prevents unrealistic 100%+ scores.

### 4. **Clear Actionability**
- Score < 60%: Focus on Must-Have skills (dealbreakers)
- Score 60-80%: Add differentiators to stand out
- Score > 80%: You're competitive, polish your resume

---

## Implementation Details

### File: `gap-analysis.ts`

```typescript
export function calculateGapAnalysis(
  resumeSkills: string[],
  marketSkills: MarketSkill[]
): GapAnalysisResult {
  // Categorize market skills by importance
  const mustHave = marketSkills.filter(s => s.importance === 'Must-have');
  const niceToHave = marketSkills.filter(s => s.importance === 'Nice-to-have');
  
  // Calculate matches
  const mustHaveMatches = mustHave.filter(s => 
    resumeSet.has(s.canonical_name.toLowerCase().trim())
  );
  const niceToHaveMatches = niceToHave.filter(s => 
    resumeSet.has(s.canonical_name.toLowerCase().trim())
  );
  
  // Calculate base match score (Must-have skills only)
  const baseMatchScore = mustHave.length > 0
    ? (mustHaveMatches.length / mustHave.length) * 100
    : 0;
  
  // Apply Differentiator Multiplier: +2% for each Nice-to-have skill
  const differentiatorBonus = niceToHaveMatches.length * 2;
  
  // Final score capped at 95%
  const finalMatchScore = Math.min(95, Math.round(baseMatchScore + differentiatorBonus));
  
  return {
    match_score: finalMatchScore,
    dealbreakers: { matched: mustHaveMatches, gaps: mustHaveGaps },
    differentiators: { matched: niceToHaveMatches, gaps: niceToHaveGaps },
    // ...
  };
}
```

---

## Dashboard Display Recommendations

### Match Score Display
```
┌─────────────────────────────────────┐
│  Your Match Score: 85%              │
│                                      │
│  ████████████████░░░░  85%          │
│                                      │
│  Core Skills: 80% (8/10)            │
│  Differentiator Bonus: +10% (5)    │
└─────────────────────────────────────┘
```

### Breakdown Display
```
🔴 Dealbreakers (Must-Have)
   ✓ 8 matched  ❌ 2 missing
   Base Score: 80%

🟡 Differentiators (Nice-to-Have)
   ✓ 5 matched  ⚪ 12 available
   Bonus: +10%

Final Score: 90%
```

### Actionable Insights
- **< 60%**: "Focus on these 5 dealbreaker skills to become competitive"
- **60-80%**: "You're competitive! Add these differentiators to stand out"
- **> 80%**: "Strong profile! Polish your resume and apply confidently"

---

## Testing

### Test Cases

```typescript
// Test 1: Perfect core, no differentiators
mustHave: 10, matched: 10 → base: 100%
niceToHave: 0 → bonus: 0%
Expected: 100%

// Test 2: Weak core, many differentiators
mustHave: 10, matched: 4 → base: 40%
niceToHave: 20 → bonus: 40%
Expected: 80%

// Test 3: Cap at 95%
mustHave: 10, matched: 10 → base: 100%
niceToHave: 30 → bonus: 60%
Expected: 95% (capped, not 160%)

// Test 4: No must-haves in market
mustHave: 0 → base: 0%
niceToHave: 10 → bonus: 20%
Expected: 20%
```

---

## Deployment

**Status**: ✅ Implemented and ready to deploy

**Next Steps**:
1. Deploy updated `gap-analysis.ts` to Supabase Edge Functions
2. Test with real resume data
3. Update frontend to display breakdown (base + bonus)

**Deploy Command**:
```bash
cd "UI V2/backend"
npx supabase functions deploy analyze-market-role --project-ref wpvavxzfbulwrnyrcmnz --no-verify-jwt
npx supabase functions deploy analyze-job-posting --project-ref wpvavxzfbulwrnyrcmnz --no-verify-jwt
```

---

**This formula provides a balanced, actionable, and realistic assessment of a candidate's market fit.**

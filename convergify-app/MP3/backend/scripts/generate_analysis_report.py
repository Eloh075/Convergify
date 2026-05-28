import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('career_analysis.db')
cursor = conn.cursor()

# Get the completed analysis
cursor.execute('SELECT id, resume_id, job_ids, status, results, start_date, completion_date FROM analyses WHERE status = "completed" LIMIT 1')
row = cursor.fetchone()

if not row:
    print("No completed analysis found")
    exit(1)

analysis_id, resume_id, job_ids_str, status, results_str, start_date, completion_date = row

# Parse data
job_ids = json.loads(job_ids_str)
results = json.loads(results_str)

# Get resume info
cursor.execute('SELECT filename, original_text FROM resumes WHERE id = ?', (resume_id,))
resume_row = cursor.fetchone()
resume_filename = resume_row[0] if resume_row else "Unknown"
resume_text = resume_row[1] if resume_row else ""

# Get job info
cursor.execute('SELECT id, title, company, location FROM jobs WHERE id IN ({})'.format(','.join('?' * len(job_ids))), job_ids)
jobs = cursor.fetchall()

conn.close()

# Generate markdown report
report = f"""# Analysis Report

## Analysis Overview

- **Analysis ID**: `{analysis_id}`
- **Status**: {status}
- **Started**: {start_date}
- **Completed**: {completion_date}
- **Resume**: {resume_filename}
- **Jobs Analyzed**: {len(jobs)}

---

## Overall Match Score

**{results.get('overall_match_score', 0)}%**

Based on skill alignment between your resume and {len(jobs)} job postings.

---

## Jobs Analyzed

"""

for i, job in enumerate(jobs, 1):
    job_id, title, company, location = job
    report += f"{i}. **{title}** at {company} ({location or 'Location not specified'})\n"

report += f"""
---

## Skill Matches ({len(results.get('skill_matches', []))})

Skills you have that match job requirements:

"""

for match in results.get('skill_matches', [])[:10]:
    skill = match.get('skill')
    relevance = match.get('relevance_score', 0)
    resume_mentions = match.get('resume_mentions', 0)
    job_mentions = match.get('job_mentions', 0)
    
    report += f"""
### {skill}
- **Relevance Score**: {relevance * 100:.0f}%
- **Resume Mentions**: {resume_mentions}
- **Job Mentions**: {job_mentions}
"""

report += f"""
---

## Skill Gaps ({len(results.get('skill_gaps', []))})

Skills missing from your resume that are in demand:

"""

for gap in results.get('skill_gaps', [])[:15]:
    skill = gap.get('skill')
    importance = gap.get('importance', 0)
    market_demand = gap.get('market_demand', 0)
    category = gap.get('category', 'Other')
    
    report += f"""
### {skill}
- **Category**: {category}
- **Importance**: {importance * 100:.0f}%
- **Market Demand**: {market_demand * 100:.0f}%
"""

report += f"""
---

## Market Insights

"""

insights = results.get('market_insights', {})
top_skills = insights.get('top_skills', [])
competition_level = insights.get('competition_level', 'unknown')

report += f"""
### Competition Level
**{competition_level.upper()}**

### Top Skills in Demand ({len(top_skills)})

"""

for skill_data in top_skills[:10]:
    skill = skill_data.get('skill')
    demand_score = skill_data.get('demand_score', 0)
    job_count = skill_data.get('job_count', 0)
    growth_trend = skill_data.get('growth_trend', 'stable')
    
    report += f"- **{skill}**: {demand_score * 100:.0f}% demand ({job_count} jobs) - {growth_trend}\n"

if insights.get('average_salary'):
    salary = insights['average_salary']
    report += f"""
### Salary Range
${salary.get('min', 0):,} - ${salary.get('max', 0):,} {salary.get('currency', 'USD')}
"""

report += f"""
---

## Recommendations ({len(results.get('recommendations', []))})

"""

for rec in results.get('recommendations', []):
    title = rec.get('title', 'Recommendation')
    category = rec.get('category', 'General')
    priority = rec.get('priority', 'Medium')
    description = rec.get('description', '')
    
    report += f"""
### {title}
- **Category**: {category}
- **Priority**: {priority}
- **Description**: {description}
"""

report += f"""
---

## Career Paths ({len(results.get('career_paths', []))})

Potential career opportunities based on your skills:

"""

for path in results.get('career_paths', []):
    role = path.get('role', 'Position')
    probability = path.get('probability', 0)
    company_type = path.get('company_type', 'Companies')
    timeline = path.get('timeline', 'Unknown')
    required_skills = path.get('required_skills', [])
    
    report += f"""
### {role}
- **Match Probability**: {probability * 100:.0f}%
- **Company Type**: {company_type}
- **Timeline**: {timeline}
- **Required Skills**: {', '.join(required_skills[:5])}
"""

report += f"""
---

## Summary

### Your Profile
- **Total Skills Identified**: {results.get('summary', {}).get('total_skills_identified', 0)}
- **Matching Skills**: {results.get('summary', {}).get('matching_skills', 0)}
- **Missing Skills**: {results.get('summary', {}).get('missing_skills', 0)}

### Analysis Stats
- **Jobs Analyzed**: {results.get('summary', {}).get('jobs_analyzed', 0)}
- **Overall Match**: {results.get('overall_match_score', 0)}%
- **Competition Level**: {competition_level}

---

*Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""

# Write to file
with open('ANALYSIS_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("✅ Analysis report generated: ANALYSIS_REPORT.md")
print(f"\nQuick Stats:")
print(f"  Overall Match: {results.get('overall_match_score', 0)}%")
print(f"  Skill Matches: {len(results.get('skill_matches', []))}")
print(f"  Skill Gaps: {len(results.get('skill_gaps', []))}")
print(f"  Jobs Analyzed: {len(jobs)}")

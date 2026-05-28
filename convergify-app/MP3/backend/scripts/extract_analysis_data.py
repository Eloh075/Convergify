import sqlite3
import json

conn = sqlite3.connect('../career_analysis.db')
cursor = conn.cursor()

cursor.execute('SELECT results FROM analyses ORDER BY created_at DESC LIMIT 1')
results = json.loads(cursor.fetchone()[0])

print('=== SKILL GAPS (First 20) ===')
for i, sg in enumerate(results['skill_gaps'][:20], 1):
    print(f"{i}. {sg['skill']}: importance={sg['importance']}, market_demand={sg['market_demand']}, category={sg['category']}")

print('\n=== SKILL MATCHES (First 15) ===')
for i, sm in enumerate(results['skill_matches'][:15], 1):
    print(f"{i}. {sm['skill']}: relevance={sm['relevance_score']}, mentions={sm['resume_mentions']}")

print('\n=== MARKET INSIGHTS TOP SKILLS (First 15) ===')
for i, ts in enumerate(results['market_insights']['top_skills'][:15], 1):
    print(f"{i}. {ts['skill']}: demand_score={ts['demand_score']}, job_count={ts['job_count']}, trend={ts['growth_trend']}")

conn.close()

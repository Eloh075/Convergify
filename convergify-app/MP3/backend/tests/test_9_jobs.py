#!/usr/bin/env python3
"""
Test with 9 jobs (the failing case)
"""
import sys
import time
import json
from datetime import datetime
from database import SessionLocal
from models.resume import Resume
from models.job import Job

def main():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("TEST - 9 JOBS (Previously Failing)")
        print("=" * 80)
        
        resume = db.query(Resume).first()
        jobs = db.query(Job).limit(9).all()
        
        if not resume or len(jobs) < 9:
            print(f"❌ Need at least 1 resume and 9 jobs (found {len(jobs)})")
            return 1
        
        print(f"\n✅ Resume: {resume.filename}")
        print(f"✅ Jobs: {len(jobs)}")
        for i, job in enumerate(jobs, 1):
            print(f"   {i}. {job.title} at {job.company}")
        
        job_ids = [job.id for job in jobs]
        job_ids_json = json.dumps(job_ids)
        
        print(f"\n{'='*80}")
        print(f"STARTING - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")
        
        start = time.time()
        
        import subprocess
        process = subprocess.Popen(
            [sys.executable, 'run_analysis_strategic.py', resume.id, job_ids_json, 'market_intelligence'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Show output in real-time
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            print(line.rstrip())
        
        process.wait()
        elapsed = time.time() - start
        
        print(f"\n{'='*80}")
        print(f"DONE - {datetime.now().strftime('%H:%M:%S')}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Per job: {elapsed/len(jobs):.1f}s")
        print(f"{'='*80}")
        
        if process.returncode == 0:
            print("\n✅ SUCCESS - The fix worked!")
        else:
            print(f"\n❌ FAILED (code: {process.returncode})")
        
        return process.returncode
        
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())

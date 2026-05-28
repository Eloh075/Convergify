#!/usr/bin/env python3
"""
Test script to measure analysis timing with 10 jobs
"""
import sys
import time
import json
from datetime import datetime
from database import SessionLocal
from models.resume import Resume
from models.job import Job

def test_analysis_timing():
    """Test analysis with 10 jobs and measure timing"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("ANALYSIS TIMING TEST - 10 JOBS")
        print("=" * 80)
        
        # Get a resume
        resume = db.query(Resume).first()
        if not resume:
            print("❌ No resume found in database")
            return 1
        
        print(f"\n✅ Found resume: {resume.filename}")
        print(f"   Resume ID: {resume.id}")
        
        # Get 10 jobs
        jobs = db.query(Job).limit(10).all()
        if len(jobs) < 10:
            print(f"⚠️  Only found {len(jobs)} jobs (need 10)")
            if len(jobs) == 0:
                print("❌ No jobs found in database")
                return 1
        else:
            print(f"\n✅ Found {len(jobs)} jobs")
        
        # Display job info
        print("\nJobs to analyze:")
        for i, job in enumerate(jobs, 1):
            print(f"  {i}. {job.title} at {job.company}")
        
        # Prepare job IDs
        job_ids = [job.id for job in jobs]
        job_ids_json = json.dumps(job_ids)
        
        print(f"\n{'=' * 80}")
        print("STARTING ANALYSIS...")
        print(f"{'=' * 80}")
        
        # Record start time
        start_time = time.time()
        start_datetime = datetime.now()
        print(f"\nStart time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the analysis subprocess
        import subprocess
        
        script_path = 'run_analysis_strategic.py'
        analysis_mode = 'market_intelligence'
        
        print(f"\nRunning: python {script_path}")
        print(f"  Resume ID: {resume.id}")
        print(f"  Job count: {len(jobs)}")
        print(f"  Mode: {analysis_mode}")
        print("\nThis may take several minutes...")
        print("(Progress will be shown below)\n")
        
        # Run subprocess with real-time output
        process = subprocess.Popen(
            [sys.executable, script_path, resume.id, job_ids_json, analysis_mode],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Read stderr in real-time for progress updates
        stderr_lines = []
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            if line:
                stderr_lines.append(line)
                # Print progress lines
                if any(keyword in line for keyword in ['Step', 'Loading', 'Extracting', 'Classifying', 'Analyzing', 'Generating', 'Saving']):
                    print(f"  {line.strip()}")
        
        # Get remaining output
        stdout, remaining_stderr = process.communicate()
        stderr_lines.extend(remaining_stderr.split('\n'))
        
        # Record end time
        end_time = time.time()
        end_datetime = datetime.now()
        elapsed_time = end_time - start_time
        
        print(f"\n{'=' * 80}")
        print("ANALYSIS COMPLETE")
        print(f"{'=' * 80}")
        
        print(f"\nEnd time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"Average per job: {elapsed_time/len(jobs):.2f} seconds")
        
        # Check result
        if process.returncode == 0:
            try:
                result = json.loads(stdout)
                if result.get('success'):
                    print(f"\n✅ Analysis succeeded!")
                    
                    # Show some result stats
                    if 'career_analysis' in result:
                        ca = result['career_analysis']
                        print(f"\nResults summary:")
                        if 'skill_gaps' in ca:
                            print(f"  - Skill gaps found: {len(ca['skill_gaps'])}")
                        if 'skill_matches' in ca:
                            print(f"  - Skill matches: {len(ca['skill_matches'])}")
                        if 'market_insights' in ca:
                            print(f"  - Market insights: {len(ca['market_insights'])}")
                else:
                    print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    return 1
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse result: {e}")
                print(f"Stdout (first 500 chars): {stdout[:500]}")
                return 1
        else:
            print(f"\n❌ Analysis subprocess failed with return code: {process.returncode}")
            print(f"\nError output:")
            for line in stderr_lines[-20:]:  # Last 20 lines
                if line.strip():
                    print(f"  {line.strip()}")
            return 1
        
        # Performance analysis
        print(f"\n{'=' * 80}")
        print("PERFORMANCE ANALYSIS")
        print(f"{'=' * 80}")
        
        if elapsed_time < 300:  # Less than 5 minutes
            print(f"✅ EXCELLENT: Analysis completed in under 5 minutes")
        elif elapsed_time < 600:  # Less than 10 minutes
            print(f"✅ GOOD: Analysis completed in under 10 minutes")
        elif elapsed_time < 1200:  # Less than 20 minutes
            print(f"⚠️  ACCEPTABLE: Analysis completed in under 20 minutes")
        else:
            print(f"❌ SLOW: Analysis took over 20 minutes")
        
        print(f"\nTiming breakdown:")
        print(f"  Total time: {elapsed_time:.2f}s")
        print(f"  Per job: {elapsed_time/len(jobs):.2f}s")
        print(f"  Jobs/minute: {len(jobs)/(elapsed_time/60):.2f}")
        
        # Recommendations
        print(f"\n{'=' * 80}")
        print("RECOMMENDATIONS")
        print(f"{'=' * 80}")
        
        if elapsed_time > 600:
            print("\n⚠️  Analysis is taking longer than expected. Consider:")
            print("  1. Using the simple analysis mode instead of strategic")
            print("  2. Implementing better caching for skill extraction")
            print("  3. Reducing the number of API calls")
            print("  4. Processing jobs in parallel")
        else:
            print("\n✅ Analysis performance is acceptable for production use")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(test_analysis_timing())

#!/bin/bash

# Test script for all backend endpoints
# Usage: ./test-endpoints.sh

BASE_URL="http://localhost:54321/functions/v1"

echo "🧪 Testing Backend Endpoints"
echo "=============================="
echo ""

# Test 1: target-options
echo "1️⃣  Testing GET /target-options"
curl -s "$BASE_URL/target-options" | jq '.' || echo "❌ Failed"
echo ""
echo ""

# Test 2: analyze-market-role
echo "2️⃣  Testing POST /analyze-market-role"
curl -s -X POST "$BASE_URL/analyze-market-role" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "specialty": "Backend",
    "experience_levels": ["Internship", "Entry Level"],
    "resume_file": "mock_base64_data"
  }' | jq '.' || echo "❌ Failed"
echo ""
echo ""

# Test 3: analyze-job-posting
echo "3️⃣  Testing POST /analyze-job-posting"
curl -s -X POST "$BASE_URL/analyze-job-posting" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior AI Engineer",
    "company": "TechVault AI",
    "job_description": "Build and deploy cutting-edge ML models using PyTorch and AWS.",
    "resume_file": "mock_base64_data"
  }' | jq '.' || echo "❌ Failed"
echo ""
echo ""

# Test 4: analysis-status
echo "4️⃣  Testing GET /analysis-status/:id"
curl -s "$BASE_URL/analysis-status/test-id-123" | jq '.' || echo "❌ Failed"
echo ""
echo ""

# Test 5: analysis-result
echo "5️⃣  Testing GET /analysis-result/:id"
curl -s "$BASE_URL/analysis-result/test-id-123" | jq '.' || echo "❌ Failed"
echo ""
echo ""

echo "✅ All tests completed!"

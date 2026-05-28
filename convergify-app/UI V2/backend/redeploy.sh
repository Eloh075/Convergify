#!/bin/bash

# Redeploy Edge Functions with updated Gemini model
# Run this after setting Gemini API keys in Supabase dashboard

echo "Redeploying Edge Functions..."

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Error: Supabase CLI not found. Install it first:"
    echo "npm install -g supabase"
    exit 1
fi

# Redeploy functions
echo "Deploying analyze-market-role..."
supabase functions deploy analyze-market-role --project-ref wpvavxzfbulwrnyrcmnz

echo "Deploying analyze-job-posting..."
supabase functions deploy analyze-job-posting --project-ref wpvavxzfbulwrnyrcmnz

echo "Done! All functions redeployed with gemini-2.5-flash"

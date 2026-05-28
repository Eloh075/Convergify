#!/bin/bash

# Test runner for resume-extractor preservation tests
# This script runs the preservation property tests on the UNFIXED code
# to establish baseline behavior that must be preserved after the fix.

echo "=========================================="
echo "Running Preservation Property Tests"
echo "=========================================="
echo ""
echo "These tests verify baseline behavior for:"
echo "  - Plain text resume extraction"
echo "  - UTF-8 special character handling"
echo "  - Truncation logic"
echo "  - Error handling"
echo ""
echo "EXPECTED OUTCOME: All preservation tests should PASS"
echo "This confirms the baseline behavior to preserve after implementing the fix."
echo ""
echo "=========================================="
echo ""

# Run only the preservation tests (skip the bug condition test that will fail)
deno test --allow-read --allow-env --filter "Preservation" resume-extractor.test.ts

echo ""
echo "=========================================="
echo "Test run complete!"
echo "=========================================="

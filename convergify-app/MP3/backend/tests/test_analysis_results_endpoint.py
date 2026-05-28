#!/usr/bin/env python3
"""
Integration test for analysis results endpoint
Tests Requirements 11.1 and 11.2 from analysis-results-dashboard-redesign spec

This test verifies:
- Endpoint returns 200 status for valid analysis ID
- Response includes all required top-level fields
- skill_matches array contains required fields
- skill_gaps array contains required fields
- Error cases (invalid ID, analysis not found, analysis not completed)
"""
import pytest
import sys
import json
from datetime import datetime
from fastapi.testclient import TestClient

# Add parent directory to path for imports
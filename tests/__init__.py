"""Test suite for Habit Tracker Application

This package contains test modules for:
- Models (habit, task, analytics)
- Controllers (habit, task, analytics)
- Database operations
- Analytics calculations

Test Configuration:
- Uses pytest framework
- Separate test database
- Isolated test environments
"""

import os
import sys

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Test configuration
TEST_DB = "test.db"
ITEMS_PER_PAGE = 15
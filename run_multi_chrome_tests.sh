#!/bin/bash
# Script to run tests on 2 different Chrome versions
# Usage: ./run_multi_chrome_tests.sh [test_path]
# Example: ./run_multi_chrome_tests.sh tests/e2e/

set -e

# Default to e2e tests if no path provided
TEST_PATH="${1:-tests/e2e/}"

echo "============================================"
echo "Running E2E Tests on Multiple Chrome Versions"
echo "============================================"
echo "Test Path: $TEST_PATH"
echo ""

# Create reports directory
mkdir -p reports

# Run tests on Chrome Stable
echo "[1/2] Running tests on Chrome Stable..."
echo "----------------------------------------"
pytest "$TEST_PATH" --browser chromium --browser-channel chrome -v --html=reports/chrome-stable-report.html --self-contained-html
CHROME_STABLE_EXIT=$?
echo "Chrome Stable tests completed with exit code: $CHROME_STABLE_EXIT"
echo ""

# Run tests on Chrome Beta
echo "[2/2] Running tests on Chrome Beta..."
echo "----------------------------------------"
pytest "$TEST_PATH" --browser chromium --browser-channel chrome-beta -v --html=reports/chrome-beta-report.html --self-contained-html
CHROME_BETA_EXIT=$?
echo "Chrome Beta tests completed with exit code: $CHROME_BETA_EXIT"
echo ""

# Summary
echo "============================================"
echo "Test Execution Summary"
echo "============================================"
echo "Chrome Stable: $CHROME_STABLE_EXIT (0 = Pass, 1 = Fail)"
echo "Chrome Beta:   $CHROME_BETA_EXIT (0 = Pass, 1 = Fail)"
echo ""
echo "Reports generated:"
echo "- reports/chrome-stable-report.html"
echo "- reports/chrome-beta-report.html"
echo "============================================"

# Exit with failure if any test suite failed
if [ $CHROME_STABLE_EXIT -ne 0 ] || [ $CHROME_BETA_EXIT -ne 0 ]; then
    echo "Some tests failed!"
    exit 1
fi

echo "All tests passed successfully!"
exit 0

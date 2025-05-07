#!/bin/bash
# Clean previous coverage data
rm -f /tmp/.coverage*
rm -rf /tmp/renx_coverage

# Run tests with coverage
python -m pytest tests/ \
  --cov=renx \
  --cov-append \
  --cov-report=term-missing

# Combine all coverage data
python -m coverage combine

# Generate HTML report in /tmp
python -m coverage html \
  --directory=/tmp/renx_coverage \
  --title="renx Coverage Report"

echo "Coverage report generated at: /tmp/renx_coverage/index.html"
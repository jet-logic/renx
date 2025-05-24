#!/bin/bash
# Clean previous coverage data
NAME=$(basename $(realpath .))
DOCS=/tmp/"$NAME"_coverage
export COVERAGE_FILE=/tmp/."$NAME"_coverage
echo @@ "<$NAME>"
rm -f "$COVERAGE_FILE"*
rm -rf $DOCS
# export PYTEST_DEBUG=1
# Run tests with coverage
python -m pytest tests/ \
  --cov=$NAME \
  --cov-append \
  --cov-report=term-missing || exit 1

echo @@ Combine all coverage data $COVERAGE_FILE
python -m coverage combine

echo @@ Generate HTML report in $DOCS
python -m coverage html \
  --directory="$DOCS" \
  --title="$NAME Coverage Report"

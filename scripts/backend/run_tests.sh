echo "running unit tests"
uv run pytest
echo "generating coverage report"
uv run coverage json
echo "checking branch and line coverage thresholds"
uv run coverage-threshold
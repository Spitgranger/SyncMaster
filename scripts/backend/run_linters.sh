echo "checking formatting errors"
uv run ruff format --check
echo "checking imports sorted"
uv run ruff check
echo "running pylint on source code"
uv run pylint ./src/backend/
echo "checking common security vulnerabilities on source code"
uv run bandit -r ./src/backend/
echo "running type checker"
uv run mypy ./src/backend/
echo "checking cloudformation template"
uv run cfn-lint ./infrastructure/backend.yaml -f parseable

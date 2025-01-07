echo "running ruff formatter"
uv run ruff format
echo "fixing incorrectly sorted imports"
uv run ruff check --fix
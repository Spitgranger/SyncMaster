uv export --frozen --no-emit-workspace --no-dev --no-editable -o ./src/backend/requirements.txt
sam.cmd build --template-file ./infrastructure/backend.yaml --use-container --build-image public.ecr.aws/sam/build-python3.13

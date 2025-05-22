#!/bin/zsh

# Enable Docker BuildKit optimizations
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Initialize builder instance
docker buildx create --use --name=arm64_builder 2>/dev/null || true

# Build with ARM64 optimizations
docker buildx build --platform linux/arm64 \
  -t sriram9217/fastapi-app:latest \
  -f fastapi_app/Dockerfile \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg UVICORN_WORKERS=4 \
  --cache-from type=registry,ref=sriram9217/fastapi-app:buildcache \
  --cache-to type=registry,ref=sriram9217/fastapi-app:buildcache,mode=max \
  --push \
  fastapi_app/

# Verify the pushed image
docker pull sriram9217/fastapi-app:latest
docker inspect sriram9217/fastapi-app:latest | jq '.[].Architecture'
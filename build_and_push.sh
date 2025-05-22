#!/bin/zsh

# Enable M3 optimizations
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
eval $(minikube docker-env)

# Create builder instance if missing
docker buildx create --use --name=m3_builder 2>/dev/null || true

# Build with ARM64 optimizations
docker buildx build --platform linux/arm64 \
  -t sriram9217/fastapi-app:latest \
  -f fastapi_app/Dockerfile \  # Explicit Dockerfile path
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg UVICORN_WORKERS=4 \
  --cache-from type=registry,ref=sriram9217/fastapi-app:buildcache \
  --cache-to type=registry,ref=sriram9217/fastapi-app:buildcache,mode=max \
  --load \
  fastapi_app/

# Push to registry (separate from build)
docker push sriram9217/fastapi-app:latest

# Update build cache
docker buildx build --platform linux/arm64 \
  -t sriram9217/fastapi-app:buildcache \
  -f fastapi_app/Dockerfile \
  --target builder \
  --push \
  fastapi_app/
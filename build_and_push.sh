#!/bin/zsh

# Enable M3-specific Docker optimizations
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
eval $(minikube docker-env)

# Build with ARM64 optimizations for M3
docker buildx build --platform linux/arm64 \
  -t sriram9217/fastapi-app:latest \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg UVICORN_WORKERS=4 \
  --load \
  fastapi_app/

# Push with cache optimization (for CI/CD)
docker push sriram9217/fastapi-app:latest \
  --cache-from type=registry,ref=sriram9217/fastapi-app:buildcache \
  --cache-to type=registry,ref=sriram9217/fastapi-app:buildcache,mode=max

# Verify Minikube image load
if minikube image ls | grep -q "sriram9217/fastapi-app"; then
  echo "✅ Successfully built and pushed M3-optimized image to Minikube"
else
  echo "❌ Image not found in Minikube!" >&2
  exit 1
fi
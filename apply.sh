#!/bin/bash

# Apply Kubernetes configurations
kubectl apply -f k8s-configmap.yaml
kubectl apply -f k8s-fastapi.yaml
kubectl apply -f k8s-postgres.yaml
kubectl apply -f k8s-redis.yaml
kubectl apply -f k8s-secrets.yaml
kubectl apply -f k8s-fastapi-hpa.yaml

echo "All configurations applied successfully."
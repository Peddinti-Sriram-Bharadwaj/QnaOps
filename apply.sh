#!/bin/bash

# This script applies all necessary Kubernetes configurations.
# This script applies all necessary Kubernetes configurations in the correct order.

echo "Applying Kubernetes configurations..."

# Apply Secrets
kubectl apply -f k8s-secrets.yaml
# 1. Apply Persistent Volume (PV)
echo "Applying Persistent Volume (model-storage-pv)..."
kubectl apply -f k8s-model-pv.yaml

# Apply ConfigMap
kubectl apply -f k8s-configmap.yaml
# 2. Apply Persistent Volume Claim (PVC)
echo "Applying Persistent Volume Claim (model-storage-pvc)..."
kubectl apply -f k8s-model-pvc.yaml
echo "Waiting for PVC (model-storage-pvc) to be bound..."
# It might take a few moments for the PVC to bind to the PV
kubectl wait --for=condition=Bound pvc/model-storage-pvc --timeout=60s

# Apply PostgreSQL (if used)
# 3. Apply Secrets
echo "Applying Secrets (k8s-secrets.yaml)..."
kubectl apply -f k8s-secrets.yaml

# 4. Apply ConfigMap
echo "Applying ConfigMap (k8s-configmap.yaml)..."
kubectl apply -f k8s-configmap.yaml

# 5. Apply PostgreSQL (if your FastAPI app uses it)
# kubectl apply -f k8s-postgres.yaml
# echo "Waiting for PostgreSQL to be ready..."
# kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Apply Redis (if used)
# 6. Apply Redis (if your FastAPI app uses it)
# kubectl apply -f k8s-redis.yaml
# echo "Waiting for Redis to be ready..."
# kubectl wait --for=condition=ready pod -l app=redis --timeout=300s

# Apply FastAPI App
# 7. Apply FastAPI App Deployment and Service
echo "Applying FastAPI application (k8s-fastapi.yaml)..."
kubectl apply -f k8s-fastapi.yaml

echo "Deployment complete. To access the FastAPI service (if LoadBalancer):"
echo "minikube service fastapi-service"
echo ""
echo "---------------------------------------------------------------------"
echo "Kubernetes configurations applied."
echo "---------------------------------------------------------------------"
echo ""
echo "Next steps:"
echo "1. Monitor pod startup: kubectl get pods -l app=fastapi-app -w"
echo "2. Check init container logs (for model download): kubectl logs <fastapi-pod-name> -c download-model -f"
echo "3. Check main container logs: kubectl logs <fastapi-pod-name> -c fastapi-app -f"
echo "4. Access the service (if LoadBalancer type and using Minikube): minikube service fastapi-service"
echo "---------------------------------------------------------------------"
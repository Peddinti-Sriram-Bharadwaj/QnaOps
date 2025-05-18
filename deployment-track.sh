#!/bin/bash
# Tracks the rollout status of a specified deployment.
# Usage: ./deployment-track.sh <deployment-name> [namespace]

DEPLOYMENT_NAME=$1
NAMESPACE=${2:-default} # Default to 'default' namespace if not provided

if [ -z "$DEPLOYMENT_NAME" ]; then
  echo "Error: Deployment name not specified."
  echo "Usage: ./deployment-track.sh <deployment-name> [namespace]"
  exit 1
fi

echo "Tracking rollout status for deployment '$DEPLOYMENT_NAME' in namespace '$NAMESPACE'..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE -w

echo "Rollout for deployment '$DEPLOYMENT_NAME' complete or timed out."
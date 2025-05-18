#!/bin/bash
# Displays Horizontal Pod Autoscaler (HPA) status.
# Usage: ./hpa-usage.sh [hpa-name] [namespace]
# If no hpa-name is provided, lists all HPAs in the namespace.

HPA_NAME=$1
NAMESPACE=${2:-default} # Default to 'default' namespace if not provided

if [ -z "$HPA_NAME" ]; then
  echo "Listing all HPAs in namespace '$NAMESPACE':"
  kubectl get hpa -n $NAMESPACE
else
  echo "Displaying status for HPA '$HPA_NAME' in namespace '$NAMESPACE':"
  kubectl get hpa $HPA_NAME -n $NAMESPACE -o wide
  echo ""
  echo "Describing HPA '$HPA_NAME' in namespace '$NAMESPACE':"
  kubectl describe hpa $HPA_NAME -n $NAMESPACE
fi
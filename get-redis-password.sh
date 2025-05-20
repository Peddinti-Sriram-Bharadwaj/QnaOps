kubectl get secret redis-secret -o jsonpath="{.data.REDIS_PASSWORD}" | base64 --decode

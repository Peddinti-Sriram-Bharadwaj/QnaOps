kubectl get secret postgres-secret -o jsonpath="{.data.POSTGRES_DB}" | base64 --decode

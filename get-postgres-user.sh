kubectl get secret postgres-secret -o jsonpath="{.data.POSTGRES_USER}" | base64 --decode

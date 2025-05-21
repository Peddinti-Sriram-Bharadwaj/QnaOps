pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = "1"
        REGISTRY = "docker.io/sriram9217" // or your image registry if using one
        VAULT_PASS = credentials('vault-pass-id') // Jenkins secret text for vault_pass.txt
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/Peddinti-Sriram-Bharadwaj/QnaOps'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh './build_and_push.sh'
            }
        }

        stage('Apply Secrets via Ansible Vault') {
            steps {
                sh '''
                export ANSIBLE_VAULT_PASSWORD_FILE=ansible/vault_pass.txt
                echo "$VAULT_PASS" > $ANSIBLE_VAULT_PASSWORD_FILE
                ansible-playbook ansible/deploy-db.yaml
                ansible-playbook ansible/deploy-fastapi-nginx.yaml
                '''
            }
        }

        stage('Deploy ELK Stack') {
            steps {
                sh '''
                export ANSIBLE_VAULT_PASSWORD_FILE=ansible/vault_pass.txt
                ansible-playbook ansible/elastic_stack_setup.yaml
                '''
            }
        }

        stage('Apply Kubernetes Manifests') {
            steps {
                sh '''
                kubectl apply -f k8s/postgres.yaml
                kubectl apply -f k8s/redis.yaml
                kubectl apply -f k8s/nginx-configmap.yaml
                kubectl apply -f k8s/fastapi-deployment.yaml
                kubectl apply -f k8s/nginx-deployment.yaml
                '''
            }
        }

        stage('Rolling Restart') {
            steps {
                sh '''
                kubectl rollout restart deployment fastapi
                kubectl rollout restart deployment nginx
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful.'
            sh '''
            nohup ./get-url.sh > get-url.log 2>&1 &
            echo "Started get-url.sh in the background."
            echo "Check the URL inside get-url.log."
            echo "Keep this tunnel running externally (e.g. terminal open)."
            '''
        }
        failure {
            echo '❌ Deployment failed.'
        }
    }

}

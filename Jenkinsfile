pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = "1"
        REGISTRY = "docker.io/sriram9217"
        ANSIBLE_VAULT_PASSWORD_FILE = "${WORKSPACE}/ansible/vault_pass.txt"
        KUBECTL_TIMEOUT = "120s"
        PATH = "/usr/local/bin:/opt/homebrew/bin:$PATH"  // Homebrew paths
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/Peddinti-Sriram-Bharadwaj/QnaOps'
            }
        }

        stage('Build & Push Docker Images') {
            steps {
                sh '''
                ../build_and_push.sh
                '''
            }
        }

        stage('Deploy ELK Stack') {
            steps {
                withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                    sh """
                    #!/bin/zsh
                    echo "$VAULT_PASS" > "$ANSIBLE_VAULT_PASSWORD_FILE"
                    chmod 600 "$ANSIBLE_VAULT_PASSWORD_FILE"
                    ansible-playbook ansible/elastic_stack_setup.yaml
                    """
                }
            }
        }

        stage('Deploy Database') {
            steps {
                withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                    sh """
                    #!/bin/zsh
                    echo "$VAULT_PASS" > "$ANSIBLE_VAULT_PASSWORD_FILE"
                    ansible-playbook ansible/deploy-db.yaml
                    """
                }
            }
        }

        stage('Deploy FastAPI & Nginx') {
            steps {
                withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                    sh """
                    #!/bin/zsh
                    echo "$VAULT_PASS" > "$ANSIBLE_VAULT_PASSWORD_FILE"
                    ansible-playbook ansible/deploy-fastapi-nginx.yaml
                    """
                }
            }
        }

        stage('Apply Kubernetes Manifests') {
            steps {
                sh '''
                #!/bin/zsh
                kubectl apply -f k8s/
                '''
            }
        }

        stage('Verify & Rolling Restart') {
            steps {
                sh '''
                #!/bin/zsh
                kubectl rollout status deployment/fastapi --timeout=$KUBECTL_TIMEOUT
                kubectl rollout status deployment/nginx --timeout=$KUBECTL_TIMEOUT
                kubectl rollout restart deployment fastapi
                kubectl rollout restart deployment nginx
                '''
            }
        }
    }

    post {
        always {
            sh '''
            #!/bin/zsh
            rm -f "$ANSIBLE_VAULT_PASSWORD_FILE"
            docker system prune -f --filter "until=24h" || true
            '''
            cleanWs()
        }
        failure {
            sh '''
            #!/bin/zsh
            kubectl rollout undo deployment/fastapi 2>/dev/null || true
            kubectl rollout undo deployment/nginx 2>/dev/null || true
            '''
        }
    }
}
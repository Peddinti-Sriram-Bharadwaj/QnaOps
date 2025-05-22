pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = "1"
        REGISTRY = "docker.io/sriram9217"
        ANSIBLE_VAULT_PASSWORD_FILE = "${WORKSPACE}/ansible/vault_pass.txt"  // Full path for reliability
        KUBECTL_TIMEOUT = "120s"
    }

    stages {
        // 1. Checkout Code
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/Peddinti-Sriram-Bharadwaj/QnaOps'
            }
        }

        // 2. Build & Push Docker Images
        stage('Build & Push Docker Images') {
            steps {
                script {
                    sh '''
                    #!/bin/zsh
                    ./build_and_push.sh
                    '''
                }
            }
        }

        // 3. Deploy ELK Stack
        stage('Deploy ELK Stack') {
            steps {
                script {
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
        }

        // 4. Deploy Database
        stage('Deploy Database') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                        sh """
                        #!/bin/zsh
                        echo "$VAULT_PASS" > "$ANSIBLE_VAULT_PASSWORD_FILE"
                        ansible-playbook ansible/deploy-db.yaml
                        """
                    }
                }
            }
        }

        // 5. Deploy FastAPI & Nginx
        stage('Deploy FastAPI & Nginx') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                        sh """
                        #!/bin/zsh
                        echo "$VAULT_PASS" > "$ANSIBLE_VAULT_PASSWORD_FILE"
                        ansible-playbook ansible/deploy-fastapi-nginx.yaml
                        """
                    }
                }
            }
        }

        // 6. Apply Kubernetes Manifests
        stage('Apply Kubernetes Manifests') {
            steps {
                sh '''
                #!/bin/zsh
                kubectl apply -f k8s/
                '''
            }
        }

        // 7. Verify & Rolling Restart
        stage('Verify & Rolling Restart') {
            steps {
                sh '''
                #!/bin/zsh
                kubectl rollout status deployment/fastapi --timeout=120s
                kubectl rollout status deployment/nginx --timeout=120s
                kubectl rollout restart deployment fastapi
                kubectl rollout restart deployment nginx
                '''
            }
        }
    }

    post {
        always {
            echo "🍏 Starting MacOS cleanup..."
            script {
                // 1. Secure Vault Cleanup (BSD-compatible)
                sh """
                #!/bin/zsh
                echo "Cleaning Ansible vault..."
                rm -f "$ANSIBLE_VAULT_PASSWORD_FILE"
                if [ ! -f "$ANSIBLE_VAULT_PASSWORD_FILE" ]; then
                    echo "Vault password file removed"
                else
                    echo "WARNING: Failed to remove vault file"
                fi
                """

                // 2. Docker Cleanup (MacOS Docker Desktop)
                sh '''
                #!/bin/zsh
                echo "Pruning Docker..."
                if command -v docker &> /dev/null; then
                    docker system prune -f --filter "until=24h"
                    docker volume prune -f
                else
                    echo "Docker not found (Is Docker Desktop running?)"
                fi
                '''

                // 3. Kubernetes Status Check (BSD grep)
                sh """
                #!/bin/zsh
                echo "Checking pods..."
                kubectl get pods --no-headers | grep -E -v "Running|Completed" && \\
                echo "WARNING: Non-running pods detected" || true
                """

                // 4. MacOS Temporary Files
                sh '''
                #!/bin/zsh
                echo "Cleaning MacOS temp files..."
                find . -type f -name "*.tmp" -delete
                find . -type f -name ".DS_Store" -delete
                '''
            }
        }
        failure {
            // MacOS-specific rollback
            sh '''
            #!/bin/zsh
            echo "Attempting rollback..."
            kubectl rollout undo deployment/fastapi 2>/dev/null || true
            kubectl rollout undo deployment/nginx 2>/dev/null || true
            '''
        }
        cleanup {
            // Workspace cleanup (MacOS-compatible)
            cleanWs()
        }
    }
}
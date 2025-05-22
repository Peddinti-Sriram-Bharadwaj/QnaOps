pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = "1"
        REGISTRY = "docker.io/sriram9217"  // Your Docker registry
        ANSIBLE_VAULT_PASSWORD_FILE = "ansible/vault_pass.txt"
    }

    stages {
        // 1. Checkout Code
        stage('Checkout') {
            steps {
                git branch: 'master', url: 'https://github.com/Peddinti-Sriram-Bharadwaj/QnaOps'
            }
        }

        // 2. Build & Push Docker Images (Early Failure Detection)
        stage('Build & Push Docker Images') {
            steps {
                script {
                    sh './build_and_push.sh'
                }
            }
        }

        // 3. Deploy Infrastructure (ELK Stack)
        stage('Deploy ELK Stack') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                        sh """
                        echo "$VAULT_PASS" > $ANSIBLE_VAULT_PASSWORD_FILE
                        chmod 600 $ANSIBLE_VAULT_PASSWORD_FILE  # Restrict permissions
                        ansible-playbook ansible/elastic_stack_setup.yaml
                        """
                    }
                }
            }
        }

        // 4. Deploy Database (Before App)
        stage('Deploy Database') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'vault-pass-id', variable: 'VAULT_PASS')]) {
                        sh """
                        echo "$VAULT_PASS" > $ANSIBLE_VAULT_PASSWORD_FILE
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
                        echo "$VAULT_PASS" > $ANSIBLE_VAULT_PASSWORD_FILE
                        ansible-playbook ansible/deploy-fastapi-nginx.yaml
                        """
                    }
                }
            }
        }

        // 6. Apply Kubernetes Manifests
        stage('Apply Kubernetes Manifests') {
            steps {
                sh 'kubectl apply -f k8s/'
            }
        }

        // 7. Verify & Rolling Restart (Optional)
        stage('Verify & Rolling Restart') {
            steps {
                sh '''
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
            sh "rm -f $ANSIBLE_VAULT_PASSWORD_FILE"  // Cleanup vault pass
        }
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed!'
            // Optionally send Slack/email notification
        }
    }
}
pipeline {
    agent any

    environment {
        KUBECONFIG = "${env.WORKSPACE}/.kube/config"
        IMAGE_TAG = "latest"
        VAULT_PASS_FILE = "${env.WORKSPACE}/ansible/vault_pass.txt"  // plaintext file with vault password
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Minikube Docker Env') {
            steps {
                sh 'eval $(minikube docker-env)'
            }
        }

        stage('Build Docker Images') {
            steps {
                dir('fastapi-app') {
                    sh "docker build -t fastapi-app:${IMAGE_TAG} ."
                }
                dir('nginx') {
                    sh "docker build -t nginx-frontend:${IMAGE_TAG} ."
                }
            }
        }

        stage('Run ELK Setup via Ansible') {
            steps {
                dir('ansible') {
                    sh 'ansible-playbook elastic_stack_setup.yaml'
                }
            }
        }

        stage('Deploy Postgres and Redis with Vault') {
            steps {
                dir('ansible') {
                    // Pass vault password file for decryption
                    sh "ansible-playbook deploy-db.yaml --vault-password-file ${VAULT_PASS_FILE}"
                }
            }
        }

        stage('Deploy FastAPI and NGINX') {
            steps {
                sh 'kubectl apply -f k8s/fastapi.yaml'
                sh 'kubectl apply -f k8s/nginx.yaml'
            }
        }

        stage('Check Rollouts') {
            steps {
                sh 'kubectl rollout status deployment/fastapi-app'
                sh 'kubectl rollout status deployment/nginx-frontend'
                sh 'kubectl rollout status statefulset/postgres'
                sh 'kubectl rollout status statefulset/redis'
            }
        }
    }

    post {
        failure {
            echo 'Deployment failed! Check Jenkins logs.'
        }
    }
}

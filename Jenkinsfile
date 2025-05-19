pipeline {
    agent any
    environment {
        APP_DEPLOYMENT_NAME = 'fastapi-app'
        APP_NAMESPACE = 'default'
        WORKSPACE_DIR = "${env.WORKSPACE}"
        MINIKUBE_IP = "localhost"
        MINIKUBE_PORT = "32000"
    }
    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code...'
                // Replace with your actual SCM checkout
                // git url: 'https://your-git-repository.com/your-project.git', branch: 'main'
            }
        }
        stage('Setup ELK Stack') {
            steps {
                script {
                    echo 'Configuring kubectl context...'
                    // Configure kubectl to use Minikube
                    sh '''
                        # Verify kubectl installation
                        command -v kubectl
                        
                        # Configure cluster access
                        kubectl config use-context minikube
                        
                        # Apply ELK configuration
                        kubectl apply -f elk_stack_setup.yaml
                        
                        # Wait for Elasticsearch readiness
                        echo "Waiting for Elasticsearch to be ready..."
                        kubectl wait --for=condition=Ready pod \
                            -l app=elasticsearch \
                            --timeout=300s
                        
                        echo "Waiting for Kibana to be ready..."
                        kubectl wait --for=condition=Ready pod \
                            -l app=kibana \
                            --timeout=300s
                    '''
                }
            }
        }
        stage('Build and Push Application Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh '''
                        eval $(minikube docker-env)
                        chmod +x ./build_and_push.sh
                        ./build_and_push.sh
                    '''
                }
            }
        }
        stage('Deploy Application') {
            steps {
                script {
                    echo "Deploying application..."
                    sh '''
                        chmod +x ./apply.sh ./deployment-track.sh
                        ./apply.sh
                        
                        echo "Tracking deployment status..."
                        ./deployment-track.sh ${APP_DEPLOYMENT_NAME} ${APP_NAMESPACE}
                    '''
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline execution finished.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check console output for details.'
        }
    }
}
pipeline {
    agent any // Ensure this agent has kubectl, docker, and git/scm tools installed and configured.

    environment {
        // Define your application's deployment name and namespace
        // These are used by deployment-track.sh
        // Assuming 'fastapi-app' from your apply.sh and get_pods.sh context
        APP_DEPLOYMENT_NAME = 'fastapi-app'
        APP_NAMESPACE = 'default' // Adjust if your application is in a different namespace
        // Define namespace for ELK if it's specific and needed for waits
        WORKSPACE_DIR = "${env.WORKSPACE}" // Define WORKSPACE_DIR using Jenkins built-in variable
        // ELK_NAMESPACE = 'elastic-system'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code...'
                // Replace with your actual SCM checkout, e.g., Git
                // git url: 'https://your-git-repository.com/your-project.git', branch: 'main'
            }
        }


        stage('Setup ELK Stack') {
            steps {
                script {
                    echo 'Applying ELK Stack configuration from elk_stack_setup.yaml...'
                    // Ensure elk_stack_setup.yaml is in the workspace
                    sh 'kubectl apply -f elk_stack_setup.yaml'

                    // IMPORTANT: ELK components can take a significant time to initialize.
                    // For a true "ready" state, you should add 'kubectl wait' commands
                    // for your specific Elasticsearch, Kibana, etc. deployments/statefulsets.
                    // Define ELK_NAMESPACE in the environment block if used.
                    // Example (adjust names, kinds, labels, and namespaces as per your elk_stack_setup.yaml):
                    // echo "Waiting for Elasticsearch to be ready..."
                    // sh "kubectl wait --for=condition=Ready pod -l app=elasticsearch -n elastic-system --timeout=10m"
                    // sh "kubectl wait --for=condition=ready pod -l app=kibana -n ${env.ELK_NAMESPACE} --timeout=5m"

                    echo 'ELK monitoring setup has been initiated. Components may take some time to become fully operational.'
                }
            }
        }

        stage('Build and Push Application Image') {
            steps {
                echo 'Building and pushing application Docker image...'
                // Consider adding Docker login steps here if pushing to a private registry
                // or using Jenkins credentials for Docker Hub.
                // Ensure Docker is configured on the Jenkins agent and can push to the specified repository.
                sh 'chmod +x ./build_and_push.sh'
                sh './build_and_push.sh'
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying application using apply.sh..."
                sh 'chmod +x ./apply.sh ./deployment-track.sh'
                sh './apply.sh'

                echo "Tracking application deployment status for '${env.APP_DEPLOYMENT_NAME}' in namespace '${env.APP_NAMESPACE}'..."
                sh "./deployment-track.sh ${env.APP_DEPLOYMENT_NAME} ${env.APP_NAMESPACE}"
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
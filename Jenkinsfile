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
                // This step depends on your SCM setup (e.g., Git)
                // Example: git url: 'https://your-git-repository.com/project.git', branch: 'main'
                echo 'Code checkout placeholder. Configure your SCM checkout here.'
                // Ensure all scripts (build_and_push.sh, apply.sh, deployment-track.sh)
                // and YAML files (elk_stack_setup.yaml) are available in the workspace.
            }
        }

        stage('Fix Jenkins Docker & Minikube Permissions') {
            steps {
                sh '''
                echo "🛠️ Fixing Jenkins user permissions..."

                # Add Jenkins to docker group
                # This command might require a restart of the Jenkins agent process or a new login session
                # for the group membership to take effect. This might not be effective immediately
                # within the same pipeline run if the agent isn't restarted.
                sudo usermod -aG docker jenkins || echo "Could not add jenkins to docker group, or already a member. This might require manual intervention or agent restart."

                # Create required directories for minikube & kube if not present
                echo "Creating .kube and .minikube directories in ${WORKSPACE_DIR}"
                sudo mkdir -p ${WORKSPACE_DIR}/.kube
                sudo mkdir -p ${WORKSPACE_DIR}/.minikube

                # Set ownership and permissions
                echo "Setting ownership and permissions for .kube and .minikube directories in ${WORKSPACE_DIR}"
                sudo chown -R jenkins:jenkins ${WORKSPACE_DIR}/.kube      # Typically jenkins user/group
                sudo chown -R jenkins:jenkins ${WORKSPACE_DIR}/.minikube   # Typically jenkins user/group
                sudo chmod -R u+wrx ${WORKSPACE_DIR}/.kube
                sudo chmod -R u+wrx ${WORKSPACE_DIR}/.minikube
                '''
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
                    // for your specific Elasticsearch, Kibana, etc., deployments/statefulsets.
                    // Example (adjust names, kinds, and namespaces as per your elk_stack_setup.yaml):
                    // sh "kubectl wait --for=condition=ready pod -l app=elasticsearch -n ${env.ELK_NAMESPACE} --timeout=10m"
                    // sh "kubectl wait --for=condition=ready pod -l app=kibana -n ${env.ELK_NAMESPACE} --timeout=5m"

                    echo 'ELK monitoring setup has been initiated. Components may take some time to become fully operational.'
                }
            }
        }

        stage('Build and Push Application Image') {
            steps {
                echo 'Building and pushing application Docker image...'
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
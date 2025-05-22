pipeline {
    agent any
    
    environment {
        DOCKER_BUILDKIT = "1"
        REGISTRY = "docker.io/sriram9217"
        VAULT_PASS = credentials('vault-pass-id')
        KUBECONFIG = credentials('kubeconfig-file-id')
        BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
        NAMESPACE = "default" // Make this configurable
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        retry(2)
        skipDefaultCheckout(true)
    }
    
    stages {
        stage('Checkout & Validate') {
            steps {
                script {
                    // Clean checkout
                    checkout scm
                    
                    // Validate required files exist
                    sh '''
                        if [ ! -f "./build_and_push.sh" ]; then
                            echo "❌ build_and_push.sh not found"
                            exit 1
                        fi
                        if [ ! -d "ansible" ]; then
                            echo "❌ ansible directory not found"
                            exit 1
                        fi
                        if [ ! -d "k8s" ]; then
                            echo "❌ k8s directory not found"
                            exit 1
                        fi
                        echo "✅ All required files present"
                    '''
                }
            }
        }
        
        stage('Build & Test Docker Images') {
            steps {
                script {
                    try {
                        // Make build script executable and run
                        sh '''
                            chmod +x ./build_and_push.sh
                            ./build_and_push.sh
                        '''
                        
                        // Verify images were built successfully
                        sh '''
                            echo "🔍 Verifying built images..."
                            docker images | grep "${REGISTRY}" || {
                                echo "❌ No images found with registry ${REGISTRY}"
                                exit 1
                            }
                        '''
                    } catch (Exception e) {
                        error "❌ Docker build failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Infrastructure Setup') {
            parallel {
                stage('Deploy ELK Stack') {
                    steps {
                        script {
                            // Create temporary vault file securely
                            sh '''
                                TEMP_VAULT=$(mktemp)
                                echo "$VAULT_PASS" > "$TEMP_VAULT"
                                chmod 600 "$TEMP_VAULT"
                                
                                export ANSIBLE_VAULT_PASSWORD_FILE="$TEMP_VAULT"
                                export ANSIBLE_HOST_KEY_CHECKING=False
                                
                                ansible-playbook ansible/elastic_stack_setup.yaml \
                                    --diff \
                                    --check-mode || echo "Dry run completed"
                                
                                ansible-playbook ansible/elastic_stack_setup.yaml \
                                    --diff
                                
                                # Clean up
                                rm -f "$TEMP_VAULT"
                            '''
                        }
                    }
                }
                
                stage('Validate Kubernetes Connection') {
                    steps {
                        sh '''
                            kubectl cluster-info
                            kubectl get nodes
                            kubectl get ns ${NAMESPACE} || kubectl create ns ${NAMESPACE}
                        '''
                    }
                }
            }
        }
        
        stage('Deploy Application Components') {
            steps {
                script {
                    // Create temporary vault file for database deployment
                    sh '''
                        TEMP_VAULT=$(mktemp)
                        echo "$VAULT_PASS" > "$TEMP_VAULT"
                        chmod 600 "$TEMP_VAULT"
                        
                        export ANSIBLE_VAULT_PASSWORD_FILE="$TEMP_VAULT"
                        export ANSIBLE_HOST_KEY_CHECKING=False
                        
                        echo "🚀 Deploying database components..."
                        ansible-playbook ansible/deploy-db.yaml --diff
                        
                        echo "🚀 Deploying FastAPI and Nginx..."
                        ansible-playbook ansible/deploy-fastapi-nginx.yaml --diff \
                            --extra-vars "image_tag=${BUILD_VERSION}"
                        
                        # Clean up
                        rm -f "$TEMP_VAULT"
                    '''
                }
            }
        }
        
        stage('Apply Kubernetes Manifests') {
            steps {
                script {
                    // Apply manifests with validation (no backup files needed)
                    sh '''
                        echo "🔍 Validating Kubernetes manifests..."
                        kubectl apply --dry-run=client -f k8s/
                        
                        echo "🚀 Applying Kubernetes manifests..."
                        kubectl apply -f k8s/ --record
                        
                        # Wait for rollout to start
                        sleep 10
                    '''
                }
            }
        }
        
        stage('Rolling Update & Health Check') {
            steps {
                script {
                    try {
                        sh '''
                            echo "🔄 Performing rolling restart..."
                            
                            # Check if deployments exist before restarting
                            if kubectl get deployment fastapi -n ${NAMESPACE} >/dev/null 2>&1; then
                                kubectl rollout restart deployment/fastapi -n ${NAMESPACE}
                                kubectl rollout status deployment/fastapi -n ${NAMESPACE} --timeout=300s
                            else
                                echo "⚠️ FastAPI deployment not found, skipping restart"
                            fi
                            
                            if kubectl get deployment nginx -n ${NAMESPACE} >/dev/null 2>&1; then
                                kubectl rollout restart deployment/nginx -n ${NAMESPACE}
                                kubectl rollout status deployment/nginx -n ${NAMESPACE} --timeout=300s
                            else
                                echo "⚠️ Nginx deployment not found, skipping restart"
                            fi
                        '''
                        
                        // Health checks
                        sh '''
                            echo "🏥 Performing health checks..."
                            
                            # Wait for pods to be ready
                            kubectl wait --for=condition=ready pod -l app=fastapi -n ${NAMESPACE} --timeout=300s || {
                                echo "❌ FastAPI pods not ready"
                                kubectl describe pods -l app=fastapi -n ${NAMESPACE}
                                exit 1
                            }
                            
                            kubectl wait --for=condition=ready pod -l app=nginx -n ${NAMESPACE} --timeout=300s || {
                                echo "❌ Nginx pods not ready"
                                kubectl describe pods -l app=nginx -n ${NAMESPACE}
                                exit 1
                            }
                            
                            echo "✅ All pods are ready"
                        '''
                    } catch (Exception e) {
                        error "❌ Deployment health check failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Smoke Tests') {
            steps {
                script {
                    sh '''
                        echo "🧪 Running smoke tests..."
                        
                        # Get service endpoints
                        FASTAPI_URL=$(kubectl get svc fastapi-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
                        NGINX_URL=$(kubectl get svc nginx-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
                        
                        # Basic connectivity tests
                        if kubectl get svc fastapi-service -n ${NAMESPACE} >/dev/null 2>&1; then
                            kubectl exec -n ${NAMESPACE} $(kubectl get pod -l app=fastapi -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}') -- curl -f http://localhost:8000/health || {
                                echo "❌ FastAPI health check failed"
                                exit 1
                            }
                        fi
                        
                        echo "✅ Smoke tests passed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            // Clean up temporary files and resources
            sh '''
                docker system prune -f 2>/dev/null || true
            '''
        }
        
        success {
            echo '''
                ✅ Deployment successful!
                
                📊 Deployment Summary:
                - Build Version: ${BUILD_VERSION}
                - Namespace: ${NAMESPACE}
                - Registry: ${REGISTRY}
            '''
            
            // Send success notification (if configured)
            // slackSend(color: 'good', message: "✅ Deployment successful for ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        
        failure {
            echo '''
                ❌ Deployment failed!
                
                🔄 Attempting automatic rollback...
            '''
            
            script {
                try {
                    // Use Kubernetes native rollback instead of backup files
                    sh '''
                        echo "🔄 Rolling back to previous revision..."
                        
                        # Check if deployments exist and have rollout history
                        if kubectl get deployment fastapi -n ${NAMESPACE} >/dev/null 2>&1; then
                            FASTAPI_REVISION=$(kubectl rollout history deployment/fastapi -n ${NAMESPACE} | tail -n 2 | head -n 1 | awk '{print $1}')
                            if [ ! -z "$FASTAPI_REVISION" ] && [ "$FASTAPI_REVISION" -gt 1 ]; then
                                echo "Rolling back FastAPI to revision $((FASTAPI_REVISION-1))..."
                                kubectl rollout undo deployment/fastapi -n ${NAMESPACE}
                                kubectl rollout status deployment/fastapi -n ${NAMESPACE} --timeout=180s
                            else
                                echo "⚠️ No previous FastAPI revision to rollback to"
                            fi
                        fi
                        
                        if kubectl get deployment nginx -n ${NAMESPACE} >/dev/null 2>&1; then
                            NGINX_REVISION=$(kubectl rollout history deployment/nginx -n ${NAMESPACE} | tail -n 2 | head -n 1 | awk '{print $1}')
                            if [ ! -z "$NGINX_REVISION" ] && [ "$NGINX_REVISION" -gt 1 ]; then
                                echo "Rolling back Nginx to revision $((NGINX_REVISION-1))..."
                                kubectl rollout undo deployment/nginx -n ${NAMESPACE}
                                kubectl rollout status deployment/nginx -n ${NAMESPACE} --timeout=180s
                            else
                                echo "⚠️ No previous Nginx revision to rollback to"
                            fi
                        fi
                        
                        echo "✅ Rollback completed using Kubernetes rollout history"
                    '''
                } catch (Exception e) {
                    echo "❌ Rollback also failed: ${e.getMessage()}"
                    
                    // As last resort, try to delete failed pods to trigger recreation
                    try {
                        sh '''
                            echo "🚨 Last resort: Deleting failing pods..."
                            kubectl delete pods -l app=fastapi -n ${NAMESPACE} --force --grace-period=0 2>/dev/null || true
                            kubectl delete pods -l app=nginx -n ${NAMESPACE} --force --grace-period=0 2>/dev/null || true
                        '''
                    } catch (Exception e2) {
                        echo "❌ Even pod deletion failed: ${e2.getMessage()}"
                    }
                }
            }
            
            // Send failure notification (if configured)
            // slackSend(color: 'danger', message: "❌ Deployment failed for ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        
        unstable {
            echo '⚠️ Deployment completed with warnings.'
        }
    }
}
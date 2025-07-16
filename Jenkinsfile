pipeline {
    agent any
    
    environment {
        CDE_AWS_REGION = credentials('cde-aws-region')
        CDE_ECR_REGISTRY = credentials('cde-ecr-registry')
        CDE_ECR_REPO_NAME = credentials('cde-ecr-repo-name')
        PROD_APPRUNNER_SERVICE_ARN = credentials('prod-apprunner-service-arn')
        STAGING_APPRUNNER_SERVICE_ARN = credentials('staging-apprunner-service-arn')
        CDE_APP_PORT = credentials('cde-app-port')
        TRIVY_SEVERITY = credentials('trivy-severity-threshold')
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    try {
                        def gitUser = env.CHANGE_AUTHOR ?: env.GIT_AUTHOR_NAME ?: sh(script: 'git log -1 --pretty=format:"%an"', returnStdout: true).trim()
                        slackSend(color: '#FFFF00', 
                            message: """BUILD STARTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'
*Triggered By:* `${gitUser}`
*Branch:* `${env.BRANCH_NAME}`
- CDE Registry deployment in progress!""".stripIndent()
                        )
                        checkout scm
                    } catch (Exception e) {
                        slackSend(color: '#FF0000', message: "Stage 'Checkout' FAILED: ${e.getMessage()}")
                        throw e
                    }
                }
            }
        }
        
        stage('Set Environment Variables') {
            steps {
                script {
                    env.IMAGE_TAG = "${env.BRANCH_NAME}-${env.GIT_COMMIT.take(7)}"
                    
                    if (env.BRANCH_NAME == 'main') {
                        env.APPRUNNER_SERVICE_ARN = "${PROD_APPRUNNER_SERVICE_ARN}"
                    } else if (env.BRANCH_NAME == 'staging') {
                        env.APPRUNNER_SERVICE_ARN = "${STAGING_APPRUNNER_SERVICE_ARN}"
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        slackSend(color: '#0099FF', message: "🔨 Building Docker image: ${IMAGE_TAG}")
                        sh """
                            docker build -t ${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG} .
                        """
                        slackSend(color: 'good', message: "✅ Docker image built successfully: ${IMAGE_TAG}")
                    } catch (Exception e) {
                        slackSend(color: '#FF0000', message: "Stage 'Build Docker Image' FAILED: ${e.getMessage()}")
                        throw e
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    try {
                        slackSend(color: '#0099FF', message: "🔍 Running security scan with Trivy...")
                        script {
                            def imageRef = "${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}"
                            def severity = "${TRIVY_SEVERITY}"
                            
                            sh """
                                # Create reports directory
                                mkdir -p reports
                                
                                # Run Trivy scan and save results
                                trivy image --format json --output reports/trivy-report.json ${imageRef}
                                
                                # Run Trivy scan with severity threshold (will fail build if critical/high vulnerabilities found)
                                echo "Scanning image: ${imageRef}"
                                trivy image --severity ${severity} --exit-code 1 ${imageRef}
                            """
                        }
                        slackSend(color: 'good', message: "✅ Security scan passed - no critical vulnerabilities found")
                    } catch (Exception e) {
                        slackSend(color: '#FF0000', message: "🚨 Security scan FAILED: Critical vulnerabilities detected! ${e.getMessage()}")
                        // Archive the scan report for review
                        archiveArtifacts artifacts: 'reports/trivy-report.json', allowEmptyArchive: true
                        throw e
                    }
                }
            }
            post {
                always {
                    // Always archive scan results for review
                    archiveArtifacts artifacts: 'reports/trivy-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'cde-aws-credentials']]) {
                    script {
                        try {
                            slackSend(color: '#0099FF', message: "📤 Pushing image to ECR: ${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}")
                            sh """
                                aws ecr get-login-password --region ${CDE_AWS_REGION} | docker login --username AWS --password-stdin ${CDE_ECR_REGISTRY}
                                docker push ${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}
                            """
                            slackSend(color: 'good', message: "✅ Image pushed to ECR successfully")
                        } catch (Exception e) {
                            slackSend(color: '#FF0000', message: "Stage 'Push to ECR' FAILED: ${e.getMessage()}")
                            throw e
                        }
                    }
                }
            }
        }
        
        stage('Update App Runner') {
            when {
                anyOf {
                    branch 'main'
                    branch 'staging'
                }
            }
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'cde-aws-credentials']]) {
                    script {
                        try {
                            def environment = env.BRANCH_NAME == 'main' ? 'Production' : 'Staging'
                            slackSend(color: '#0099FF', message: "🚀 Updating App Runner service for ${environment} environment")
                            sh """
                                echo "Disabling auto-deployment and updating image..."
                                
                                aws apprunner update-service \\
                                    --service-arn ${APPRUNNER_SERVICE_ARN} \\
                                    --source-configuration '{"ImageRepository":{"ImageIdentifier":"${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}","ImageConfiguration":{"Port":"'${CDE_APP_PORT}'"},"ImageRepositoryType":"ECR"},"AutoDeploymentsEnabled":false}' \\
                                    --region ${CDE_AWS_REGION} \\
                                    --no-cli-pager
                            """
                            slackSend(color: 'good', message: "✅ App Runner service updated for ${environment}")
                        } catch (Exception e) {
                            slackSend(color: '#FF0000', message: "Stage 'Update App Runner' FAILED: ${e.getMessage()}")
                            throw e
                        }
                    }
                }
            }
        }
        
        stage('Check Deployment Status') {
            when {
                anyOf {
                    branch 'main'
                    branch 'staging'
                }
            }
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'cde-aws-credentials']]) {
                    script {
                        try {
                            def environment = env.BRANCH_NAME == 'main' ? 'Production' : 'Staging'
                            slackSend(color: '#0099FF', message: "⏳ Waiting for ${environment} deployment to complete (4 minutes)...")
                            script {
                                def maxAttempts = 24
                                def attempt = 0
                                def serviceStatus = ''
                                
                                while (attempt < maxAttempts) {
                                    attempt++
                                    serviceStatus = sh(
                                        script: "aws apprunner describe-service --service-arn ${APPRUNNER_SERVICE_ARN} --query 'Service.Status' --output text --region ${CDE_AWS_REGION}",
                                        returnStdout: true
                                    ).trim()
                                    
                                    echo "Attempt ${attempt}/${maxAttempts}: Service Status: ${serviceStatus}"
                                    
                                    if (serviceStatus == 'RUNNING') {
                                        def imageUri = sh(
                                            script: "aws apprunner describe-service --service-arn ${APPRUNNER_SERVICE_ARN} --query 'Service.SourceConfiguration.ImageRepository.ImageIdentifier' --output text --region ${CDE_AWS_REGION}",
                                            returnStdout: true
                                        ).trim()
                                        echo "✅ Deployment successful!"
                                        echo "Current Image: ${imageUri}"
                                        break
                                    } else if (serviceStatus in ['CREATE_FAILED', 'UPDATE_FAILED_ROLLBACK_COMPLETE']) {
                                        error("❌ Deployment failed with status: ${serviceStatus}")
                                    }
                                    
                                    if (attempt == maxAttempts) {
                                        error("❌ Deployment timeout after 4 minutes")
                                    }
                                    
                                    sleep(10)
                                }
                            }
                            slackSend(color: 'good', message: "🎉 ${environment} deployment completed successfully!")
                        } catch (Exception e) {
                            slackSend(color: '#FF0000', message: "Stage 'Check Deployment Status' FAILED: ${e.getMessage()}")
                            throw e
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            script {
                try {
                    def commitHash = env.GIT_COMMIT?.take(7) ?: 'unknown'
                    def commitMessage = 'Deployment successful'
                    def environment = env.BRANCH_NAME == 'main' ? 'Production' : 'Staging'
                    slackSend(
                        color: 'good',
                        message: """
                            :white_check_mark: *CDE Registry Deployment Successful!*
                            *Job:* `${env.JOB_NAME}`
                            *Build Number:* `${env.BUILD_NUMBER}`
                            *Environment:* `${environment}`
                            *Branch:* `${env.BRANCH_NAME}`
                            *Image Tag:* `${IMAGE_TAG}`
                            *Commit Hash:* `${commitHash}`
                            *Duration:* ${currentBuild.durationString}
                        """.stripIndent()
                    )
                } catch (Exception e) {
                    echo "Error sending success notification: ${e.getMessage()}"
                }
            }
        }
        failure {
            script {
                try {
                    def commitHash = env.GIT_COMMIT?.take(7) ?: 'unknown'
                    def environment = env.BRANCH_NAME == 'main' ? 'Production' : 'Staging'
                    slackSend(
                        color: 'danger',
                        message: """
                            :x: *CDE Registry Deployment Failed!*
                            *Job:* `${env.JOB_NAME}`
                            *Build Number:* `${env.BUILD_NUMBER}`
                            *Environment:* `${environment}`
                            *Branch:* `${env.BRANCH_NAME}`
                            *Duration:* ${currentBuild.durationString}
                            *Console Output:* ${env.BUILD_URL}console
                        """.stripIndent()
                    )
                } catch (Exception e) {
                    echo "Error sending failure notification: ${e.getMessage()}"
                }
            }
        }
        always {
            script {
                try {
                    // Clean up Docker images to free disk space
                    def imageRef = "${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}"
                    sh """
                        echo "Cleaning up Docker resources..."
                        
                        # Remove the built image
                        docker rmi ${imageRef} || true
                        
                        # Remove dangling images
                        docker image prune -f || true
                        
                        # Remove unused containers
                        docker container prune -f || true
                        
                        echo "Docker cleanup completed"
                    """
                } catch (Exception e) {
                    echo "Warning: Docker cleanup failed: ${e.getMessage()}"
                }
            }
            cleanWs()
        }
    }
}
pipeline {
    agent any
    
    environment {
        CDE_AWS_REGION = credentials('cde-aws-region')
        CDE_ECR_REGISTRY = credentials('cde-ecr-registry')
        CDE_ECR_REPO_NAME = credentials('cde-ecr-repo-name')
        PROD_APPRUNNER_SERVICE_ARN = credentials('prod-apprunner-service-arn')
        STAGING_APPRUNNER_SERVICE_ARN = credentials('staging-apprunner-service-arn')
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
                                aws apprunner update-service \\
                                    --service-arn ${APPRUNNER_SERVICE_ARN} \\
                                    --source-configuration '{"ImageRepository":{"ImageIdentifier":"${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}","ImageConfiguration":{"Port":"8000"},"ImageRepositoryType":"ECR"}}' \\
                                    --region ${CDE_AWS_REGION}
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
                            sh """
                                echo "Waiting 4 minutes for deployment to complete..."
                                sleep 240
                                
                                SERVICE_STATUS=\$(aws apprunner describe-service --service-arn ${APPRUNNER_SERVICE_ARN} --query 'Service.Status' --output text --region ${CDE_AWS_REGION})
                                IMAGE_URI=\$(aws apprunner describe-service --service-arn ${APPRUNNER_SERVICE_ARN} --query 'Service.SourceConfiguration.ImageRepository.ImageIdentifier' --output text --region ${CDE_AWS_REGION})
                                
                                echo "Service Status: \$SERVICE_STATUS"
                                echo "Current Image: \$IMAGE_URI"
                                
                                if [ "\$SERVICE_STATUS" = "RUNNING" ]; then
                                    echo "✅ Deployment successful!"
                                else
                                    echo "❌ Deployment failed with status: \$SERVICE_STATUS"
                                    exit 1
                                fi
                            """
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
                def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                def commitMessage = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
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
                        *Commit Message:* `${commitMessage}`
                        *Duration:* ${currentBuild.durationString}
                    """.stripIndent()
                )
            }
        }
        failure {
            script {
                def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                def commitMessage = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                def environment = env.BRANCH_NAME == 'main' ? 'Production' : 'Staging'
                slackSend(
                    color: 'danger',
                    message: """
                        :x: *CDE Registry Deployment Failed!*
                        *Job:* `${env.JOB_NAME}`
                        *Build Number:* `${env.BUILD_NUMBER}`
                        *Environment:* `${environment}`
                        *Branch:* `${env.BRANCH_NAME}`
                        *Commit Hash:* `${commitHash}`
                        *Commit Message:* `${commitMessage}`
                        *Duration:* ${currentBuild.durationString}
                        *Console Output:* ${env.BUILD_URL}console
                    """.stripIndent()
                )
            }
        }
        always {
            cleanWs()
        }
    }
}
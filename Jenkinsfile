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
                checkout scm
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
                    sh """
                        docker build -t ${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG} .
                    """
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'cde-aws-credentials']]) {
                    script {
                        sh """
                            aws ecr get-login-password --region ${CDE_AWS_REGION} | docker login --username AWS --password-stdin ${CDE_ECR_REGISTRY}
                            docker push ${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}
                        """
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
                        sh """
                            aws apprunner update-service \\
                                --service-arn ${APPRUNNER_SERVICE_ARN} \\
                                --source-configuration '{"ImageRepository":{"ImageIdentifier":"${CDE_ECR_REGISTRY}/${CDE_ECR_REPO_NAME}:${IMAGE_TAG}","ImageConfiguration":{"Port":"8000"},"ImageRepositoryType":"ECR"}}' \\
                                --region ${CDE_AWS_REGION}
                        """
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
                        sh """
                            echo "Waiting for deployment to complete..."
                            aws apprunner wait service-updated --service-arn ${APPRUNNER_SERVICE_ARN} --region ${CDE_AWS_REGION}
                            
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
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
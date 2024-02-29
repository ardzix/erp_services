pipeline {
    agent any
    environment {
        // Define the full image name including the registry prefix
        DOCKER_IMAGE = 'ardzix/rizz_erp_service:latest'
    }
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Print the current working directory for debugging
                    sh 'pwd'
                    // Build the Docker image with the tag specified in DOCKER_IMAGE environment variable
                    sh "docker build -t ${env.DOCKER_IMAGE} ."
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                script {
                    // Login to Docker Hub using credentials stored in Jenkins
                    withCredentials([usernamePassword(credentialsId: 'ard-dockerhub', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                        sh "echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin"
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push the image to Docker Hub
                    sh "docker push ${env.DOCKER_IMAGE}"
                }
            }
        }

        stage('Deploy to VPS') {
            steps {
                script {
                    sshagent(['stag-arnatech-sa-01']) {
                        // Remove the existing container if it exists
                        sh "ssh -o StrictHostKeyChecking=no root@172.105.124.43 'docker rm -f rizz-erp-service || true'"
                        // Pull the latest Docker image
                        sh "ssh -o StrictHostKeyChecking=no root@172.105.124.43 'docker pull ${env.DOCKER_IMAGE}'"
                        // Run the Docker container
                        sh "ssh -o StrictHostKeyChecking=no root@172.105.124.43 'docker run -d -p 8002:8002 --restart always --network development --name rizz-erp-service  --env-file rizz_erp/.env ${env.DOCKER_IMAGE}'"
                    }
                }
            }
        }

    }
           
}
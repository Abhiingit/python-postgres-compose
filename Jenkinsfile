pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
                sh 'git rev-parse --short HEAD'
            }
        }

        stage('Build') {
            steps {
                echo 'Build stage started'
                sh 'echo "Build completed successfully"'
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage started'
                sh 'echo "All tests passed"'
            }
        }

        stage('Package') {
            steps {
                echo 'Packaging application'
                sh 'echo "Package created successfully"'
            }
        }
    }

    post {
        success {
            echo 'Jenkins Pipeline completed successfully ✅'
        }

        failure {
            echo 'Jenkins Pipeline failed ❌'
        }
    }
}
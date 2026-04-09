pipeline {
    agent any
    
    libraries {
        lib('my-shared-library') 
    }

    stages {
        stage('Dev Environment') {
            when { branch 'dev' } 
            steps {
                script {
                    sh 'python ingest.py'
                    sh 'python train.py'
                    sh 'python deploy.py'
                    try {
                        sh 'python test_model.py'
                    } catch (Exception e) {
                        sendEmail()
                        error "Dev Testing failed"
                    }
                }
            }
        }

        stage('Pre-Prod Pipeline') {
            when { branch 'main' }
            steps {
                script {
                    sh 'python test_model.py'
                }
            }
        }

        stage('Prod Pipeline') {
            when { buildingTag() } 
            steps {
                script {
                    sh 'python deploy.py'
                }
            }
        }
    }
}
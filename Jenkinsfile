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
                    sh 'python3 ingest.py'
                    sh 'python3 train.py'
                    sh 'python3 deploy.py'
                    try {
                        sh 'python3 test_model.py'
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
                    sh 'python3 test_model.py'
                }
            }
        }

        stage('Prod Pipeline') {
            when { buildingTag() } 
            steps {
                script {
                    sh 'python3 deploy.py'
                }
            }
        }
    }
}

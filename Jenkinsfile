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
                    // Windows ke liye 'bat' use karein
                    bat 'python ingest.py'
                    bat 'python train.py'
                    
                    // Shared Library ke steps use karein
                    deployModel(alias: 'Challenger', port: 5001)
                    
                    def passed = testModel(port: 5001, threshold: 0.85)
                    
                    if (!passed) {
                        sendEmail(status: 'FAIL')
                        error "Dev Testing failed"
                    }
                }
            }
        }

        stage('Pre-Prod Pipeline') {
            when { branch 'main' }
            steps {
                script {
                    // Windows ke liye 'bat'
                    def passed = testModel(port: 5001, threshold: 0.90)
                    if (!passed) { error "Pre-Prod Testing failed" }
                }
            }
        }

        stage('Prod Pipeline') {
            when { buildingTag() } 
            steps {
                script {
                    // Production deployment
                    deployModel(alias: 'Champion', port: 5002)
                }
            }
        }
    }
}

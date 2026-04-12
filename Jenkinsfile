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
                    // Windows commands (bat)
                    bat 'python ingest.py'
                    bat 'python train.py'
                    
                    // Shared Library steps
                    deployModel(alias: 'Challenger', port: 5001)
                    
                    def passed = testModel(port: 5001, threshold: 0.85)
                    
                    if (passed) {
                        echo "Testing Passed!"
                    } else {
                        error "Dev Testing failed - Accuracy too low"
                    }
                }
            }
        }

        stage('Pre-Prod Pipeline') {
            when { branch 'main' }
            steps {
                script {
                    bat 'python test_model.py'
                }
            }
        }
    }
}

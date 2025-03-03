pipeline {
    agent { label 'stds-backend' }

    environment {
        PROJECT_DIR = '/home/ifan' 
    }
    
    
    triggers {
        githubPush()  // 啟用 GitHub webhook 觸發
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/ifan0927/stds_backend.git',
            }
        }

        stage('Setup Environment') {
            steps {
                dir("${PROJECT_DIR}") {
                    // docker-compose 設置環境變數
                    withCredentials([file(credentialsId: '07fca1b5-4273-403c-99c8-b3979c18c866', variable: 'DOCKER_ENV')]) {
                        sh 'cp $DOCKER_ENV .env'
                        sh 'chmod 644 .env'
                    }

                    // FastAPI 應用設置環境變數
                    withCredentials([file(credentialsId: '919b3a7c-0306-4d9a-911d-814150a8e6dc', variable: 'API_ENV')]) {
                        sh 'cp $API_ENV api/.env'
                        sh 'chmod 644 api/.env'
                    }
                }
            }
        }

        stage('Build and Deploy') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh 'docker-compose down || true'
                    sh 'docker-compose build'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Health Check') {
            steps {
                // 等待服務啟動
                sh 'sleep 15'

                // 檢查 API 服務是否正常運行
                sh 'curl -s http://localhost:8000/health || echo "API health check failed but continuing"'
            }
        }
    }

    post {
        success {
            echo '部署成功！'
        }
        failure {
            echo '部署失敗！'
        }
        always {
            echo '部署流程完成'
        }
    }
}
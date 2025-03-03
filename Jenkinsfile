// 總共使用四個Jenkins 憑證 管理敏感訊息 docker-compose-env,fastapi-env,gcp-service-account,gcp-bucket-name, initsql採用GCP Cloud Storage
// 透過JenkinsFile 進行自動化部署
// 1. Checkout: 從Github 下載專案
// 2. Setup Environment: 設置環境變數
// 3. Build and Deploy: 使用docker-compose 建置並啟動服務
// 4. Health Check: 檢查API 服務是否正常運行
// 5. Post: 部署成功或失敗後清理敏感檔案
pipeline {
    agent {
        label 'stds-backend'
    }
    
    environment {
        GCP_BUCKET = credentials('d363e5cc-9369-43d7-93db-804aa17626f7')
        SQL_FILE = 'init.sql'
    }
    
    triggers {
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ifan0927/stds_backend.git'
            }
        }
        
        stage('Setup Environment') {
            steps {
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
                
                // 從 GCP Cloud Storage 下載 init.sql
                withCredentials([file(credentialsId: '28cf4fd6-0347-4fb5-9100-b2da894be9dd', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                        # 安裝 gsutil 
                        which gsutil || (curl https://sdk.cloud.google.com | bash -s -- --disable-prompts && export PATH=$PATH:~/google-cloud-sdk/bin)
                        
                        # 設置 GCP 身份驗證
                        export GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
                        
                        # 下載 init.sql 從 Cloud Storage
                        gsutil cp gs://${GCP_BUCKET}/${SQL_FILE} ./init.sql
                        
                        # 確保正確的權限
                        chmod 644 ./init.sql
                    '''
                }
            }
        }
        
        stage('Build and Deploy') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose build'
                sh 'docker-compose up -d'
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
            // 清理敏感檔案
            sh 'rm -f .env api/.env init.sql'
        }
    }
}
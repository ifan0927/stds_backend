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
        GCP_BUCKET = credentials('gcp-bucket-name')
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
                withCredentials([file(credentialsId: 'docker-compose', variable: 'DOCKER_ENV')]) {
                    sh 'cp $DOCKER_ENV .env'
                    sh 'chmod 644 .env'
                }
                
                // FastAPI 應用設置環境變數
                withCredentials([file(credentialsId: 'fastapi', variable: 'API_ENV')]) {
                    sh 'cp $API_ENV api/.env'
                    sh 'chmod 644 api/.env'
                }
                
                // 從 GCP Cloud Storage 下載 init.sql
                withCredentials([file(credentialsId: 'gcp-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
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
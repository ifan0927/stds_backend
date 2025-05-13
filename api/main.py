from fastapi import FastAPI
from fastapi import Request
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import estates, rooms, rentals, users, electric_record, file, schedules, accounting, overtime_payment, emails
from routes import entry_table, auth, sop, upload, cache_management, schedule_replies, generate
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
from database import get_db
from models.file import Files as File
from utils.cloudstorage import StorageService
from utils import redis_config
import logging

# 設置時區和實例化 StorageService
tz = timezone(timedelta(hours=8))
storage_service = StorageService()

# 定義清理孤兒文件的函數
def cleanup_orphan_files():
    db = next(get_db())
    try:
        # 找出超過24小時且 ref_id 為 NULL 的文件
        cutoff_time = datetime.now(tz) - timedelta(hours=24)
        orphan_files = db.query(File).filter(
            File.ref_id.is_(None),
            File.upload_time < cutoff_time
        ).all()
        
        # 刪除找到的文件
        delete_count = 0
        for file in orphan_files:
            try:
                # 從雲存儲中刪除文件
                if file.blob_path:
                    storage_service.delete_file(file.blob_path)
                
                # 從數據庫中刪除記錄
                db.delete(file)
                delete_count += 1
            except Exception as e:
                print(f"Error deleting orphan file {file.id}: {str(e)}")
        
        # 提交更改
        db.commit()
        print(f"Cleanup completed: {delete_count} orphan files deleted")
    except Exception as e:
        print(f"Error during orphan file cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()

# 設置排程器
scheduler = BackgroundScheduler()
scheduler.add_job(
    cleanup_orphan_files,
    trigger=CronTrigger(hour=3, minute=0),  # 每天凌晨 3 點執行
    id="cleanup_orphan_files"
)

load_dotenv()
app = FastAPI(title="Estate Management API")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
routes_list = [
    estates,
    rooms,
    rentals,
    users,
    electric_record,
    file,
    schedules,
    accounting,
    overtime_payment,
    emails,
    entry_table,
    auth,
    sop,
    upload,
    cache_management,
    schedule_replies,
    generate
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
for route in routes_list:
    app.include_router(route.router)

@app.on_event("startup")
async def startup_event():
    try:
        ping = redis_config.redis_client.ping()
        if ping:
            logging.info("Successfully connected to Redis")
        else:
            logging.error("Failed to connect to Redis, ping returned False")
            scheduler.start()
            logging.info("Background scheduler started for orphan file cleanup")
    except Exception as e:
        logging.error(f"Strat up error: {e}")
    

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("Background scheduler shut down")

@app.get("/")
def read_root():
    return {"message": "Welcome to Estate Management API V0.1"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/callback")
async def callback(request: Request):
    # 獲取LINE平台傳送的事件
    body = await request.body()
    body_text = body.decode('utf-8')

    signature = request.headers.get('X-Line-Signature', '')
    
    try:
        events = json.loads(body_text)['events']
        
        for event in events:
            # 檢查事件是否來自群組
            if 'source' in event and event['source']['type'] == 'group':
                # 提取並打印群組ID
                group_id = event['source']['groupId']
                print(f"群組ID: {group_id}")
                
        return {"status": "OK"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
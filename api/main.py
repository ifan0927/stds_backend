# main.py
from fastapi import FastAPI
from fastapi import Request as request
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import estates, auth, rooms, rentals, users, electric_record, file, schedules, accounting, overtime_payment, emails
from routes import entry_table, line_bot
from database import engine
import models.estate
import json


load_dotenv()
app = FastAPI(title="Estate Management API")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(estates.router)
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(rentals.router)
app.include_router(users.router)
app.include_router(electric_record.router)
app.include_router(file.router)
app.include_router(schedules.router)
app.include_router(accounting.router)
app.include_router(overtime_payment.router)
app.include_router(emails.router)
app.include_router(entry_table.router)
app.include_router(line_bot.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Estate Management API V0.1"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取LINE平台傳送的事件
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        events = json.loads(body)['events']
        
        for event in events:
            # 檢查事件是否來自群組
            if 'source' in event and event['source']['type'] == 'group':
                # 提取並打印群組ID
                group_id = event['source']['groupId']
                print(f"群組ID: {group_id}")

            
        return 'OK'
    except Exception as e:
        print(f"Error: {e}")
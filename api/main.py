from fastapi import FastAPI
from fastapi import Request
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import estates, rooms, rentals, users, electric_record, file, schedules, accounting, overtime_payment, emails
from routes import entry_table, auth, sop, upload
import json


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
    upload
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
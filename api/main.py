# main.py
from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import estates, auth, rooms, rentals, users, electric_record, file, schedules, accounting, overtime_payment, emails
from database import engine
import models.estate


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

@app.get("/")
def read_root():
    return {"message": "Welcome to Estate Management API V1"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
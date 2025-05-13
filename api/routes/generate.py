from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import tempfile
import uuid
from docxtpl import DocxTemplate
from pydantic import BaseModel

from database import get_db
from models.room import Room
from models.rental import Rental
from models.users import User
from models.electric_record import ElectricRecord
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(tags=["generate"])

# 建立一個用於存儲臨時文件的目錄
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_files")
os.makedirs(TEMP_DIR, exist_ok=True)

class ReceiptData(BaseModel):
    estate_name: str
    room_number: str
    tenant_name: str
    current_reading: float
    previous_reading: float
    usage: float
    fee: int
    year: str
    prev_month: str
    current_month: str

class RoomTenantInfo(BaseModel):
    room_id: int
    room_name: str
    tenant_name: str = ""  # 允許空租客名稱

class ReportData(BaseModel):
    estate_id: str
    estate_name: str
    year: str
    rooms: List[RoomTenantInfo]

@router.post("/generate/receipt")
async def generate_receipt(
    data: ReceiptData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """生成電費收據"""
    try:
        # 使用DocxTemplate生成Word文檔
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "receipt_template.docx")
        
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail="找不到收據模板")
            
        doc = DocxTemplate(template_path)
        
        # 準備模板上下文數據
        context = {
            "estate_name": data.estate_name,
            "room_number": data.room_number,
            "tenant_name": data.tenant_name,
            "current_reading": data.current_reading,
            "previous_reading": data.previous_reading,
            "usage": data.usage,
            "fee": data.fee,
            "calculation": f"{data.previous_reading}-{data.current_reading}={data.usage}x4.5={data.fee}",
            "period": f"{data.year}/{'0' if int(data.prev_month) < 10 else ''}{data.prev_month}～{data.year}/{'0' if int(data.current_month) < 10 else ''}{data.current_month}",
        }
        
        # 渲染模板
        doc.render(context)
        
        # 創建一個具有意義的文件名
        filename = f"receipt_{data.room_number}_{data.year}{data.current_month}.docx"
        output_path = os.path.join(TEMP_DIR, filename)
        
        # 保存文件
        doc.save(output_path)
        
        # 設置背景任務清理臨時文件
        background_tasks.add_task(cleanup_temp_file, output_path, 300)  # 5分鐘後刪除
        
        # 直接返回文件下載
        from fastapi.responses import FileResponse
        return FileResponse(
            path=output_path,
            filename=f"收據_{data.estate_name}_{data.room_number}_{data.year}{data.current_month}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        # 記錄詳細錯誤信息
        import traceback
        traceback_str = traceback.format_exc()
        print(f"收據生成錯誤: {str(e)}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"生成收據失敗: {str(e)}")

@router.post("/generate/report")
async def generate_report(
    data: ReportData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """生成電費總表"""
    try:
        # 使用DocxTemplate生成Word文檔
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "report_template.docx")
        
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail="找不到總表模板")
        
        print(f"模板路徑: {template_path}, 存在: {os.path.exists(template_path)}")
            
        doc = DocxTemplate(template_path)
        
        # 獲取所有房間的讀數資料
        room_data = []
        total_usage = 0
        total_fee = 0
        
        # 獲取12月和10月的讀數進行比較計算
        for room_info in data.rooms:
            room_id = room_info.room_id
            
            # 獲取12月讀數
            dec_readings = db.query(ElectricRecord).filter(
                ElectricRecord.room_id == room_id,
                ElectricRecord.record_year == int(data.year),
                ElectricRecord.record_month == 12
            ).first()
            
            # 獲取10月讀數
            oct_readings = db.query(ElectricRecord).filter(
                ElectricRecord.room_id == room_id,
                ElectricRecord.record_year == int(data.year),
                ElectricRecord.record_month == 10
            ).first()
            
            # 計算用電量與電費
            current_reading = dec_readings.reading if dec_readings else None
            previous_reading = oct_readings.reading if oct_readings else None
            
            usage = 0
            if current_reading is not None and previous_reading is not None:
                usage = current_reading - previous_reading
            
            fee = round(usage * 4.5)
            
            # 添加到房間數據列表
            room_data.append({
                "room_number": room_info.room_name,
                "tenant_name": room_info.tenant_name,
                "current_reading": current_reading if current_reading is not None else "",
                "previous_reading": previous_reading if previous_reading is not None else "",
                "usage": usage,
                "fee": fee
            })
            
            total_usage += usage
            total_fee += fee
        
        # 準備模板上下文數據
        context = {
            "estate_name": data.estate_name,
            "year": data.year,
            "month": "12",
            "rooms": room_data,
            "total_usage": total_usage,
            "total_fee": total_fee
        }
        
        # 輸出模板數據用於調試
        print("模板數據:", context)
        
        # 渲染模板
        doc.render(context)
        
        # 創建具有意義的文件名
        filename = f"{data.estate_name}_{data.year}_12.docx"
        output_path = os.path.join(TEMP_DIR, filename)
        
        # 保存文件
        doc.save(output_path)
        print(f"文件已保存到: {output_path}")
        
        # 設置背景任務清理臨時文件
        background_tasks.add_task(cleanup_temp_file, output_path, 300)  # 5分鐘後刪除
        
        # 直接返回文件下載
        from fastapi.responses import FileResponse
        return FileResponse(
            path=output_path,
            filename=f"{data.estate_name}{data.year}_12電費總表.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        # 記錄詳細錯誤信息
        import traceback
        traceback_str = traceback.format_exc()
        print(f"總表生成錯誤: {str(e)}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"生成電費總表失敗: {str(e)}")

# 清理臨時文件的背景任務
async def cleanup_temp_file(file_path: str, delay_seconds: int):
    """在指定延遲後刪除臨時文件"""
    import asyncio
    
    await asyncio.sleep(delay_seconds)
    
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            print(f"已刪除臨時文件: {file_path}")
    except Exception as e:
        print(f"刪除臨時文件失敗: {str(e)}")
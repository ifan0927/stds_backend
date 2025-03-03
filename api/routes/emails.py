from fastapi import FastAPI, BackgroundTasks, APIRouter, Body, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from schemas.emails import EmailSchema
from utils.utils import send_email_task
from utils.auth import get_current_active_user
from models.auth import AuthUser


router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/send-email/", response_class=JSONResponse)
async def send_email_endpoint(
    background_tasks: BackgroundTasks,
    email_data: EmailSchema = Body(...),
    current_user: AuthUser = Depends(get_current_active_user)
):

    # 添加到后台任务
    background_tasks.add_task(send_email_task, email_data)
    
    return {
        "status": "success",
        "message": "Email sending task has been queued"
    }
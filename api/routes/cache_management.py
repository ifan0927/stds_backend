# cache_management.py
from utils.redis_config import redis_client
import logging
from fastapi import APIRouter, Depends
from utils.auth import get_current_active_user
from models.auth import AuthUser

router = APIRouter(prefix="/cache", tags=["cache"])

@router.delete("/clear")
def clear_all_cache(
    current_user: AuthUser = Depends(get_current_active_user)
):
    """僅管理員可以清除所有快取"""
    if current_user.role != "admin":
        return {"status": "error", "message": "Admin privilege required"}
    
    try:
        redis_client.flushdb()
        return {"status": "success", "message": "All cache cleared successfully"}
    except Exception as e:
        logging.error(f"Error clearing cache: {e}")
        return {"status": "error", "message": str(e)}

@router.delete("/rentals")
def clear_rentals_cache(
    current_user: AuthUser = Depends(get_current_active_user)
):
    """清除所有租賃相關的快取"""
    if current_user.role != "admin":
        return {"status": "error", "message": "Admin privilege required"}
    
    try:
        keys = redis_client.keys("rentals:*")
        if keys:
            redis_client.delete(*keys)
        return {"status": "success", "message": f"Cleared {len(keys)} cache entries"}
    except Exception as e:
        logging.error(f"Error clearing rentals cache: {e}")
        return {"status": "error", "message": str(e)}

@router.delete("/rentals/room/{room_id}")
def clear_room_cache(
    room_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """清除特定房間的快取"""
    try:
        keys = redis_client.keys(f"rentals:room:{room_id}:*")
        if keys:
            redis_client.delete(*keys)
        return {"status": "success", "message": f"Cleared {len(keys)} cache entries for room {room_id}"}
    except Exception as e:
        logging.error(f"Error clearing room cache: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/stats")
def get_cache_stats(
    current_user: AuthUser = Depends(get_current_active_user)
):
    """獲取快取統計資訊"""
    if current_user.role != "admin":
        return {"status": "error", "message": "Admin privilege required"}
    
    try:
        info = redis_client.info()
        keys_count = redis_client.dbsize()
        rental_keys = len(redis_client.keys("rentals:*"))
        
        return {
            "status": "success",
            "total_keys": keys_count,
            "rental_keys": rental_keys,
            "memory_used": info.get("used_memory_human", "N/A"),
            "uptime_days": info.get("uptime_in_days", "N/A")
        }
    except Exception as e:
        logging.error(f"Error getting cache stats: {e}")
        return {"status": "error", "message": str(e)}
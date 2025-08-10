from fastapi import APIRouter, HTTPException
from health_engine.file_health import file_health_fetch

health_router = APIRouter(prefix="/api/v1", tags=["File health"])

@health_router.get("/file-health")
def file_health(id):
    if int(id) in [1,2,3]:
        return file_health_fetch(id)
    
    else: 
        return "invalied file id"

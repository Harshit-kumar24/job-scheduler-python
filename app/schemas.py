from typing import Optional, Dict
from pydantic import BaseModel,ConfigDict
from datetime import datetime 


class JobCreate(BaseModel):
    job_name: Optional[str]
    schedule_cron: str
    last_run_time: Optional[datetime] = None
    next_run_time: Optional[datetime] = None
    last_run_status: Optional[int] = None
    parameters: Optional[Dict[str,object]] = None



class JobResponse(JobCreate):
    id: int

    class Config:
        orm_mode = True 
        

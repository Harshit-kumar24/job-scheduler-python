from app.models import Job
from app.schemas import JobCreate
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

#get job by name
async def get_job_by_name(db: AsyncSession, job_name: str):
    result = await db.execute(select(Job).filter(Job.job_name == job_name))
    return result.scalars().first()

#create a new job 
async def create_job(db: AsyncSession, job: JobCreate):
    existing_job = await get_job_by_name(db, job.job_name)
    if existing_job:
        raise HTTPException(status_code=400, detail="Job name already exists")
    db_job = Job(
        job_name=job.job_name,
        schedule_cron=job.schedule_cron,
        last_run_time=job.last_run_time,
        next_run_time=job.next_run_time,
        last_run_status=job.last_run_status,
        parameters=job.parameters
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

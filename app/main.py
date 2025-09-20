from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repository.job_repository import JobRepository
from app.services.job_service import JobService
from app.models import Job as JobModel
from app.schemas import JobCreate, JobResponse
from typing import List


app = FastAPI(
    title="Job Scheduler Microservice",
    description="A microservice to schedule and manage cron-based jobs.",
    version="1.0.0",
    contact={
        "name": "Harshit Kumar",
        "email": "harshit.kumar@email.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    })


def get_job_service(db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    return JobService(repo)

@app.get("/jobs", response_model=List[JobResponse])
async def get_all_jobs(db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    return await repo.get_all_jobs()

@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_by_id(job_id: int, db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    job = await repo.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, service: JobService = Depends(get_job_service)):
    try:
        job_model = JobModel(**job.dict())
        return await service.create_and_schedule_job(job_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Thankyou for taking a look at my job scheduler..."}

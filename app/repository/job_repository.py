from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Job

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_jobs(self):
        result = await self.session.execute(select(Job))
        return result.scalars().all()

    async def get_job_by_id(self, job_id: int):
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def create_job(self, job: Job):
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

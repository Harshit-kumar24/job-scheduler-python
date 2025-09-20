from apscheduler.triggers.cron import CronTrigger
from app.repository.job_repository import JobRepository
from app.models import Job
from app.scheduler_manager import scheduler, scheduled_job_action

class JobService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    async def create_and_schedule_job(self, job_data: Job):
        db_job = await self.repo.create_job(job_data)

        try:
            trigger = CronTrigger.from_crontab(db_job.schedule_cron)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression: {e}")

        scheduler.add_job(
            func=scheduled_job_action,
            trigger=trigger,
            args=[db_job.id],
            id=str(db_job.id),
            replace_existing=True
        )

        return db_job

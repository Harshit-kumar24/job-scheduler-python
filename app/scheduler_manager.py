from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.start()

def scheduled_job_action(job_id: int):
    print(f"Executing job {job_id} at {datetime.now()}")

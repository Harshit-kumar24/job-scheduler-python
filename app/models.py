from sqlalchemy import Column,Integer,String,TIMESTAMP,JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema":"masters"}

    id = Column(Integer,primary_key=True,index=True)
    job_name = Column(String(255),unique=True,nullable=True)
    schedule_cron = Column(String(100),nullable=False)
    last_run_time = Column(TIMESTAMP,nullable=True)
    next_run_time = Column(TIMESTAMP,nullable=True)
    last_run_status = Column(Integer,nullable=True)
    parameters = Column(JSON,nullable=True)
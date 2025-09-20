create schema masters;

CREATE TABLE masters.jobs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL UNIQUE,
    schedule_cron VARCHAR(100) NOT NULL,
    last_run_time TIMESTAMP,
    next_run_time TIMESTAMP,
    last_run_status INT, 
    parameters JSONB
);

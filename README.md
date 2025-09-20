### How to setup the project 
----------------------------------
- To setup this project first start docker engine in your local or on server
- changes these configurations accordingly in the **docker-compose.yml** file
```
POSTGRES_USER: postgres_user
POSTGRES_PASSWORD: postgres_password
POSTGRES_DB: postgres_db
POSTGRES_HOST: postgres_host
POSTGRES_PORT: 5432
```
- after that execute the **run.sh** script
- once both the container for **database** and **job-scheduler** started running successfully
- connect to the database using **pgadmin4** or **DBeaver** and execute the migration.sql script
- once that is done you are good to go
- you can test the enpoints by visiting
```
http://{dns}:8000/docs
```
- change the **dns** accordingly
  

### Overview
------------
You need to develop a scheduler microservice that allows job scheduling while maintaining
critical job-related information. The service should have API endpoints for job management,
such as listing all jobs, retrieving details of a specific job by ID, and creating new jobs.

Scalability: The application should be scalable to handle increased applicant
complexity, **~10,000 users** spread globally, **~1,000 services**, and **~6,000 API requests**
per minute
#### <u>Functional Requirements</u>

- **create job:** endpoint to schedule a new job with necessary metadata like name, schedule(cron),parameters etc.
- **get job by id:** retrieve job details by a unique job id
- **list all jobs:** fetch a list of jobs with filters
#### <u>Non-Functional Requirements</u>

- The system is expected to have **high availablity** **( avaliablity > consistency)**
- System should execute the scheduled job **atleast once**
- Jobs should run almost when the scheduled run is expected **(2-4 second deplay is OK)**
- Even if the system is down the jobs recieved shouldn't be lost **(the system should be durable)**
- The should be able to handle almost **6000 API request, 1000 services, 10,000 users globally**
#### <u>Capacity Estimation</u>

- Since its mentioned we have **6000 API request per minute** to our Job scheduler we can take **80:20 read to write ratio** so we have now,

- **in a minute:** 20% x 6000 = 1200 new jobs per minute 
- **in a hour:** 1200 * 60 = 72,000 new jobs per hour 
- **in a day:** 72,000 * 24 = 1,728,000 new jobs per day

- according to the **cron expression** after scheduling a single job can repeat multiple times in a day we can take a estimation of **5 times a day**

- **total jobs in a day:** 1,728,000 * 5 = 8,640,000 total jobs a day

 **Throughput Expected:** **(Total jobs per day) / (Number of seconds in a day)**

 > ***Expected Throughput = 8,640,000 / 86400 = 100 jobs per second***

##### Storage Estimation 
- we can assume that the job is in **general a python script** that we have to run 
- Assuming we have 8,640,000 unique jobs per day and each job is a python script of roughly **200 lines and each line has roughly 50 bytes of data** 

**Storage per script:** 200 lines * 50 bytes =10000 bytes (10KB) per script

**Total Storage per day for scripts :** 10KB * 8,640,000 = 8,64,00,000 KB per day ~ **(82.4 GB)**
#### Calculation (per user)
##### Assumptions
- Jobs per user = **5**
- Executions per job per day = **5**
- Size per execution = **3 KB**
- Job metadata = **1.5 KB per job**
- User profile = **2 KB**
-  Executions/day = 5 jobs × 5 execs/job = **25 execs/day**
-  Execution storage/day = 25 × 3 KB = **75 KB/day**
-  Job metadata = 5 × 1.5 KB = **7.5 KB**
-  User profile = **2 KB**

Total/day = 75 + 7.5 + 2 = **84.5 KB/day** ≈ **~85 KB/day**

**Total Storage per day for total user:** 10,000 users x 85KB = 850,000 KB (0.81GB)

> ***Total Storage Requred per day: 82.4GB + 0.81GB ~ 83GB***
### <u>Basic High Level Design</u>
-------------------------------------
![basic high level design](https://github.com/Harshit-kumar24/job-scheduler-python/blob/8d047aaeaf8af8e295fc7fd46e03c72cd290f0bd/images/Pasted%20image%2020250919121438.png)
- So according to the basic high level architecture when a user makes a request the request will go through a **API gateway** for general authentication checks and service discovery.
- from the api gateway the request will meet **load balancer** which will distribute the load to multiple running instances of our **scheduler service** 
- the scheduler service will save all the necessary job related data into our **DynamoDB**

#### Why we are choosing DynamoDB?

-  For our job scheduler as discussed we need **highly avaliable** database also the number of **writes** will mainly come from,
1. scheduling a job 
2. creating a run for job (when status is pending)
3. updating run status

- The **reads** will come from the following,
1. Some mechanism which will fetch the upcoming jobs to run based on the schedule
2. If user queries to get all jobs 
3. If user queries to get a specific job based on id

- The choice of DB will depend on how frequent we want to fetch upcoming jobs to run 

- lets say we query the db every minute to fetch the jobs that has to be execute for the next minute and **keep them in a sorted manner such that for that minute based on the time they has to be executed if they has to be executed on the same time any one can be excuted first**

- as we can see this is a **FIFO operation** where first job will come and get executed so, for this condition we can use a queue type service so we can use something like **Kafka or Message Queue service**
- but we can't use **kafka** as first of all it is a overkill for this usecase and second we want to maintain order and in kafka you can only maintain order in a single partition so if you insert in a single partition in kafka what will be the point of using a kafka when you can use a **Message Queue(RabbitMQ, SQS)**
- Now among options like **MongoDB, Cassandra & DynamoDB** we can use anyone as the writes are also not much. We have to make sure that DB is indexed as the **job retrieval to load in queue has to be fast**

### <u>Full High Level Design</u>
-----------------------------------
![basic high level design](https://github.com/Harshit-kumar24/job-scheduler-python/blob/8d047aaeaf8af8e295fc7fd46e03c72cd290f0bd/images/Pasted%20image%2020250919154624.png)
- As we have cleared why we are using **DynamoDB** now we can focus on actual logic.
- For, every minute we have to fetch the jobs that has to be executed for **next minute** that we will do using **Watcher Service** that will load the next jobs that has to be executed in the **SQS(Simple Queue Service)** as discussed.
- The actual logic **(Python code)** will be fetched from **S3 Bucket**
- Once the next minute comes our **Executor Service** will start processing jobs from the **SQS** and will run in a **Containerized Environment** to protect our system as the code can be malicious as well.
- During this process the **Executor Service** will also update the status of the job to **Scheduler Service** if any user is fetching the status of the job that is being executed 
- Once the job is done the final will be updated in the **database** if it got successfully executed or rejected.
  
### <u>Important Problem that should be addressed</u>

- **The problem here is to load the next minute job**. We have to query the DB for **8,640,000** per minute at peak which is a lot and then we also have to filter for the next minute jobs and then **sort** them in **ascending** order to load into the queue 
- which is quite a lot of work. To solve this problem we will use the concept of **partitions & sort key**
- since we have to deal with the jobs that are coming in next minute, other data is totally irrelevant at the moment so instead quering **8.6 million( Approx. )** records we can partition this data into **24 partitions** or less based on requirement and for every hour now we will store data into a different partition DB so for **(hour1: partition1), (hour2: partition2), (hour3: partition3)** and so on.
- Now we don't have to query **8.6 million records** instead we have to query **(8.6 million/ 24) records approx** which will rapidly **decrease the latency**. 
- the response if we will fetch status of a job it will look something like this,
  
```
 {
    "execution_time": 1729329492, 
    "key": "1729329492-3244-2373-2352-6432", 
    "job_id": "3244-2373-2352-6432",
    "user_id": "user123",
    "status": "PENDING",
    "attempt": 0
}
```

- we will find the partition key by getting the current hour from the timestamp so if the current time is **3.02 AM Monday** partition key would be **3** so the data will be fetched from the 3rd partition
### <u>Future Enhancements</u>

1. We can add some kind of retry logic so if a **job** fails we can execute it N number of times before finally failing it 
2. If there is much more delay in job execution we can alert the user 
3. We can add functionality for user to execute a job now first then run it after on some different schedule time

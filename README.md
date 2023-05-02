# Functional Design
The context required for a successful implementation of the solution could be:

1. Warehouse to store raw and processed data. -> BlobStorage
2. Event streaming to queue -> Kafka
3. An ETL to pull the raw events into the warehouse.
4. An ETL to process the data and load it into the database.
6. REST API that can query the Database.
7. Frontend that can query the API.

# Where should the company deploy this API?
- AWS EC2: "cheap" virtual machine. Billed by time online.
- AWS Lambda: "cheap" function run when certain contitions are met. Billed by use cost and number of uses.
- AWS EKS + Fargate: expensive solution that:
    1. Can facilitate the creation of replicas to distribute the load...
    2. ...through a load balancer (i.e Ingress).
    3. No downtime with rolling release.
    4. Always enough resources with Fargate.

## API costs
1. Less initial investment would be EC2, since I could repeat my steps and focus on security/network issues.
2. For a low and sparse number of requests, AWS Lambda could be cheaper. Higher initial investment (because I don't know how to do it).
3. Highest initial investment that could require multiple engineers. High continuous expense.

All this options would also need a database, which could also be deployed on EC2 (cheaper) or on RDS (more expensive).

# How to deploy in the cloud
This is the easiest way I found to do it:
1. Build API image.
2. Create ECR for the project.
3. Push images to ECR.
4. Create 2 EC2 instances (`A` and `B`), and install docker on both.
5. Pull API image in ECR into `A`.
6. Pull Postgres into EC2 instance `B`.
7. Spin up containers. API should be able to reach the DB, so the selection of the host is VERY important. Worked for me for with the public IP.

# Customer specific auth
Easiest solution would be API Keys. To manage users and keys, it might be possible to use AWS Cognito.

# Which concerns should they have regarding security?
- Isolated network for API and Database with one point of access to the API.
- Proper Database management to protect encrypt sensitive data.
- Enpoint to generate Oauth token using user credentials.

# Technical info
## Requirements
### Test: poetry, docker
Poetry to install ALL deps in the virtualenv, since the requirements.txt file is limited to PRD libraries.
Docker, because the tests will spin up a Postgres.

### Run: docker, terraform
Docker to build the image. Use `make build`. Image `myapi` will be created.
`terraform apply` to spin up API and Database. Will ask for variables.
`terraform destroy` to destroy everything.

## API
Once deployed access the endpoints at port 8000.
Low effort frontend is the OpenAPI itself.
Since the database will be empty, you will need to load the data using the endpoints tagged as ADMIN.

1. Load parks info
2. Select park name and load park energy readings.
3. Repeat step 2 for as many parks as you want.

## Endpoints
- `/parks`: list park info.
- `/parks/energy_readings`: list park info with readings. It's a join between the two tables.
- `/stats/parks`: show stats by park by date.
- `/stats/energy_types`: show stats by energy type by date.

### Admin
Just used to load the data. Did it for myself, not for you :D. You're supposed to use the deployed AWS app!

# 2-Tier Python + PostgreSQL Docker Application

## Overview

This project demonstrates an end-to-end **2-tier containerized application** using Docker and Docker Compose.

The application consists of:

* Python Flask web application
* PostgreSQL database
* Docker Bridge Network
* Docker Named Volume for persistent database storage
* Bind Mount demonstration
* Docker Hub image push/pull
* AWS ECR image push/pull
* Bash health-check script

The project combines the Docker, Linux, Bash scripting, networking, storage, and container registry concepts learned during the week.

\---

## Architecture

```text
                    Client
                      |
                      | HTTP :5000
                      v
             +-------------------+
             |   Flask Web App   |
             |   Docker Container|
             +---------+---------+
                       |
                       | Docker Bridge Network
                       | DB\_HOST=db
                       v
             +-------------------+
             |    PostgreSQL     |
             |  Docker Container |
             +---------+---------+
                       |
                       v
             +-------------------+
             |   Named Volume   |
             |   postgres\_data  |
             +-------------------+
```

\---

## Technologies Used

* Python 3.13
* Flask
* PostgreSQL 16
* Docker
* Docker Compose
* Bash
* Linux
* Docker Hub
* AWS ECR

\---

## Project Structure

```text
python-postgres-compose/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── scripts/
│   └── health\_check.sh
│
├── bind-mount-demo/
│   └── hello.txt
│
├── Dockerfile
├── compose.yaml
├── .dockerignore
└── README.md
```

\---

# 1\. Application

The web tier is built using Flask.

### GET `/`

Checks whether the Flask application is running.

Example response:

```text
Python + PostgreSQL application is running!
```

### POST `/messages`

Adds a message to PostgreSQL.

Example:

```json
{
  "message": "Hello from Docker Compose"
}
```

### GET `/messages`

Retrieves stored messages from PostgreSQL.

Example:

```text
1 | Persistent data test
2 | Final 2-tier capstone test
```

\---

# 2\. Dockerfile

The application is containerized using the following Dockerfile:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5000

CMD \["python", "app.py"]
```

## Dockerfile Best Practices Used

### Small base image

```dockerfile
FROM python:3.13-slim
```

The slim Python image reduces image size compared with the full Python image.

### Layer caching

Dependencies are copied and installed before the application code:

```dockerfile
COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .
```

If only `app.py` changes, Docker can reuse the dependency installation layer from its cache.

### No pip cache

```text
--no-cache-dir
```

prevents pip from storing unnecessary package cache files inside the image.

### Multi-stage builds

Multi-stage builds were studied as a Docker optimization technique. They are useful when a project needs build dependencies in an earlier stage but only final runtime files in the production image. This small Flask application does not require a separate build stage, so the final capstone uses a simple single-stage Dockerfile.

\---

# 3\. Dockerignore

The project uses `.dockerignore` to prevent unnecessary files from being sent to the Docker build context.

```text
.git
.gitignore
\_\_pycache\_\_
\*.pyc
.venv
venv
bind-mount-demo
README.md
```

This reduces build context size and keeps unnecessary files out of the image build process.

\---

# 4\. Docker Compose

Docker Compose is used to manage the two containers:

```text
app → Flask web application

db → PostgreSQL database
```

Compose also manages:

* Container networking
* Database health checks
* Service dependencies
* Persistent storage

The application waits for PostgreSQL to become healthy:

```yaml
depends\_on:
  db:
    condition: service\_healthy
```

PostgreSQL uses:

```yaml
healthcheck:
  test: \["CMD-SHELL", "pg\_isready -U appuser -d appdb"]
```

\---

# 5\. Docker Networking

Docker Compose automatically creates a bridge network:

```text
python-postgres-compose\_default
```

The containers communicate through this network.

The Flask application connects to PostgreSQL using:

```text
DB\_HOST=db
```

Here, `db` is the PostgreSQL service name defined in `compose.yaml`.

Docker's internal DNS resolves `db` to the PostgreSQL container.

The application therefore does not need to hard-code the PostgreSQL container IP address.

```text
Flask Container
      |
      | db:5432
      v
PostgreSQL Container
```

The database port `5432` is used internally by the Compose network.

\---

# 6\. Persistent Storage

PostgreSQL uses a Docker named volume:

```text
postgres\_data
```

The volume is mounted at:

```text
/var/lib/postgresql/data
```

This separates database data from the PostgreSQL container itself.

```text
PostgreSQL Container
        |
        v
postgres\_data
        |
        v
Persistent Database Data
```

## Persistence Test

The database was tested using:

```bash
docker compose down
docker compose up -d
```

After the PostgreSQL container was recreated, the existing records were still available:

```text
1 | Persistent data test
2 | Final 2-tier capstone test
```

This proved that the named volume preserved the database data.

### Important

```bash
docker compose down
```

removes containers and the network but normally preserves named volumes.

```bash
docker compose down -v
```

also removes the volumes and can remove the stored database data.

\---

# 7\. Bind Mount

A bind mount maps a specific host directory into a container.

For this project:

```text
./bind-mount-demo
```

was mapped to:

```text
/app/data
```

A file was created on the Windows host:

```text
bind-mount-demo/hello.txt
```

with:

```text
Hello from Windows host
```

The file was successfully read from inside an Ubuntu Docker container.

This demonstrated:

```text
Windows Host
    |
    | Bind Mount
    v
Docker Container
```

## Named Volume vs Bind Mount

### Named Volume

Docker-managed storage.

Best suited for:

* PostgreSQL
* MySQL
* MongoDB
* Persistent application data

### Bind Mount

Host directory mapped to a container directory.

Best suited for:

* Development
* Source code
* Configuration files
* Files that need direct host access

\---

# 8\. Running the Application

Build the image and start both services:

```bash
docker compose up -d --build
```

Check the services:

```bash
docker compose ps
```

Expected:

```text
app → Up
db  → Up (healthy)
```

\---

# 9\. Application Testing

Test the Flask application:

```powershell
Invoke-RestMethod http://localhost:5000/
```

Expected:

```text
Python + PostgreSQL application is running!
```

Add a message:

```powershell
Invoke-RestMethod -Uri http://localhost:5000/messages -Method Post -ContentType "application/json" -Body '{"message":"Final 2-tier capstone test"}'
```

Retrieve messages:

```powershell
Invoke-RestMethod http://localhost:5000/messages
```

Example:

```text
1 | Persistent data test
2 | Final 2-tier capstone test
```

The application successfully inserted and retrieved records from PostgreSQL.

\---

# 10\. PostgreSQL Verification

PostgreSQL can be accessed from the database container using:

```bash
docker compose exec db psql -U appuser -d appdb
```

Stored messages were verified directly inside PostgreSQL.

Example:

```text
id | message
---+-------------------------
1  | Persistent data test
2  | Final 2-tier capstone test
```

\---

# 11\. Bash Health Check

The project includes:

```text
scripts/health\_check.sh
```

The script demonstrates Linux and Bash concepts including:

* Variables
* Functions
* if/else
* Command substitution
* Script arguments
* grep
* df
* curl
* Docker Compose inspection

The script checks:

* Host information
* Disk usage
* Docker services
* PostgreSQL availability
* Flask application health

\---

# 12\. Linux Concepts Applied

The project builds upon the Linux concepts practiced during the week.

### File and directory operations

```bash
pwd
ls
cd
mkdir
cp
mv
rm
```

### Permissions

```bash
chmod
chown
```

### Process management

```bash
ps
top
kill
```

### Package management

```bash
apt
yum
dnf
```

### Users and groups

```bash
useradd
usermod
groupadd
groups
id
```

### Disk usage

```bash
df
du
```

### Text processing

```bash
grep
sed
awk
```

### Networking

```bash
ssh
curl
ping
netstat
ss
```

### Scheduling

```bash
crontab
```

### Log analysis

Linux logs and application output were analyzed using command-line tools and Bash/Python scripts during the learning process.

\---

# 13\. Docker Hub

The Flask application image was pushed to Docker Hub as:

```text
abhijeetpratap/python-postgres-compose-app:1.0
```

The complete workflow was tested:

```text
Build
  ↓
Tag
  ↓
Push to Docker Hub
  ↓
Pull from Docker Hub
```

Commands used:

```bash
docker tag python-postgres-compose-app:latest abhijeetpratap/python-postgres-compose-app:1.0

docker push abhijeetpratap/python-postgres-compose-app:1.0

docker pull abhijeetpratap/python-postgres-compose-app:1.0
```

\---

# 14\. AWS ECR

An Amazon ECR repository was created in the `ap-south-1` region.

Repository:

```text
python-postgres-compose-app
```

ECR image:

```text
111789566208.dkr.ecr.ap-south-1.amazonaws.com/python-postgres-compose-app:1.0
```

The complete workflow was tested:

```text
Docker Image
     ↓
Authenticate with ECR
     ↓
Tag Image
     ↓
Push to ECR
     ↓
Pull from ECR
     ↓
Run Container
```

The image was successfully pushed to and pulled from Amazon ECR.

\---

# 15\. End-to-End Workflow

The final project demonstrates:

```text
Developer
    |
    v
Dockerfile
    |
    v
Docker Image
    |
    +--------------------+
    |                    |
    v                    v
Docker Hub             AWS ECR
    |                    |
    v                    v
Pull                   Pull
    |                    |
    +---------+----------+
              |
              v
        Docker Container
              |
              v
        Flask Web Tier
              |
        Docker Network
              |
              v
       PostgreSQL DB Tier
              |
              v
       Named Docker Volume
              |
              v
       Persistent Data
```

\---

# 16\. Key Learning Outcomes

This project demonstrates practical understanding of:

* Linux filesystem and navigation
* Linux file operations and permissions
* Linux processes and package management
* Users and groups
* Disk usage
* Bash variables and control structures
* Bash functions and script arguments
* grep, sed, and awk
* Networking fundamentals
* SSH, curl, ping, and socket inspection
* Cron jobs
* Log analysis
* Dockerfile optimization
* Docker image layers
* Docker build caching
* `.dockerignore`
* Multi-container applications
* Docker Compose
* Service dependencies
* Health checks
* Bridge networking
* Named volumes
* Bind mounts
* Persistent database storage
* Docker Hub
* AWS ECR
* End-to-end containerization

\---

# Conclusion

This project demonstrates how a Python web application and PostgreSQL database can be containerized and managed as a complete 2-tier application.

It combines Linux administration, Bash scripting, networking, Docker, Docker Compose, persistent storage, container registries, and AWS ECR into one practical workflow.


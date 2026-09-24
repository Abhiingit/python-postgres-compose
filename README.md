# 2-Tier Python + PostgreSQL Docker, Kubernetes & CI/CD Application

## Overview

This project demonstrates an end-to-end 2-tier application using Python Flask and PostgreSQL.

The application was first containerized with Docker and Docker Compose, then deployed to Kubernetes using Minikube. The project was later extended with Docker Hub, AWS ECR, GitHub Actions CI/CD, AWS IAM OIDC authentication, a Windows self-hosted GitHub Actions runner, and Jenkins.

The project covers:

- Python Flask
- PostgreSQL
- Docker
- Docker Compose
- Docker networking
- Named volumes
- Bind mounts
- Docker Hub
- AWS ECR
- Kubernetes
- Minikube
- kubectl
- Helm
- Deployments
- Services
- Ingress
- ConfigMaps
- Secrets
- Liveness and readiness probes
- PersistentVolumes and PersistentVolumeClaims
- Rolling updates and rollbacks
- GitHub Actions
- GitHub OIDC
- Self-hosted GitHub Actions runners
- Jenkins Freestyle jobs
- Jenkins Pipelines
- Jenkinsfile / Pipeline as Code

---

# Architecture

```text
                          Client
                            |
                            v
                    +----------------+
                    |   Flask App    |
                    |   Port 5000    |
                    +-------+--------+
                            |
                            | PostgreSQL
                            v
                    +----------------+
                    |  PostgreSQL DB |
                    |    Port 5432   |
                    +----------------+
                            |
                            v
                     Persistent Data
```

For the Kubernetes deployment:

```text
                         Kubernetes / Minikube
                                  |
              +-------------------+-------------------+
              |                                       |
              v                                       v
      Flask Deployment                       PostgreSQL Deployment
         4 replicas                              1 replica
              |                                       |
              v                                       v
       Flask NodePort                         PostgreSQL ClusterIP
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                           Application Traffic
```

The CI/CD workflow adds:

```text
Developer
    |
    | git push / merge to main
    v
GitHub
    |
    v
GitHub Actions
    |
    +-------------------------+
    |                         |
    v                         v
Test + Ruff              Docker Build
                              |
                              v
                         AWS ECR Push
                              |
                              v
                  Windows Self-Hosted Runner
                              |
                              v
                          kubectl
                              |
                              v
                       Minikube Cluster
                              |
                              v
                     Kubernetes Rollout
```

---

# Technologies

- Python 3.13
- Flask
- PostgreSQL 16
- Docker
- Docker Compose
- Bash / Linux
- Kubernetes
- Minikube
- kubectl
- Helm
- Docker Hub
- AWS ECR
- AWS IAM
- GitHub Actions
- GitHub OIDC
- Jenkins
- Groovy / Jenkinsfile

---

# Project Structure

```text
python-postgres-compose/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── app.py
│   ├── __init__.py
│   └── requirements.txt
│
├── tests/
│   └── test_app.py
│
├── scripts/
│   └── health_check.sh
│
├── bind-mount-demo/
│   └── hello.txt
│
├── k8s/
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   └── ingress.yaml
│
├── Dockerfile
├── compose.yaml
├── Jenkinsfile
├── requirements-dev.txt
├── .dockerignore
└── README.md
```

---

# 1. Flask Application

The web tier uses Python Flask.

## GET `/`

Health endpoint:

```text
Python + PostgreSQL application is running!
```

## POST `/messages`

Adds a message to PostgreSQL.

Example:

```json
{
  "message": "Hello from Docker Compose"
}
```

## GET `/messages`

Returns stored messages.

Example:

```text
1 | Persistent data test
2 | Hello from Kubernetes
```

---

# 2. Docker

## Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

## Docker best practices

- `python:3.13-slim` is used as a smaller runtime image.
- Dependencies are copied before application code to improve layer caching.
- `pip --no-cache-dir` avoids storing unnecessary package cache.
- `.dockerignore` reduces the build context.
- Multi-stage builds were studied as an optimization technique, although this small application does not require multiple stages.

---

# 3. Docker Compose

Docker Compose runs two services:

```text
Flask Application
       |
       | db:5432
       v
PostgreSQL
```

The Flask application connects to PostgreSQL through the Compose service name:

```text
DB_HOST=db
```

PostgreSQL has a healthcheck, and the Flask service waits for the database to become healthy.

## Start

```bash
docker compose up -d --build
```

## Check

```bash
docker compose ps
```

## Stop

```bash
docker compose down
```

---

# 4. Docker Networking

Docker Compose automatically creates a bridge network.

The application can reach PostgreSQL using:

```text
db:5432
```

Instead of using the database container IP address, service-name DNS is used.

```text
Flask
  |
  | db:5432
  v
Compose Network
  |
  v
PostgreSQL
```

---

# 5. Docker Volumes

PostgreSQL uses a named volume:

```text
postgres_data
```

mounted at:

```text
/var/lib/postgresql/data
```

Persistence was tested by:

```bash
docker compose down
docker compose up -d
```

The database data remained available.

To remove the volume and stored database data:

```bash
docker compose down -v
```

---

# 6. Bind Mount

A bind mount was demonstrated using:

```text
./bind-mount-demo:/app/data
```

A file created on the Windows host was successfully read from inside a Docker container.

## Named volume vs bind mount

| Feature | Named Volume | Bind Mount |
|---|---|---|
| Managed by | Docker | Host filesystem |
| Example | `postgres_data` | `./bind-mount-demo:/app/data` |
| Database use | Good | Possible but less convenient |
| Development files | Less common | Very useful |

---

# 7. Docker Hub

The application image was pushed to Docker Hub:

```text
abhijeetpratap/python-postgres-compose-app:1.0
```

Workflow:

```text
Dockerfile
   ↓
docker build
   ↓
Docker image
   ↓
Docker tag
   ↓
Docker Hub
   ↓
docker pull
```

---

# 8. AWS ECR

An Amazon ECR repository was created in:

```text
ap-south-1
```

Repository:

```text
python-postgres-compose-app
```

Example image:

```text
111789566208.dkr.ecr.ap-south-1.amazonaws.com/python-postgres-compose-app:1.0
```

The image was successfully pushed to and pulled from ECR.

## ECR workflow

```text
Docker Build
    ↓
AWS Authentication
    ↓
ECR Login
    ↓
Tag Image
    ↓
Push Image
    ↓
ECR
```

---

# 9. Kubernetes with Minikube

Minikube was used to run a local Kubernetes cluster using the Docker driver.

Start the cluster:

```bash
minikube start --driver=docker
```

Check the cluster:

```bash
kubectl get nodes
```

Example:

```text
NAME       STATUS   ROLES           VERSION
minikube   Ready    control-plane   v1.37.0
```

---

# 10. Kubernetes Deployment

The Flask application uses a Kubernetes Deployment:

```text
Deployment
    |
    +---- Pod
    |
    +---- Pod
    |
    +---- Pod
    |
    +---- Pod
```

The application was scaled to 4 replicas:

```bash
kubectl scale deployment python-postgres-app --replicas=4
```

---

# 11. Kubernetes Services

## ClusterIP

Used for internal communication.

```text
Flask
  |
  v
postgres-service:5432
  |
  v
PostgreSQL Pods
```

## NodePort

Used to expose the Flask application through Minikube.

```text
Client
  |
  v
NodePort
  |
  v
Flask Service
  |
  v
Flask Pods
```

## LoadBalancer

A LoadBalancer Service was also tested with:

```bash
minikube tunnel
```

## Ingress

The NGINX Ingress controller was enabled.

Example route:

```text
python-app.local
      |
      v
    Ingress
      |
      v
Flask Service
      |
      v
Flask Pods
```

For the Windows Minikube Docker driver, the hosts file used:

```text
127.0.0.1 python-app.local
```

The route was tested successfully over HTTP.

---

# 12. ConfigMaps and Secrets

## ConfigMap

Non-sensitive PostgreSQL configuration is stored in a ConfigMap:

```text
POSTGRES_DB=appdb
POSTGRES_USER=appuser
```

## Kubernetes Secret

The PostgreSQL password is supplied through a Secret.

A placeholder-only file is stored in:

```text
k8s/secret.example.yaml
```

A real password is never committed to GitHub.

The Flask Deployment receives:

```text
DB_HOST=postgres-service
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=<from Kubernetes Secret>
```

---

# 13. Liveness and Readiness Probes

The Flask Deployment uses HTTP probes on:

```text
/
```

Port:

```text
5000
```

## Liveness

Determines whether the container is alive.

If the container becomes unhealthy, Kubernetes can restart it.

## Readiness

Determines whether the Pod is ready to receive traffic.

```text
Liveness  -> Is it alive?
Readiness -> Is it ready for traffic?
```

---

# 14. PersistentVolume and PersistentVolumeClaim

Kubernetes persistent storage was also practiced separately.

```text
Pod
 ↓
PVC
 ↓
PV
 ↓
Persistent Storage
```

A `1Gi` PVC using the standard StorageClass was dynamically bound to a PersistentVolume.

Persistence was verified by:

1. Writing a file to the mounted volume.
2. Deleting the Pod.
3. Recreating the Pod using the same PVC.
4. Reading the same file again.

---

# 15. Helm

Helm was used as the Kubernetes package manager.

Repository:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

A sample NGINX release was installed:

```bash
helm install nginx-demo bitnami/nginx
```

The release was verified using:

```bash
helm list
```

---

# 16. Linux and Bash

The project also incorporated Linux and Bash practical work.

Topics practiced:

```text
Filesystem navigation
File operations
Permissions
File types
Processes
Package management
Users and groups
Disk usage
Variables
if/else
for/while loops
Functions
Script arguments
grep
sed
awk
SSH
curl
ping
ss
netstat
Cron jobs
Log analysis
```

The project contains:

```text
scripts/health_check.sh
```

---

# 17. Automated Tests

Development dependencies are stored in:

```text
requirements-dev.txt
```

```text
-r app/requirements.txt
pytest
ruff
```

Tests are located in:

```text
tests/test_app.py
```

The test verifies that:

```text
GET /
```

returns HTTP 200 and the expected response.

Run locally:

```bash
python -m pytest -q
```

Example:

```text
1 passed
```

---

# 18. GitHub Actions CI/CD

The project uses GitHub Actions for automated testing, Docker image building, AWS ECR publishing, and deployment to local Minikube.

Workflow file:

```text
.github/workflows/ci.yml
```

## Trigger behavior

Pull requests targeting `main` run:

```text
Test + Ruff
```

A push to `main` runs:

```text
Test + Ruff
      ↓
Docker Build
      ↓
AWS ECR Push
      ↓
Minikube Deployment
```

A merged Pull Request normally creates a push to `main`, which triggers the deployment pipeline.

## CI/CD Architecture

```text
Pull Request
     |
     v
GitHub Actions
     |
     v
Test + Ruff
```

For `main`:

```text
Push to main
      |
      v
Test + Ruff
      |
      v
Docker Build
      |
      v
AWS ECR
      |
      v
Windows Self-Hosted Runner
      |
      v
kubectl
      |
      v
Minikube
      |
      v
Kubernetes Deployment
```

---

# 19. GitHub Actions Testing

The testing job runs on:

```text
ubuntu-latest
```

It performs:

```text
Checkout
   ↓
Python 3.13
   ↓
Install development dependencies
   ↓
pytest
   ↓
Ruff
```

---

# 20. Docker Build and ECR Push

The build job runs only for pushes to `main`.

The Docker image is tagged with the Git commit SHA:

```text
<registry>/python-postgres-compose-app:<commit-sha>
```

and also:

```text
<registry>/python-postgres-compose-app:latest
```

This allows the Kubernetes deployment to use the exact image produced by the current Git commit.

---

# 21. AWS OIDC Authentication

GitHub Actions uses AWS IAM OIDC rather than storing a long-lived AWS access key in GitHub.

The architecture is:

```text
GitHub Actions
      |
      | OIDC token
      v
GitHub OIDC Provider in AWS
      |
      v
IAM Role
      |
      v
Temporary AWS Credentials
      |
      v
Amazon ECR
```

The IAM role is restricted to the repository's `main` branch.

Repository configuration includes:

```text
AWS_ROLE_ARN
```

as a GitHub repository variable.

---

# 22. Kubernetes Deployment from GitHub Actions

The final deployment job runs on a Windows self-hosted GitHub Actions runner.

Runner labels:

```text
self-hosted
Windows
X64
```

The runner accesses the local Minikube cluster using:

```text
C:\actions-runner\kubeconfig
```

The workflow performs:

```text
AWS OIDC authentication
        ↓
Verify Kubernetes access
        ↓
Create PostgreSQL Secret
        ↓
Create ECR image pull Secret
        ↓
Apply ConfigMap
        ↓
Apply PostgreSQL Service
        ↓
Apply PostgreSQL Deployment
        ↓
Apply Application Service
        ↓
Apply Application Deployment
        ↓
Apply Ingress
        ↓
Set exact ECR image
        ↓
Wait for rollout
        ↓
Verify Pods / Services / Ingress
```

The GitHub repository stores the PostgreSQL password as:

```text
K8S_POSTGRES_PASSWORD
```

This password is not stored in the repository.

---

# 23. ECR Image Pull Secret

The Kubernetes deployment uses:

```yaml
imagePullSecrets:
  - name: ecr-registry-secret
```

The GitHub Actions deployment job creates or updates this Kubernetes Secret using an ECR authorization token.

This allows Minikube to pull the private ECR image.

---

# 24. Successful CI/CD Result

The complete GitHub Actions pipeline was successfully tested.

Result:

```text
Test + Lint          ✅
Build + Push to ECR  ✅
Deploy to Minikube   ✅
```

This means the project can automatically:

```text
Git push / merge to main
        ↓
Run tests
        ↓
Build Docker image
        ↓
Push image to ECR
        ↓
Deploy image to local Minikube
```

---

# 25. Jenkins

Jenkins was also installed locally using Docker.

## Jenkins Docker installation

The Jenkins container was created using:

```bash
docker run -d --name jenkins \
  -p 8081:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk21
```

Jenkins was accessed at:

```text
http://localhost:8081
```

Port `8081` was used because port `8080` was already occupied on the Windows host.

## Persistent Jenkins data

Jenkins uses the Docker volume:

```text
jenkins_home
```

mounted at:

```text
/var/jenkins_home
```

This keeps Jenkins jobs and configuration persistent across container restarts.

---

# 26. Jenkins Freestyle Job

A Freestyle job named:

```text
docker-hello
```

was created.

The build step executed shell commands such as:

```bash
echo "Hello from Jenkins!"
echo "Build number: $BUILD_NUMBER"
echo "Workspace: $WORKSPACE"
java -version
```

The Freestyle build completed successfully.

Example result:

```text
Hello from Jenkins!
Build number: 1
Workspace: /var/jenkins_home/workspace/docker-hello
Finished: SUCCESS
```

---

# 27. Jenkins Pipeline

A Jenkins Pipeline job named:

```text
python-pipeline
```

was created.

The pipeline was first tested directly inside the Jenkins UI and then converted to Pipeline as Code.

Pipeline stages:

```text
Checkout
   ↓
Build
   ↓
Test
   ↓
Package
```

---

# 28. Jenkinsfile

The pipeline definition is stored in the repository as:

```text
Jenkinsfile
```

The pipeline uses Declarative Pipeline syntax.

Example structure:

```groovy
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Build') {
            steps {
                echo 'Build stage started'
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage started'
            }
        }

        stage('Package') {
            steps {
                echo 'Packaging application'
            }
        }
    }
}
```

Jenkins was configured using:

```text
Pipeline script from SCM
```

with:

```text
SCM: Git
Repository:
https://github.com/Abhiingit/python-postgres-compose.git

Branch:
*/main

Script Path:
Jenkinsfile
```

The pipeline successfully executed from the Jenkinsfile stored in GitHub.

---

# 29. Jenkins vs GitHub Actions vs GitLab CI

| Feature | Jenkins | GitHub Actions | GitLab CI/CD |
|---|---|---|---|
| Pipeline definition | Jenkinsfile / UI | `.github/workflows/*.yml` | `.gitlab-ci.yml` |
| Platform integration | Standalone | GitHub | GitLab |
| Hosted runners | Usually organization-managed infrastructure | GitHub-hosted or self-hosted | GitLab-hosted or self-managed |
| Self-hosted execution | Yes | Yes | Yes |
| Main configuration style | Groovy / Jenkins Pipeline | YAML | YAML |
| Extension model | Large plugin ecosystem | Actions ecosystem | GitLab components/integrations |
| Repository integration | Multiple SCM providers | Strong GitHub integration | Strong GitLab integration |
| Infrastructure control | Very high | High with self-hosted runners | High with self-managed runners |
| Common use | Highly customized or established CI/CD environments | GitHub-centered development | GitLab-centered DevOps workflows |

## Jenkins

Jenkins is a standalone automation server with a large plugin ecosystem and flexible agent architecture.

It can be useful when organizations need extensive control over infrastructure and build environments, or already have an established Jenkins ecosystem.

Typical architecture:

```text
Jenkins Controller
       |
       +---- Agent
       |
       +---- Agent
       |
       +---- Agent
```

## GitHub Actions

GitHub Actions is integrated directly into GitHub repositories.

It is useful when source code, Pull Requests, Issues, Releases, and CI/CD are already centered around GitHub.

Typical architecture:

```text
GitHub Repository
       |
       v
GitHub Actions
       |
       +---- GitHub-hosted Runner
       |
       +---- Self-hosted Runner
```

## GitLab CI/CD

GitLab CI/CD is tightly integrated with GitLab's repository and DevOps platform.

It uses `.gitlab-ci.yml` and GitLab runners to execute jobs.

Typical architecture:

```text
GitLab Repository
       |
       v
.gitlab-ci.yml
       |
       v
GitLab Runner
```

The choice depends on an organization's existing platform, infrastructure requirements, integrations, and operational preferences.

---

# 30. Jenkins vs GitHub Actions in This Project

This project demonstrates both approaches.

## GitHub Actions

Used for the application CI/CD workflow:

```text
GitHub
   ↓
Test
   ↓
Docker Build
   ↓
ECR Push
   ↓
Self-hosted Windows Runner
   ↓
Minikube
```

## Jenkins

Used to practice:

```text
Freestyle Job
      ↓
Pipeline Job
      ↓
Jenkinsfile
      ↓
Pipeline as Code
```

This demonstrates how two different CI/CD systems can automate similar development workflows.

---

# 31. Final End-to-End Workflow

```text
                    Developer
                        |
                        v
                  Git Repository
                        |
          +-------------+-------------+
          |                           |
          v                           v
   GitHub Actions                  Jenkins
          |                           |
          |                           |
    +-----+-----+                Jenkinsfile
    |           |
    v           v
  Tests       Docker Build
                  |
                  v
                AWS ECR
                  |
                  v
        Windows Self-Hosted Runner
                  |
                  v
               Minikube
                  |
          +-------+-------+
          |               |
          v               v
    Flask Deployment  PostgreSQL
          |               |
          +-------+-------+
                  |
                  v
              Services
                  |
                  v
               Ingress
                  |
                  v
             Application
```

---

# Key Learning Outcomes

This project demonstrates practical experience with:

- Linux administration
- Bash scripting
- Dockerfiles
- Docker image layering
- Docker Compose
- Container networking
- Service discovery
- Named volumes
- Bind mounts
- Docker Hub
- AWS ECR
- AWS IAM
- GitHub OIDC
- GitHub Actions
- Self-hosted runners
- Kubernetes
- Minikube
- kubectl
- Deployments
- Replica scaling
- Rolling updates
- Rollbacks
- ClusterIP
- NodePort
- LoadBalancer
- Ingress
- ConfigMaps
- Secrets
- Liveness probes
- Readiness probes
- PersistentVolumes
- PersistentVolumeClaims
- Helm
- Pytest
- Ruff
- Jenkins Freestyle jobs
- Jenkins Pipelines
- Jenkinsfile
- Pipeline as Code
- CI/CD architecture

---

# Conclusion

This project combines the Docker, Linux, Kubernetes, AWS, CI/CD, and Jenkins practicals into one end-to-end DevOps project.

The final implementation demonstrates how a Flask + PostgreSQL application can be:

```text
Developed
   ↓
Tested
   ↓
Containerized
   ↓
Published to Docker Hub / ECR
   ↓
Deployed to Kubernetes
   ↓
Automatically updated through CI/CD
```

The project also demonstrates two major CI/CD approaches:

```text
GitHub Actions
      +
Jenkins
```

along with the architecture and role of GitLab CI/CD.

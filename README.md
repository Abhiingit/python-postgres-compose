# 2-Tier Python + PostgreSQL Docker & Kubernetes Application

## Overview

This project demonstrates an end-to-end 2-tier application using Python Flask and PostgreSQL, first containerized with Docker and Docker Compose and then deployed to Kubernetes using Minikube.

It covers Dockerfiles, Compose, networking, volumes, bind mounts, Docker Hub, AWS ECR, Kubernetes Deployments, Services, Ingress, ConfigMaps, Secrets, probes, scaling, rolling updates, rollbacks, and persistent storage basics.

## Architecture

```text
Client
  |
  v
Flask Web Tier
  |
  | Docker/Kubernetes network
  v
PostgreSQL DB Tier
  |
  v
Persistent Storage
```

## Technologies

- Python 3.13
- Flask
- PostgreSQL 16
- Docker
- Docker Compose
- Bash/Linux
- Kubernetes
- Minikube
- kubectl
- Helm
- Docker Hub
- AWS ECR

## Project Structure

```text
python-postgres-compose/
├── app/
│   ├── app.py
│   └── requirements.txt
├── scripts/
│   └── health_check.sh
├── bind-mount-demo/
│   └── hello.txt
├── k8s/
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   └── ingress.yaml
├── Dockerfile
├── compose.yaml
├── .dockerignore
└── README.md
```

# Docker

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

### Best practices used

- `python:3.13-slim` keeps the base image smaller.
- `requirements.txt` is copied before `app.py`, allowing Docker to reuse dependency layers when application code changes.
- `pip --no-cache-dir` avoids storing pip cache in the image.
- `.dockerignore` excludes unnecessary files from the build context.
- Multi-stage builds were studied as an optimization technique; this small application does not require a separate build stage.

## Docker Compose

Compose manages the Flask `app` service and PostgreSQL `db` service.

The app waits for PostgreSQL to become healthy using a healthcheck and `depends_on` condition.

```text
Flask app
   |
   | db:5432
   v
PostgreSQL
```

Compose automatically creates a bridge network and service-name DNS makes `db` resolvable from the Flask container.

## Volumes

PostgreSQL uses a named volume:

```text
postgres_data
```

mounted at:

```text
/var/lib/postgresql/data
```

Persistence was tested by removing the containers with `docker compose down`, recreating them with `docker compose up -d`, and confirming the existing database data remained.

`docker compose down -v` removes project volumes and can remove the stored database data.

## Bind Mount

A bind mount was demonstrated using:

```text
./bind-mount-demo:/app/data
```

A file created on the Windows host was successfully read from inside a Docker container.

### Named volume vs bind mount

- Named volume: Docker-managed storage; useful for database data.
- Bind mount: specific host folder mapped into the container; useful for development and files that need direct host access.

## Docker Hub

The application image was pushed and pulled as:

```text
abhijeetpratap/python-postgres-compose-app:1.0
```

Workflow:

```text
Build -> Tag -> Push -> Docker Hub -> Pull
```

## AWS ECR

An ECR repository was created in `ap-south-1`:

```text
python-postgres-compose-app
```

Image:

```text
111789566208.dkr.ecr.ap-south-1.amazonaws.com/python-postgres-compose-app:1.0
```

Workflow:

```text
Build -> Authenticate -> Tag -> Push -> ECR -> Pull -> Run
```

# Kubernetes

## Minikube

Minikube was used to run a local Kubernetes cluster with the Docker driver.

```bash
minikube start
kubectl get nodes
```

## Architecture

```text
                Kubernetes Cluster
                       |
              +--------+--------+
              |                 |
        Control Plane        Node
                                |
                                v
                              Pods
                                |
                            Containers
```

Important control-plane concepts:

- API Server: communication gateway.
- Scheduler: selects where Pods run.
- Controller Manager: works toward the desired state.
- etcd: stores cluster state.

## kubectl

```bash
kubectl get pods
kubectl describe pod <pod>
kubectl apply -f <file>.yaml
kubectl delete -f <file>.yaml
```

`get` provides an overview, `describe` provides detailed information, and `apply` creates or updates declarative resources from YAML.

## Deployment and Scaling

The Flask image was loaded into Minikube:

```bash
minikube image load abhijeetpratap/python-postgres-compose-app:1.0
```

A Deployment was created and scaled from 2 to 4 replicas:

```bash
kubectl scale deployment python-postgres-app --replicas=4
```

## Rolling Update and Rollback

The image was updated from version `1.0` to `2.0`:

```bash
kubectl set image deployment/python-postgres-app app=abhijeetpratap/python-postgres-compose-app:2.0
kubectl rollout status deployment/python-postgres-app
```

Rollback:

```bash
kubectl rollout undo deployment/python-postgres-app
```

The final running image was verified as version `1.0`.

# Kubernetes Services

## ClusterIP

Provides internal-only access to Pods.

```text
Application -> ClusterIP Service -> Pods
```

## NodePort

Exposes a Service on a node port. It was used with Minikube to expose the Flask application.

```text
Client -> NodePort -> Service -> Pods
```

## LoadBalancer

Represents an external load-balancer Service. With Minikube, `minikube tunnel` was used to make the LoadBalancer Service accessible locally.

## Ingress

The NGINX Ingress Controller was enabled in Minikube and the Flask application was routed through:

```text
python-app.local -> Ingress -> Flask Service -> Flask Pods
```

For the Minikube Docker driver on Windows, the hosts file mapped:

```text
127.0.0.1 python-app.local
```

The Ingress route was successfully tested over HTTP.

# ConfigMaps and Secrets

## ConfigMap

The project uses a ConfigMap for non-sensitive PostgreSQL configuration:

```text
POSTGRES_DB=appdb
POSTGRES_USER=appuser
```

## Secret

The database password is supplied through a Kubernetes Secret. A placeholder-only `secret.example.yaml` is kept in the repository; a real password should be created separately and never committed.

Important: Kubernetes Secret values are commonly base64-encoded in API/YAML representations; base64 is encoding, not encryption. Proper RBAC and cluster security are still required.

The Flask Deployment receives:

```text
DB_HOST=postgres-service
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=<from Secret>
```

# Liveness and Readiness Probes

The Flask Deployment uses an HTTP liveness probe and readiness probe on `/` port `5000`.

```text
Liveness  -> Is the container alive? If unhealthy, Kubernetes can restart it.
Readiness -> Is the Pod ready for traffic? If not, Service traffic can be withheld.
```

# PostgreSQL on Kubernetes

PostgreSQL is deployed separately from Flask and exposed through a ClusterIP Service:

```text
postgres-service:5432
```

The Flask application connects to this stable Service name rather than a Pod IP.

The Day-38 application was tested through the Flask NodePort Service, and the following record was successfully inserted into PostgreSQL:

```text
1 | Hello from Kubernetes
```

# PersistentVolume and PersistentVolumeClaim

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

A `1Gi` PVC using the `standard` StorageClass was dynamically bound to a PersistentVolume.

Persistence was verified by writing a file to the mounted volume, deleting the Pod, recreating the Pod with the same PVC, and successfully reading the same file afterward.

# Helm

Helm is the package manager for Kubernetes.

Helm was installed and a Bitnami repository was added:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

A sample NGINX chart was deployed:

```bash
helm install nginx-demo bitnami/nginx
helm list
```

The release was verified with status `deployed`.

# Linux and Bash

The learning workflow also included Linux administration and Bash scripting:

```text
Filesystem navigation
File operations
Permissions
File types
Process management
Package management
Users and groups
Disk usage
Variables
if/else
for/while loops
Functions
Script arguments
grep/sed/awk
SSH/curl/ping/ss/netstat
Cron jobs
Log analysis
```

The project contains a Bash health-check script at:

```text
scripts/health_check.sh
```

# End-to-End Workflow

```text
Linux / Bash
     |
     v
Dockerfile
     |
     v
Docker Image
     |
     +------------------+
     |                  |
     v                  v
Docker Hub            AWS ECR
     |                  |
     +--------+---------+
              |
              v
          Kubernetes
           Minikube
              |
       ConfigMap + Secret
              |
       +------+------+
       |             |
       v             v
 Flask Deployment  PostgreSQL Deployment
       |             |
       v             v
 Flask Service    PostgreSQL Service
       |             |
       +------+------+
              |
              v
            Ingress
              |
              v
           Application
```

# Key Learning Outcomes

This project demonstrates practical experience with:

- Linux administration and Bash scripting
- Dockerfiles and image optimization
- Docker layer caching and `.dockerignore`
- Docker Compose and multi-container applications
- Bridge networking and service discovery
- Named volumes and bind mounts
- Docker Hub and AWS ECR
- Kubernetes Pods and Deployments
- Replica scaling
- Rolling updates and rollbacks
- ClusterIP, NodePort, and LoadBalancer Services
- NGINX Ingress
- ConfigMaps and Secrets
- Liveness and readiness probes
- PersistentVolumes and PersistentVolumeClaims
- Minikube and kubectl
- Helm charts and releases

# Conclusion

This project brings together the Linux, Bash, Docker, and Kubernetes concepts learned through the practical sessions into one documented end-to-end workflow. It demonstrates how a Python web application and PostgreSQL database can be containerized, configured, networked, persisted, published to registries, and deployed and managed on a local Kubernetes cluster.

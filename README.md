# CatchCast

CatchCast is a fishing log application. A user registers a catch by selecting the specie of 
fish then records the length of it, after submitting they will be prompted to share their location. 
The application retrieves the weather for the specific location and stores it in PostgreSQL.

The idea is that when you catch fish (which can be rare), that you for the next year know where, 
what date it was and the weather condition of the catches. Making it easier for you to know where to 
fish, having a more structural approach to fishing rather then just guessing where the fish might be.

Built with an Nginx frontend, two Python REST services, and PostgreSQL, deployed using
Kubernetes.

## Prerequisites

- Git
- Docker Desktop with Kubernetes enabled and running
- kubectl
- A browser with location access enabled

## Deploy

### 1. Clone the repository

```bash
git clone https://github.com/mamz22/PA2577_CatchCast.git
cd PA2577_CatchCast
```

Run the remaining commands from this folder.

### 2. Select the Kubernetes cluster

```bash
kubectl config use-context docker-desktop
kubectl get nodes
```

### 3. Configure credentials

Create `kubernetes/.env` with these two lines. Replace both password placeholders with the
same password containing letters and numbers.

```dotenv
POSTGRES_PASSWORD=REPLACE_WITH_PASSWORD
DATABASE_URL=postgresql+psycopg://castcatch:REPLACE_WITH_PASSWORD@postgres:5432/castcatch
```

Create the Secret:

```bash
kubectl create secret generic postgres-secret --from-env-file=kubernetes/.env -n default
```

### 4. Deploy PostgreSQL

```bash
kubectl apply -f kubernetes/postgres.yaml -n default
kubectl rollout status statefulset/postgres -n default --timeout=180s
```

### 5. Deploy the application

```bash
kubectl apply -f kubernetes/weather-service.yaml -n default
kubectl rollout status deployment/weather-service -n default --timeout=180s

kubectl apply -f kubernetes/catch-service.yaml -n default
kubectl rollout status deployment/catch-service -n default --timeout=180s

kubectl apply -f kubernetes/frontend.yaml -n default
kubectl rollout status deployment/frontend -n default --timeout=180s
```

### 6. Open CastCatch

```bash
kubectl port-forward service/frontend 8080:80 -n default
```

Open http://localhost:8080 and allow browser location access. Keep the terminal running
while using the application.

## Build and push images

Deployment uses prebuilt images. Only run these commands when rebuilding them. Pushing
requires access to the `markomunoz` Docker Hub account; use your own account name and
update the Kubernetes manifests when publishing your own images.

```bash
docker build -t markomunoz/catch-service:v2 ./services/catch-service
docker build -t markomunoz/weather-service:v1 ./services/weather-service
docker build -t markomunoz/castcatch-frontend:v1 ./frontend

docker login

docker push markomunoz/catch-service:v2
docker push markomunoz/weather-service:v1
docker push markomunoz/castcatch-frontend:v1
```

PostgreSQL uses `postgres:16-alpine` and requires no build.

## Software Architecture Diagram

<img width="1845" height="1289" alt="image" src="https://github.com/user-attachments/assets/144d9c4c-dc97-4b47-9099-45d3e6c54f09" />


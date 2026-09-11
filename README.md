CatchCast is a fishing log application.

A user registers a fish from a menu of fishes, then records the length of the fish. When the submit button is pushed the user will 
be asked to share their location. The application uses the location of the user to retrieve the current weather and location information
then stores the catch in PostgreSQL and displays previous catches.

Component                    Responsibility
Frontend/Nginx               Serves the browser interface and forwards /api/ requests

Catch service                Validates requests, retrieves weather, saves and lists catches

Weather service              Retrieves weather and reverse-geocoding information through external REST APIs

PostgreSQL                   Stores catch records on persistent storage


Deployment

A fresh deployment needs a local kubernetes/.env containing:

POSTGRES_PASSWORD=YOUR_PASSWORD
DATABASE_URL=postgressql+psycopg://castcatch:YOUR_PASSWORD@postgres:5432/castcatch
(The username/database must match postgres.yaml)

Then record the deployment commands in this order:

kubectl create secret generic postgres-secret --from-env-file=kubernetes/.env -n default

kubectl apply -f kubernetes/postgres.yaml -n default

kubectl rollout status statefulset/postgres -n default --timeout=180s

kubectl apply -f kubernetes/weather-service.yaml -n default

kubectl apply -f kubernetes/catch-service.yaml -n default

kubectl apply -f kubernetes/frontend.yaml -n default

kubectl get pods,pvc -n default

kubectl port-forward service/frontend 8080:80 -n default

Open http://localhost:8080 with the post-forward terminal running. Inc

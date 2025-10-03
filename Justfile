# == Prep operators for CRDs
helm-repo-add-mongodb:
    helm repo add mongodb https://mongodb.github.io/helm-charts
    helm repo update

helm-install-mongodb-operator:
    helm install community-operator mongodb/community-operator --namespace mongodb-cluster --create-namespace

helm-repo-add-istio:
    helm repo add istio https://istio-release.storage.googleapis.com/charts
    helm repo update

helm-install-istio:
    helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace
    helm install istiod istio/istiod --namespace istio-system --set profile=ambient --set pilot.env.PILOT_ENABLE_ALPHA_GATEWAY_API=true --wait

helm-install-dagster-repo:
    helm repo add dagster https://dagster-io.github.io/helm
    helm repo update

kubectl-install-gateway-api VERSION="v1.3.0":
    kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/{{VERSION}}/standard-install.yaml
    kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/{{VERSION}}/experimental-install.yaml

helm-repo-add-prometheus:
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

setup-k8s-cluster: helm-repo-add-mongodb helm-install-mongodb-operator helm-repo-add-istio helm-install-istio kubectl-install-gateway-api helm-repo-add-prometheus

# == Install app

helm-install-mongodb:
    helm upgrade --install mongodb helm/mongodb -n mongodb-cluster --create-namespace

helm-install-dagster:
    helm upgrade --install dagster-postgres helm/dagster -n dagster --create-namespace
    helm upgrade --install dagster dagster/dagster --namespace dagster -f helm/dagster/official-values.yaml --set postgresql.postgresqlPassword=changeMe

helm-install-apiserver:
    helm upgrade --install apiserver helm/apiserver -n apiserver --create-namespace

helm-install-gatewayapi:
    helm upgrade --install gatewayapi helm/gatewayapi -n istio-gateway --create-namespace

helm-install-spark:
    helm upgrade --install spark helm/spark -n spark-cluster --create-namespace

helm-install-minio:
    helm upgrade --install minio helm/minio -n minio-cluster --create-namespace

helm-install-prometheus:
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -f helm/prometheus/official-values.yaml -n monitoring --create-namespace
    helm upgrade --install prometheus-gateway helm/prometheus -n monitoring --create-namespace

build-apiserver:
    docker build . -t k8s-services/apiserver --target apiserver

build-dagster-service:
    docker build . -t k8s-services/dagster-service --target dagster-codelocation

deploy: build-apiserver build-dagster-service helm-install-gatewayapi helm-install-prometheus helm-install-spark helm-install-minio helm-install-apiserver helm-install-dagster helm-install-mongodb

# === For test publishing data into mongodb using external endpoint

test-insert COUNT="10" APISERVER_BASE_URL="http://localhost:8010":
    APISERVER_BASE_URL={{APISERVER_BASE_URL}} PYTHONPATH=services/ uv run python3 services/apiserver/scripts/internal_insert_cli.py -n {{COUNT}}

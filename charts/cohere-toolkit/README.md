> [!WARNING]
> This helm chart is still experimental and is under active development. 
> 
> It is not recommended for production use.

## Running on Minikube

1. Create a cluster
```shell
minikube start
```

2. Add your Cohere API key to the [`values/local.yaml`](values/local.yaml) file.
```yaml
global:
  cohere:
    api_key: "<YOUR_API_KEY>"
```

3. Install the chart
```shell
helm install cohere-toolkit ./helm/cohere-toolkit \
  --create-namespace \
  -n cohere-toolkit \
  -f ./helm/cohere-toolkit/values/local.yaml \
  --wait --timeout 30s
```

4. In separate shells, port-forward both backend and frontend services
```shell
kubectl port-forward svc/toolkit-backend 8000:80 -n cohere-toolkit
```
```shell
kubectl port-forward svc/toolkit-frontend 4000:80 -n cohere-toolkit
```

5. Open the frontend in your browser
```shell
open http://localhost:4000
```

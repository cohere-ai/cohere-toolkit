echo "Region $GOOGLE_CLOUD_REGION"
echo "Project $GOOGLE_CLOUD_PROJECT"
echo "Service $K_SERVICE"
echo "URL $SERVICE_URL"
gcloud run services describe toolkit-deploy --project oss-toolkit --region us-central1 --format export > service.yaml
sed -i '/startupProbe:/,/timeoutSeconds: 240/c\
    startupProbe:\
      timeoutSeconds: 1\
      periodSeconds: 1\
      failureThreshold: 120\
      httpGet:\
        path: /api/health\
        port: 4000' service.yam
gcloud run services replace service.yaml --project oss-toolkit --region us-central1

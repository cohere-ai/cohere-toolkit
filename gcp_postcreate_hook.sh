#!/bin/bash
echo "Region $GOOGLE_CLOUD_REGION"
echo "Project $GOOGLE_CLOUD_PROJECT"
echo "Service $K_SERVICE"
echo "URL $SERVICE_URL"
gcloud run services describe toolkit-deploy --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_REGION --format export > service.yaml
sed -i '/template:/,/spec:/s/^\(\s*name:\).*/\1 ""/' service.yaml
sed -i '/startupProbe:/,/timeoutSeconds: 240/c\
        startupProbe:\
          timeoutSeconds: 1\
          periodSeconds: 1\
          failureThreshold: 120\
          httpGet:\
            path: /api/health\
            port: 4000' service.yaml
gcloud run services replace service.yaml --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_REGION

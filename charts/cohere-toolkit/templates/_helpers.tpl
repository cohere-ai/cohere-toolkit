
{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cohere-toolkit.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cohere-toolkit.labels" -}}
helm.sh/chart: {{ include "cohere-toolkit.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Database connection string
*/}}
{{- define "cohere-toolkit.database-url" -}}
{{- if .Values.global.database.connection_string }}
{{ .Values.global.database.connection_string }}
{{- else }}
{{- $db := .Values.global.database }}
{{- printf "postgresql+psycopg2://%s:%s@%s:%.0f/%s" $db.username $db.password $db.host $db.port $db.name }}
{{- end}}
{{- end}}

{{- define "cohere-toolkit.redis-url" -}}
{{- $redis := .Values.global.redis }}
{{- printf "redis://:%s@%s:%.0f" $redis.password $redis.host $redis.port -}}
{{- end -}}

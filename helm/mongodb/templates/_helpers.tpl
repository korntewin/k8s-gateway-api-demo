{{- define "mongodb.name" -}}
{{- default .Chart.Name .Values.replicaSet.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mongodb.fullname" -}}
{{- $name := default .Chart.Name .Values.replicaSet.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mongodb.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "mongodb.labels" -}}
helm.sh/chart: {{ include "mongodb.chart" . }}
app.kubernetes.io/name: {{ include "mongodb.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
mongodb.com/cluster: {{ include "mongodb.fullname" . }}
{{- end -}}

{{- define "mongodb.adminSecretName" -}}
{{ include "mongodb.fullname" . }}-admin
{{- end -}}

{{- define "apiserver.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "apiserver.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "apiserver.chart" -}}
{{- printf "%s-%s" .Chart.Name (.Chart.Version | replace "+" "_") -}}
{{- end -}}

{{- define "apiserver.labels" -}}
helm.sh/chart: {{ include "apiserver.chart" . }}
app.kubernetes.io/name: {{ include "apiserver.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "apiserver.selectorLabels" -}}
app.kubernetes.io/name: {{ include "apiserver.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "apiserver.mongodbSecretName" -}}
{{- $mongodb := .Values.mongodb | default (dict) -}}
{{- $secret := $mongodb.connectionStringSecret | default (dict) -}}
{{- if $secret.name -}}
{{- $secret.name -}}
{{- else -}}
{{- printf "%s-mongodb-uri" (include "apiserver.fullname" .) -}}
{{- end -}}
{{- end -}}

{{- define "apiserver.mongodbSecretKey" -}}
{{- $mongodb := .Values.mongodb | default (dict) -}}
{{- $secret := $mongodb.connectionStringSecret | default (dict) -}}
{{- default "uri" $secret.key -}}
{{- end -}}

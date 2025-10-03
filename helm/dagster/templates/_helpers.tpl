{{- define "dagster.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "dagster.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := include "dagster.name" . -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "dagster.labels" -}}
app.kubernetes.io/name: {{ include "dagster.name" . }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "dagster.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dagster.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "dagster.postgresHost" -}}
{{- if .Values.postgres.enabled -}}
{{ include "dagster.fullname" . }}-postgres
{{- else if hasKey .Values.postgres "host" -}}
{{ .Values.postgres.host }}
{{- else -}}
{{ fail "postgres.host must be set when postgres.enabled is false" }}
{{- end -}}
{{- end -}}

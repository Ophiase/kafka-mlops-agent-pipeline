{{- define "mastodon-agent-mlops.name" -}}
{{- default "mastodon-agent-mlops" .Chart.Name -}}
{{- end -}}

{{- define "mastodon-agent-mlops.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s" (include "mastodon-agent-mlops.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "mastodon-agent-mlops.labels" -}}
app.kubernetes.io/name: {{ include "mastodon-agent-mlops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
{{- end -}}

{{- define "mastodon-agent-mlops.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mastodon-agent-mlops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "mastodon-agent-mlops.componentName" -}}
{{- printf "%s-%s" (include "mastodon-agent-mlops.fullname" .) .component | trunc 63 | trimSuffix "-" -}}
{{- end -}}

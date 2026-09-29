AI NOC Agent 🤖

An AI-powered NOC (Network Operations Center) Agent that monitors application and infrastructure health, detects incidents, investigates them using AI, and manages the incident lifecycle through Slack and Jira.

I built this project to explore how AI can be used in day-to-day NOC and DevOps operations to reduce manual investigation effort and bring monitoring, logs, Kubernetes, historical incidents, and operational runbooks together.

🚀 Features

Real-time application and infrastructure monitoring

Automated incident detection

Alert correlation

AI-powered incident investigation

Kubernetes health investigation

Application log analysis

Historical incident search

RAG-based runbook retrieval

Slack incident notifications

Jira incident management

Automatic recovery detection

Prometheus metrics

Grafana monitoring dashboard

Persistent incident history

Local LLM using Ollama

🏗️ Architecture

                    ┌─────────────────────────┐
                    │ Application /           │
                    │ Infrastructure          │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
        ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
        │ Prometheus  │   │ Application │   │ Kubernetes  │
        │   Metrics   │   │    Logs     │   │   Cluster   │
        └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │      AI NOC Agent       │
                    │         FastAPI         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Alert Correlation    │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
        ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
        │   Incident  │  │     RAG     │  │ Historical  │
        │    Store    │  │  Runbooks   │  │  Incidents  │
        └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
               │                │                │
               └────────────────┼────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │         Ollama          │
                    │       llama3.2:3b       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   AI Investigation      │
                    │        Report           │
                    └────────────┬────────────┘
                                 │
                         ┌───────┴───────┐
                         │               │
                         ▼               ▼
                  ┌─────────────┐ ┌─────────────┐
                  │    Slack    │ │     Jira    │
                  └─────────────┘ └─────────────┘

🔄 Incident Lifecycle

Monitoring
    │
    ▼
Signal Detection
    │
    ▼
Alert Correlation
    │
    ▼
Incident Created
    │
    ├──────────────► Slack Notification
    │
    ├──────────────► Jira Issue Created
    │
    ▼
AI Investigation
    │
    ├── Prometheus Metrics
    ├── Application Logs
    ├── Kubernetes Health
    ├── Historical Incidents
    └── Runbook Retrieval
    │
    ▼
Investigation Report
    │
    ▼
Jira → In Progress
    │
    ▼
Continuous Health Monitoring
    │
    ▼
3 Consecutive Healthy Checks
    │
    ▼
Incident Recovered
    │
    ├──────────────► Slack Recovery Notification
    └──────────────► Jira → Done

🧠 AI Investigation

The project uses a locally running Ollama model for incident investigation.

Model: llama3.2:3b

Before asking the AI to investigate an incident, the agent collects information from different sources.

The AI can receive:

CPU utilization

Memory utilization

Application errors

Request metrics

Request latency

Application error logs

Kubernetes pod status

Kubernetes events

Kubernetes restart information

Deployment status

Node pressure information

Correlated signals

Historical incidents

Relevant runbooks

The investigation report includes:

Incident Summary

Confirmed Observations

Correlated Signals

Historical Incident Patterns

Runbook Guidance

Possible Contributing Factors

Root Cause Status

Recommended Read-Only Diagnostic Next Steps

Risk / Safety Note

The AI is instructed to use the available evidence, avoid inventing facts, and clearly separate confirmed observations from possible contributing factors.

🔗 Alert Correlation

The correlation engine combines related signals before sending the investigation context to the AI.

Currently supported signals include:

High CPU

High memory

Application errors

Incident mode

Kubernetes ImagePullBackOff

Kubernetes ErrImagePull

Kubernetes CrashLoopBackOff

High pod restarts

Deployment unavailable

Node MemoryPressure

Node DiskPressure

Node PIDPressure

Example:

CPU High
   +
Memory High
   +
Application Error
   +
Kubernetes Image Pull Failure
        │
        ▼
Correlated Incident
        │
        ▼
AI Investigation

This gives the investigation more context instead of looking at individual signals separately.

☸️ Kubernetes Investigation

The project uses kubectl to collect Kubernetes health information.

The Kubernetes integration can check:

Pod status

Deployment status

Pod restart counts

Pod descriptions

Pod events

Pod logs

Node pressure

For testing the NOC Agent, a deliberately broken pod was created:

noc-broken-pod
      │
      ▼
ImagePullBackOff
      │
      ▼
ErrImagePull
      │
      ▼
Image manifest not found

The Kubernetes failure is collected as part of the incident evidence and passed to the AI investigation.

📚 RAG / Runbook Retrieval

The project includes a RAG layer for operational runbooks using ChromaDB.

The flow is:

Incident Context
      │
      ▼
Search Query
      │
      ▼
ChromaDB
      │
      ▼
Relevant Runbooks
      │
      ▼
AI Investigation

This allows the investigation to use operational guidance along with live monitoring information.

Runbooks are maintained in:

runbooks/

Examples include:

application_http_500.md
kubernetes_image_pull_backoff.md

🗂️ Incident History

Incident information is persisted locally in:

incidents/

Each incident can contain:

Incident ID

Status

Severity

Detection timestamp

Incident evidence

AI investigation result

Recovery information

Jira issue key

Historical incidents can also be searched and used as additional context during investigations.

💬 Slack Integration

Slack is used for incident notifications and investigation updates.

The agent can send:

Incident Detected
        ↓
Slack Notification
        ↓
AI Investigation Report
        ↓
Recovery Notification

This gives the NOC team incident updates without having to continuously monitor the application manually.

🎫 Jira Integration

Jira is used to track the incident lifecycle.

The current flow is:

Incident Detected
        ↓
Jira Issue Created
        ↓
In Progress
        ↓
Incident Recovered
        ↓
Done

The Jira issue key is also stored with the corresponding incident.

📊 Monitoring

Prometheus

Prometheus collects metrics from the demo application and AI NOC Agent.

The AI NOC Agent exposes metrics such as:

noc_active_incidents
noc_critical_incidents
noc_high_incidents
noc_warning_incidents
noc_total_incidents
noc_recovered_incidents
noc_ai_investigations_completed
noc_ai_investigations_failed

Metrics endpoint:

http://localhost:8000/metrics

Grafana

The project includes an AI NOC dashboard with:

CPU Usage

Memory Usage

Application Errors

P95 Request Latency

Incident Mode

Application Error Rate

Request Rate

NOC Demo App Health

Active Incidents

Grafana:

http://localhost:3000

🧪 Incident Simulation

The demo application can simulate a production-like incident.

Start Incident

curl -X POST http://localhost:8001/incident/start

The application enters incident mode and exposes high CPU and memory values.

Stop Incident

curl -X POST http://localhost:8001/incident/stop

The NOC Agent then observes the return to healthy conditions.

An incident is marked recovered after:

3 consecutive healthy checks

🛠️ Tech Stack

Area

Technology

Language

Python

API

FastAPI

AI

Ollama / llama3.2:3b

Monitoring

Prometheus

Visualization

Grafana

Containers

Docker / Docker Compose

Orchestration

Kubernetes

RAG

ChromaDB

Incident Management

Jira

Notifications

Slack

Version Control

Git / GitHub

📁 Project Structure

<pre>
ai-noc-agent/
│
├── agent/
│   ├── main.py
│   ├── agent.py
│   ├── investigator.py
│   ├── detector.py
│   ├── incident_store.py
│   ├── history.py
│   ├── historical_intelligence.py
│   ├── correlation.py
│   └── llm.py
│
├── tools/
│   ├── prometheus.py
│   ├── logs.py
│   ├── kubernetes.py
│   ├── slack.py
│   └── jira.py
│
├── demo_app/
│   └── app.py
│
├── rag/
│   ├── ingest.py
│   └── search.py
│
├── runbooks/
├── incidents/
├── logs/
├── chroma_db/
│
├── monitoring/
│   └── prometheus/
│       └── prometheus.yml
│
├── tests/
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
</pre>

⚙️ Setup

Prerequisites

Make sure the following are installed:

Python 3.12+

Docker Desktop

Docker Compose

Kubernetes

kubectl

Ollama

Git

1. Clone the Repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ai-noc-agent

2. Create Virtual Environment

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Start Ollama

Install Ollama and make sure it is running.

Pull the model:

ollama pull llama3.2:3b

Verify:

ollama list

5. Start Prometheus and Grafana

docker compose up -d

Verify:

docker ps

6. Start the Demo Application

uvicorn demo_app.app:app --host 0.0.0.0 --port 8001

Demo application:

http://localhost:8001

7. Start the AI NOC Agent

Open another terminal:

cd ~/ai-noc-agent
source venv/bin/activate
uvicorn agent.main:app --host 0.0.0.0 --port 8000

Check the agent:

curl http://localhost:8000/health

Expected:

{
  "status": "healthy"
}

🔌 API Endpoints

Endpoint

Description

GET /health

Check AI NOC Agent health

GET /incidents

Get all incidents

GET /incidents/active

Get active incidents

GET /incidents/summary

Get incident summary

GET /incidents/{incident_id}

Get a specific incident

GET /incidents/similar/{incident_id}

Find similar incidents

GET /metrics

Prometheus metrics

🔥 End-to-End Demo

Start the incident simulation:

curl -X POST http://localhost:8001/incident/start

The expected flow is:

Incident Simulation
        ↓
Prometheus Metrics
        ↓
Incident Detection
        ↓
Alert Correlation
        ↓
Incident Created
        ↓
AI Investigation
        ↓
Slack Notification
        ↓
Jira Issue Created
        ↓
Jira → In Progress
        ↓
Health Monitoring
        ↓
3 Healthy Checks
        ↓
Incident Recovered
        ↓
Slack Recovery
        ↓
Jira → Done

Stop the incident simulation:

curl -X POST http://localhost:8001/incident/stop

🔐 Safety Approach

The current implementation follows an investigation-first approach.

The AI can:

Analyze monitoring data

Analyze application logs

Inspect Kubernetes health

Correlate alerts

Search historical incidents

Retrieve runbook information

Recommend read-only diagnostic steps

The current implementation does not automatically execute destructive remediation actions.

This keeps remediation under human control.

📌 Example Incident

A test incident generated by the project included:

Severity: CRITICAL

CPU: 95%
Memory: 92%
Incident Mode: 1

The incident was correlated with multiple signals, including:

CPU_HIGH
MEMORY_HIGH
INCIDENT_MODE
KUBERNETES_IMAGE_PULL_FAILURE

The AI investigation collected the available evidence and used historical incidents and relevant runbooks as additional context.

The incident was then recovered after:

3 / 3 healthy checks

The corresponding Jira incident was moved through the incident lifecycle.

🎯 What I Built / Learned

Through this project I worked on:

Python-based NOC automation

FastAPI

Prometheus monitoring

Grafana dashboards

Kubernetes troubleshooting

Alert correlation

Incident lifecycle management

Local LLM integration

RAG and runbook retrieval

Slack integration

Jira integration

DevOps observability

Human-in-the-loop AI design

🔮 Future Improvements

Possible future improvements include:

Human-approved automated remediation

Additional infrastructure integrations

More advanced alert correlation

More operational runbooks

Production Kubernetes deployment

Authentication and authorization

Production-grade persistent storage

👨‍💻 Author

Tushar Sharma

DevOps | Cloud | NOC Engineering

This project was built as a hands-on exploration of using AI for monitoring, incident investigation, and DevOps operations.

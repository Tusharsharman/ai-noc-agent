AI NOC Agent 🤖

AI NOC Agent is an AI-powered Network Operations Center project that helps monitor application and infrastructure health, detect incidents, investigate problems, and manage the incident lifecycle.

I built this project to understand how AI can be used in NOC and DevOps operations to reduce manual investigation work and bring monitoring, logs, Kubernetes, historical incidents, and operational runbooks into one workflow.

What We Built

The project monitors a demo application and infrastructure using Prometheus and Grafana. When an incident occurs, the agent collects available evidence such as metrics, application errors, logs, Kubernetes health, correlated signals, historical incidents, and relevant runbooks.

The collected information is then used for AI-assisted incident investigation. The investigation provides observations, correlated signals, possible contributing factors, root-cause status, and read-only diagnostic recommendations.

The project also maintains incident information and connects the incident lifecycle with Slack and Jira. Slack is used for notifications and Jira is used for incident tracking and status updates.

What We Used

Python

FastAPI

Prometheus

Grafana

Docker / Docker Compose

Kubernetes / kubectl

Ollama

ChromaDB

RAG / operational runbooks

Slack

Jira

Git / GitHub

Architecture

flowchart TD
    A[Application / Infrastructure] --> B[Prometheus]
    A --> C[Application Logs]
    A --> D[Kubernetes]

    B --> E[AI NOC Agent]
    C --> E
    D --> E

    E --> F[Signal Correlation]
    F --> G[Incident Store]
    F --> H[RAG / Runbooks]
    F --> I[Historical Incidents]

    G --> J[AI Investigation]
    H --> J
    I --> J
    F --> J

    J --> K[Slack]
    J --> L[Jira]

How It Works

The application and infrastructure provide monitoring information to the AI NOC Agent. Prometheus provides metrics, application logs provide error information, and Kubernetes provides pod, deployment, event, restart, and node health information.

The correlation engine combines related signals so that the AI receives a complete incident context instead of investigating each signal separately.

The RAG layer searches operational runbooks, while historical incident information provides additional context from previous incidents.

The AI then investigates the incident using the available evidence. The resulting incident information is stored and the workflow can update Slack and Jira.

The project also supports incident recovery detection by continuously checking system health after an incident.

Incident Detection

The project can identify conditions such as:

High CPU usage

High memory usage

Application errors

Incident mode

Kubernetes ImagePullBackOff

Kubernetes ErrImagePull

Kubernetes CrashLoopBackOff

High pod restarts

Deployment availability issues

Node MemoryPressure

Node DiskPressure

Node PIDPressure

AI Investigation

The AI investigation uses information collected from the monitoring and incident-management components.

It can use:

CPU and memory usage

Application errors

Request metrics and latency

Application error logs

Kubernetes health

Kubernetes events

Correlated signals

Historical incidents

Relevant runbooks

The investigation is designed to work with available evidence and separate confirmed observations from possible contributing factors.

RAG and Historical Incidents

The project includes a RAG layer using ChromaDB for operational runbooks. This allows the agent to retrieve relevant troubleshooting information for an incident.

Incident information is stored locally and can be searched for similar historical incidents. This gives the AI additional context when investigating a new incident.

Slack and Jira

Slack is integrated for incident notifications and investigation updates.

Jira is integrated for incident tracking. The incident can be created and updated through its lifecycle, including recovery and completion.

This connects technical investigation with the normal NOC incident-management workflow.

Monitoring

Prometheus is used for collecting application and AI NOC metrics.

Grafana is used to visualize monitoring information such as CPU, memory, errors, request metrics, application health, and active incidents.

Kubernetes

The project uses Kubernetes health information as part of incident investigation.

The agent can inspect pods, deployments, restart counts, pod descriptions, pod events, pod logs, and node pressure conditions.

A deliberately broken Kubernetes pod was also used to test failure investigation, including ImagePullBackOff and ErrImagePull conditions.

Incident Simulation

The demo application includes an incident simulation that can generate high CPU and memory conditions.

Start an incident:

curl -X POST http://localhost:8001/incident/start

Stop an incident:

curl -X POST http://localhost:8001/incident/stop

This makes it possible to test the monitoring and investigation workflow without depending on a real production failure.

Current Project Status

The main working flow is complete and has been tested locally.

The current project includes:

Application and infrastructure monitoring

Incident detection

Signal correlation

AI-assisted investigation

Kubernetes investigation

Application log analysis

RAG-based runbook retrieval

Historical incident context

Slack notifications

Jira incident tracking

Incident recovery detection

Prometheus metrics

Grafana monitoring

Local AI inference

Future Scope

The project can be extended further with human-approved automated remediation, more infrastructure and cloud integrations, more advanced alert correlation, additional operational runbooks, production Kubernetes deployment, authentication and authorization, and production-grade persistent storage.

The current design keeps investigation separate from destructive remediation so that future remediation actions can remain under human approval.

Project Structure

ai-noc-agent/
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
├── tools/
│   ├── prometheus.py
│   ├── logs.py
│   ├── kubernetes.py
│   ├── slack.py
│   └── jira.py
├── demo_app/
├── rag/
├── runbooks/
├── incidents/
├── logs/
├── chroma_db/
├── monitoring/
├── tests/
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md

Author

Tushar Sharma

DevOps | Cloud | NOC Engineering

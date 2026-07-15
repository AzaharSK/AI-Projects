# AI-Projects
AI-Projects portfolio

### How to apply llm content-safety:
- https://github.com/agentgateway/agentgateway/blob/main/examples/llm-prompt-guard/azure-content-safety-config.yaml

### How to do llm-semantic-routing
- https://github.com/agentgateway/agentgateway/blob/main/examples/llm-semantic-routing/k8s/agentgateway-routing.yaml

### How to apply TLS on LLM:
- https://github.com/agentgateway/agentgateway/blob/main/examples/mcp-tls/config.yaml

### Apply RATE LIMIT on LLM requests:
- https://github.com/agentgateway/agentgateway/blob/main/examples/traffic-ratelimiting-global/ratelimit-config.yaml

### Multi Models unified-gateway:
- https://github.com/agentgateway/agentgateway/blob/main/examples/traffic-unified-gateway/config.yaml


# Production-Grade AI Routing Architecture (Summary)

## Goal

Build an **Enterprise AI Platform** that intelligently decides:

* Which **LLM** to use?
* Should we use **RAG**?
* Should an **AI Agent** be invoked?
* Should the request be **blocked**?
* How to optimize **cost**, **latency**, and **accuracy**?

Instead of always sending every request to GPT-5, we use a **Policy-based AI Router**.

---

# Overall Architecture

```text
                        User
                         │
                         ▼
                API Gateway (Ingress)
                         │
                         ▼
                FastAPI AI Router
        ┌────────────────────────────────┐
        │ Intent Detection               │
        │ Sensitivity Detection          │
        │ Company Knowledge Score        │
        │ RAG Confidence                 │
        │ Utility Score Calculation      │
        │ Token Estimation               │
        │ Latency Prediction             │
        └────────────────────────────────┘
                         │
                         ▼
                OPA Policy Engine
        ┌────────────────────────────────┐
        │ Allow / Deny                   │
        │ Route Selection                │
        │ Organization Policy            │
        │ Compliance Rules               │
        └────────────────────────────────┘
                         │
                         ▼
                  AgentGateway
        ┌────────────────────────────────┐
        │ Authentication                 │
        │ Prompt Guard                   │
        │ Rate Limiting                  │
        │ Retries                        │
        │ Observability                  │
        │ Provider Routing               │
        └────────────────────────────────┘
                         │
        ┌──────────┬──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼
     Small LLM   GPT-5   Internal RAG   AI Agent
```

---

# Responsibilities

## 1. FastAPI AI Router (Decision Engine)

Responsible for intelligence.

Calculates:

* Intent
* Company Knowledge
* Sensitivity
* RAG Confidence
* Utility Score
* Cost
* Latency

Example

```
Prompt:
How do we deploy the Core Banking Service?
```

Extracted Features

```
Company Knowledge = 0.96

Sensitivity = 0.82

RAG Confidence = 0.91

Cost = Medium

Latency = Medium
```

---

## 2. Utility Score

Example formula

```
Utility Score =
0.35 × Company Knowledge
+0.25 × Sensitivity
+0.20 × RAG Confidence
-0.10 × Cost
-0.10 × Latency
```

Result

```
Utility Score = 0.62
```

---

## 3. OPA (Policy Engine)

OPA decides

* Allow?
* Deny?
* Which route?

Example policy

```
if organization == "ExternalVendor"
      deny

if utility < 0.30
      Small LLM

if utility between 0.30 and 0.55
      GPT-5

if utility > 0.55
      Internal RAG

if utility > 0.80
      AI Agent
```

Notice that the routing rules are **configuration (policy)**, not hardcoded in the application.

---

# Example 1

### User

```
Hello
```

Features

```
Intent = Greeting

Utility = 0.10
```

Decision

```
Small LLM
```

Reason

```
Simple request
```

---

# Example 2

### User

```
Explain Kubernetes Pods
```

Features

```
Company Knowledge = 0

Sensitivity = 0

Utility = 0.42
```

Decision

```
GPT-5
```

Reason

```
General knowledge question
```

---

# Example 3

### User

```
How do we deploy the Core Banking Service?
```

Features

```
Company Knowledge = 0.96

Sensitivity = 0.82

RAG Confidence = 0.91

Utility = 0.62
```

Decision

```
Internal Vector DB

+

Internal LLM
```

Reason

```
Uses confidential enterprise knowledge.
```

---

# Example 4

### User

```
Generate Monthly Compliance Report

Read SAP

Create Jira

Email Manager
```

Features

```
Multi-step

Uses tools

Workflow

Utility = 0.90
```

Decision

```
AI Agent
```

Reason

```
Requires planning and tool execution.
```

---

# Example 5

### User

```
Show Internal HR Salary Policy
```

Organization

```
ExternalVendor
```

OPA

```
deny
```

Response

```
403 Forbidden
```

Reason

```
External organizations cannot access HR policies.
```

---

# OPA Input

```
{
  "organization": "RetailBank",
  "utility": 0.62,
  "companyKnowledge": 0.96,
  "intent": "deployment"
}
```

OPA Output

```
{
  "allow": true,
  "route": "internal-rag"
}
```

---

# AgentGateway Role

AgentGateway **does not calculate utility scores**. It executes the decision made by your AI Router.

It provides:

* Authentication
* API key management
* Rate limiting
* Prompt guardrails
* Retries
* Load balancing
* Observability
* Provider routing

Example mapping:

| Route from OPA | AgentGateway backend     |
| -------------- | ------------------------ |
| `slm`          | Mistral / Phi            |
| `gpt5`         | GPT-5                    |
| `internal-rag` | Internal LLM + Vector DB |
| `agent`        | LangGraph Agent          |

---

# Recommended Open Source Stack

| Layer                | Tool                    |
| -------------------- | ----------------------- |
| API                  | FastAPI                 |
| AI Router            | LangGraph               |
| Policy Engine        | Open Policy Agent (OPA) |
| AI Gateway           | AgentGateway            |
| Vector DB            | Qdrant or Milvus        |
| Agent Framework      | LangGraph               |
| Cache                | Redis                   |
| Monitoring           | Prometheus + Grafana    |
| Tracing              | OpenTelemetry           |
| Deployment           | Kubernetes              |
| Messaging (optional) | Kafka                   |

---

# End-to-End Request Flow

```text
User
 │
 ▼
FastAPI
 │
 ├── Intent Detection
 ├── Sensitivity Detection
 ├── Utility Score
 ├── RAG Confidence
 │
 ▼
OPA
 │
 ├── allow?
 ├── deny?
 └── route?
 │
 ▼
AgentGateway
 │
 ├── Authentication
 ├── Prompt Guard
 ├── Rate Limit
 ├── Retry
 ├── Observability
 │
 ▼
Chosen Backend
 │
 ├── Small LLM
 ├── GPT-5
 ├── Internal RAG
 └── AI Agent
 │
 ▼
Response
```

## Why this architecture?

This design follows the **single responsibility principle**:

* **FastAPI + LangGraph**: Understand the request and compute routing signals.
* **OPA**: Enforce business, security, and compliance policies in a centralized, auditable way.
* **AgentGateway**: Securely execute the routing decision, manage providers, and handle operational concerns.
* **LLMs / RAG / Agents**: Perform the actual AI inference or workflow.

This separation makes the platform easier to scale, test, and evolve as new models, policies, and enterprise requirements are introduced.

<img width="1078" height="630" alt="image" src="https://github.com/user-attachments/assets/57e0a86e-bb11-4503-877c-674f58346f22" />

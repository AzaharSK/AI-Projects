# Edge-to-Cloud (Connected Vehicle) Telemetry Platform

## Business Context

Modern automotive OEMs, fleet operators, logistics companies, and mobility providers require real-time visibility into vehicle health, location, driver behavior, connectivity status, and operational efficiency across large fleets. Traditional vehicle diagnostics are reactive and often identify issues only after a vehicle reaches a service center.

The Connected Vehicle Telematics Platform enables continuous collection, processing, storage, and analysis of vehicle telemetry data from millions of connected vehicles. The platform provides near real-time monitoring, predictive maintenance, fleet analytics, remote diagnostics, and over-the-air (OTA) software update capabilities.

## Key Business Objectives

* Enable real-time vehicle monitoring across global fleets.
* Improve vehicle uptime through predictive maintenance.
* Reduce operational costs by identifying inefficient driving patterns.
* Enhance driver safety through proactive alerting and behavioral analytics.
* Support remote diagnostics and troubleshooting without dealership visits.
* Enable OTA software and configuration updates.
* Provide fleet operators with actionable analytics and reporting.
* Create a scalable cloud platform capable of supporting millions of connected vehicles.

## Typical Data Collected

* Vehicle speed, RPM, odometer, gear position.
* Battery voltage, current, state-of-charge (SOC), state-of-health (SOH).
* GPS location, heading, altitude, route information.
* Engine temperature, coolant temperature, fuel consumption.
* Cellular, Wi-Fi, and Bluetooth connectivity status.
* Device health metrics such as CPU, memory, storage, and network utilization.
* Diagnostic Trouble Codes (DTCs) and fault events.
* OTA update status and software version information.

## Primary Business Use Cases

### Fleet Management

* Real-time vehicle tracking.
* Route optimization.
* Fleet utilization monitoring.
* Fuel consumption analysis.
* Driver performance scoring.

### Predictive Maintenance

* Early detection of component degradation.
* Battery health monitoring.
* Engine and powertrain anomaly detection.
* Service scheduling recommendations.

### Driver Safety

* Overspeed detection.
* Harsh braking identification.
* Harsh acceleration detection.
* Unsafe driving behavior alerts.

### Vehicle Diagnostics

* Remote fault code retrieval.
* Vehicle health dashboards.
* Service center integration.
* Root-cause analysis support.

### OTA Software Management

* Remote software deployment.
* Feature enablement.
* Firmware updates.
* Rollback management.
* Campaign monitoring.

### Business Intelligence

* Fleet KPIs.
* Vehicle utilization reports.
* Maintenance cost analysis.
* Battery degradation analytics.
* Regional performance benchmarking.

## Platform Scale

* Supports up to 1 million connected vehicles.
* Processes over 100,000 telemetry events per second.
* Distributed Kafka-based event streaming architecture.
* Multi-service cloud-native deployment.
* Highly available and horizontally scalable infrastructure.

## Technology Stack

* Vehicle Edge: AAOS / Linux Telematics Agent
* Transport: gRPC, HTTPS, Protobuf
* API Layer: FastAPI
* Streaming Platform: Apache Kafka (KRaft)
* Schema Management: Schema Registry
* Processing: Python Microservices
* Storage: PostgreSQL, ClickHouse, Redis, Object Storage
* Monitoring: Prometheus, Grafana, OpenTelemetry
* Deployment: Docker, Kubernetes
* Security: mTLS, JWT Authentication, Certificate Management



Even Many large-scale telemetry platforms are built as domain-agnostic Edge-to-Cloud platforms and then customized for different industries.

```
Automotive 
IoT 
RDK-B Connected devices
AI observability
Fleet management
Telecom
Healthcare devices
smart manufacturing
Industrial automation
EV infrastructure
```


### Layer 1: Common Telemetry Platform (Reusable)
This remains the same across Automotive, AI Observability, Fleet Management, Telecom, and Healthcare.

```
Edge Device
    ↓
Data Collection Agent
    ↓
Protocol Gateway
    ↓
Message Broker
    ↓
Stream Processing
    ↓
Storage
    ↓
Analytics / AI
    ↓
Dashboards / APIs
```
------------------
## Core capabilities should be considered:
- Device registration
- Device identity
- Authentication
- Telemetry ingestion
- Event processing
- Time-series storage
- Alerting
- Fleet/device management
- OTA updates
- Observability
- Digital twin
- Data lake integration


# Referrance:



- https://www.w3.org/TR/viss2-core/#server-capabilities
- https://github.com/COVESA/vehicle_signal_specification/tree/master
- https://github.com/thatlarrypearson/vehicle-telemetry-system/
- https://source.android.com/docs/automotive/vhal/system-properties
- https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/android16-qpr2-release/automotive/vehicle/aidl/generated_lib/4/cpp/AnnotationsForVehicleProperty.h
- https://android.googlesource.com/platform//hardware/interfaces/+/afa170792ae6799435ce0e532365d808aa349ef6/automotive/vehicle/aidl/emu_metadata/android.hardware.automotive.vehicle-types-meta.json
- https://android.googlesource.com/platform//hardware/interfaces/+/6a5da1503331a32cd36759563efc106bf8b278be/automotive/vehicle/aidl/emu_metadata/android.hardware.automotive.vehicle-types-meta.json
- https://android.googlesource.com/platform//hardware/interfaces/+/4e10251c1d8f6925739fd9d26f347b68c1e5c6e3/automotive/vehicle/aidl/impl/default_config/config/DefaultProperties.json


# Telematics Platform Architecture Validation (1M Vehicles)

<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/15e34207-b81b-44c3-9d69-8a8873de908f" />



---------------------------------
# Auth services:
-------------------------------

Yes, in a production-scale telematics platform (handling 1 million+ vehicles), the **Auth Service should absolutely be a separate microservice**.

The Ingestion API layer must remain as lightweight and stateless as possible. It should not be querying a database to verify credentials on every single gRPC/HTTPS request. Instead, it should offload credential verification to the dedicated Auth Service, which issues a short-lived cryptographically signed token (like a JWT). The Ingestion API then verifies this token locally using public keys.

Here is how you can architect the authentication flow using **VIN** and **Service Scopes**, optimized for a high-performance gRPC/HTTPS infrastructure.



## Auth Architecture Flow

Instead of authenticating on every telemetry ping, the vehicle performs a handshake with the Auth Service to get a token, then uses that token for all subsequent data ingestion.

```
+---------------+          1. Auth Request (VIN + Secret/Cert)          +--------------+
|               | ----------------------------------------------------> |              |
|               | <---------------------------------------------------- |              |
|    Vehicle    |               2. Issue Token (JWT)                    | Auth Service |
| (AAOS/Linux)  |                                                       +--------------+
|               |          3. gRPC/HTTPS Stream (Include JWT)
|               | --------------------------------------------------+
+---------------+                                                   |
                                                                    v
                                                       +------------------------+
                                                       |  Ingestion API Layer   |
                                                       | (Validates JWT locally) |
                                                       +------------------------+

```

### Designing the Token (JWT Payload)

The token issued by the Auth Service should embed the **VIN** (as the subject or a custom claim) and the allowed **scopes** (the services or endpoints the vehicle is authorized to access).

Using a standard JWT format allows your Ingestion API to validate the payload in microseconds without a database lookup.

### Example Decoded JWT Payload:

```
{
  "iss": "auth.telematics.company.com",
  "aud": "telematics-ingestion",

  "sub": "device:TCU-9A7B8C6D",
  "vin": "WAQ12345678901",
  "tenant_id": "fleet-acme",
  "fw_version": "2.3.1",
  "vehicle_model": "SUV-X",

  "scopes": [
    "telemetry:publish",
    "diagnostics:publish",
    "trip:publish",
    "status:publish"
  ],

  "iat": 1718100000,
  "exp": 1718103600
}
```

### Vehicle Device Token:
- "sub":"device:TCU-9A7B8C6D",
- "sub": "device:GATEWAY-ABCD1234"
- "sub": "device:AAOS-HEADUNIT-001"

### 

# For APIs:

```
POST /v1/telemetry
POST /v1/device/status
POST /v1/diagnostics
POST /v1/trips/events
POST /v1/ota/status
```

```jsin
{
  "iss": "auth.telematics.company.com",
  "aud": "telematics-platform",
  "sub": "service:ota-manager",
  "client_id": "ota-manager-service",
  "service_name": "ota-management",
  "environment": "production",
  "region": "ap-south-1",

  "scopes": [
    "ota:create",
    "ota:publish",
    "ota:cancel",
    "ota:view",
    "vehicle:command"
  ],

  "iat": 1718100000,
  "nbf": 1718100000,
  "exp": 1718103600,

  "jti": "5c4fd0f8-b2dc-47de-8f0c-9d4d3a1c6e52"
}
```

Used for:
- Create Over-The-Air update campaign
- Schedule Over-The-Air update campaign
- Pause Over-The-Air update campaign
- Cancel Over-The-Air update campaign
- Send Over-The-Air update commands


## Step-by-Step Authentication & Authorization Process

### Step 1: The Vehicle Initial Handshake (With Auth Service)

The vehicle agents initiate an authentication request to the **Auth Service** (typically over HTTPS).

* **The Credentials:** Since you aren't using MQTT (which often uses mTLS), you can use **mTLS** at the HTTPS layer, or a secure hardware-stored secret (TPM chip in the vehicle) passing an asymmetric signature.
* **The Response:** The Auth Service verifies the vehicle identity against your Asset Registry, generates the JWT containing the specific scopes allowed for that vehicle model, signs it with a private key, and returns it to the vehicle.

### Step 2: Local Token Caching at the Edge

The vehicle's `Certificate Manager` or Auth Agent caches this token locally. Because cellular networks drift, the token should have a reasonable lifetime (e.g., 12 to 24 hours) so the vehicle doesn't have to re-authenticate constantly.

### Step 3: Ingestion API Token Verification (Zero DB Calls)

When the vehicle streams data to the Ingestion API via gRPC or HTTPS, it includes the token in the request headers (e.g., `Authorization: Bearer <JWT>` or gRPC metadata).

The Ingestion API layer performs two fast checks:

1. **Cryptographic Validation:** It checks the token's signature using the Auth Service's public key (cached in memory via JWKS). If valid, it trusts the `vin` inside the token.
2. **Scope Verification:** It checks if the requested endpoint matches the granted scopes.

-----------------------------------------------
## Ingestion API services:
-----------------------------------------


Your Ingestion API can use a simple interceptor or middleware matrix to map incoming endpoints to required token scopes: Enforceing the Scopes.

| Incoming Endpoint / gRPC Method | Required Scope in Token | Ingestion Action |
| --- | --- | --- |
| `POST /v1/telemetry` | `telemetry:write` | Extracts `vin` from token $\rightarrow$ Sets Kafka Partition Key to `vin` $\rightarrow$ Publishes. |
| `POST /v1/diagnostics` | `diagnostics:write` | Extracts `vin` from token $\rightarrow$ Publishes to diagnostics Kafka topic. |
| `POST /v1/ota/status` | `ota:write` | Extracts `vin` from token $\rightarrow$ Tracks update progress. |


The ingestion service doesn't care whether the payload contains speed, battery, GPS, CPU, or connectivity data. Its job is simply:
- Authenticate vehicle
- Validate schema
- Add metadata (receive timestamp, vehicle ID, etc.)
- Publish to Kafka
- Return 200 Accepted

v1 API:
```
POST /v1/telemetry
POST /v1/device/status
POST /v1/diagnostics
POST /v1/trips/events
POST /v1/ota/status
```


### Vehicle client requests
```
Vehicle client 
   |
   +--> POST /v1/telemetry
   |
   +--> POST /v1/device/status
   |
   +--> POST /v1/diagnostics
   |
   +--> POST /v1/trips/events
   |
   +--> POST /v1/ota/status
```

### Backend handling  :
```
/v1/telemetry
      |
      +--> vehicle.telemetry.raw (kafka topic)

/v1/device/status
      |
      +--> vehicle.device.status (kafka topic)

/v1/diagnostics
      |
      +--> vehicle.diagnostics.raw (kafka topic)

/v1/trips/events
      |
      +--> vehicle.trip.events (kafka topic)

/v1/ota/status
      |
      +--> vehicle.ota.status (kafka topic)

```


### Why this is highly secure:

The vehicle *cannot lie* about its VIN. Even if a malicious client modifies the data payload to say `VIN: SPY_VIN`, the Ingestion API ignores the payload's claims and strictly uses the `vin` extracted from the cryptographically verified token to populate the Kafka partition key. This prevents cross-vehicle data tampering completely.


------------------

### 1. Periodic Telemetry

- __Sent every:__

- 5 sec
- 10 sec
- 30 sec

depending on requirements.

- __API:__  
```

POST /v1/telemetry
```
- __Schema:__
```json
{
  "vin":"VIN123",
  "timestamp":1781123456789,

  "vehicleMetrics":{
    "speed":72,
    "rpm":2200,
    "odometer":123456
  },

  "batteryMetrics":{
    "soc":81,
    "voltage":13.8
  },

  "locationMetrics":{
    "latitude":12.97,
    "longitude":77.59
  }
}
```
- __Backend:__
```
POST /v1/telemetry
          |
          v
vehicle.telemetry.raw
```


In a high-performance system designed for 1 million vehicles, these endpoints should **not be separate microservices**. Instead, they should exist as **different route handlers inside a single, unified Ingestion Microservice**.

Here is why this distinction matters for your Kafka architecture, and how the internals actually look.

---

## 1. The Design: One Microservice, Multiple Routes

If you built 5 separate microservices (one for telemetry, one for status, one for diagnostics, etc.), you would introduce massive, unnecessary operational overhead: 5 different codebases to maintain, 5 different deployment pipelines, and significantly higher cloud infrastructure costs (paying for minimal CPU/Memory baselines across dozens of redundant containers).

Instead, you build a single **Telematics Ingestion Service** (written in a high-concurrency language like Go or Java).

```
                          +-------------------------------+
                          |   Telematics Ingestion Service|
                          |                               |
POST /v1/telemetry  ----> |  --> Route Handler A -------+ |
POST /v1/diagnostics ----> |  --> Route Handler B -----+ | |
POST /v1/trips/events ---> |  --> Route Handler C ---+ | | |
                          +-------------------------|-|-|-|
                                                    v v v v
                                         +-----------------------------------------+
                                        | Kafka Producers [p1,p2, ..,p6] Clients   |
                                        +------------------------------------------+
                                                       |
         +---------------------------------------------+------------------------------------+
         |                             |                             |                      |
         v                             v                             v                      v
[vehicle.telemetry.raw]    [vehicle.diagnostics.raw]     [vehicle.trip.events]     [vehicle.ota.status]

```

### How it behaves inside the service:

1. The service boots up and creates **one global Kafka Producer client instance** (which handles an internal connection pool to your 6 Kafka brokers).
2. The service exposes your 5 API paths.
3. When a request hits `POST /v1/diagnostics`, the diagnostics route handler accepts the payload, reads the `X-Validated-VIN` header, and hands the message over to the shared Kafka Producer with instructions to drop it into the `vehicle.diagnostics.raw` topic.

---

# Scale Targets : For ~1 million vehicles:
```sql
Vehicles                 : 1,000,000
Upload Interval          : 10 sec
Messages/sec             : ~100,000

Kafka Brokers            : 6–12
Partitions               : 384–768
Replication Factor       : 3
FastAPI Pods             : 20–100
Telemetry Consumers      : 20–50
Alert Consumers          : 10–30
Analytics Consumers      : 20–50
```
# Deployement : 
```
Ingress Pods          100
CPU per Pod           2-4 vCPU
RAM per Pod           2-4 GB
Kafka Workers         20 per pod
Kafka Brokers         6-9
Controllers           3
Partitions            384
Availability Zones    3
```

```
+-----------------------------------------------------------+
|                       Connected Vehicles                  |
|                                                           |
| AAOS / Linux / RTOS                                       |
|                                                           |
| Telemetry Agent                                           |
| GPS Agent                                                 |
| Diagnostics Agent                                         |
| OTA Agent                                                 |
| Certificate Manager                                       |
+------------------------------------------------------------+
Vehicles                 : 1,000,000
Upload Interval          : 10 sec
post Messages/sec        : ~100,000 msg/sec


Consume Stable ingestion API:

      POST /v1/telemetry — raw Protobuf bytes, 202 on enqueue
      POST /v1/diagnostics — DTC fault event ingest
      POST /v1/device/status — compacted topic, latest state
      POST /v1/trips/events — trip lifecycle event ingest
      POST /v1/ota/status — firmware update status ingest

+-----------------------------------------------------------+
                           |
                           |
                 mTLS  HTTPS / MQTT / gRPC
                           |
                           v

+----------------------------------------------------------------------------------------------------------------------------------------------------+
           Global Load Balancer/ API Gateway / Envoy
------------------------------------------------------------------------------------------------------------------------------------------------------
Azure Traffic Manager (DNS-level global LB)
Azure App Gateway/WAF (L7 LB, TLS termination, OWASP WAF)
Envoy sidecar (JWT SCOPED validation via JWKS cache, rate limiting)
Envoy holds the JWKS public key cache so every ingestion pod validates tokens locally without hitting auth_service per request.
+---------------------------------------------------------------------------------------------------------------------------------------------------+
                           |
                           v

+-----------------------------------------------------------+
|              Fastapi Ingestion API Layer  (100 Pods)      |
|                                                           |
| FastAPI / Go / Java                                       |
|                                                           |
| Authentication  (in token/scope)                          |
| Vehicle Identity  (in token/scope)                        |
| Payload Validation  (in token/scope)                      |
| Rate Limiting                                             |
+-----------------------------------------------------------+
                           |
                           |
+------------------------------------------------------------+
|            Bounded asyncio Queue + DLQ                     |
+------------------------------------------------------------+
                           |
                           |
+------------------------------------------------------------+
                     Kafka Producer
Kafka Brokers            : 6–12
Partitions               : 384–768
Replication Factor       : 3
+------------------------------------------------------------+
                           |
                           v

======================================================================
                           KAFKA PLATFORM
======================================================================

                KRaft Controllers (3 or 5)

          +------------+------------+------------+
          | Controller | Controller | Controller |
          +------------+------------+------------+

                              |

+------------+ +------------+ +------------+ +------------+ +------------+ +------------+
| Broker-1   | | Broker-2   | | Broker-3   | | Broker-4   | | Broker-5   | | Broker-6   |
+------------+ +------------+ +------------+ +------------+ +------------+ +------------+

Topics:

vehicle.telemetry.raw
vehicle.location.raw
vehicle.health.raw
vehicle.diagnostics.raw
vehicle.device.status
vehicle.trip.events
vehicle.alerts
vehicle.ota.events
vehicle.telemetry.processed
vehicle.analytics.features

Partition Key = VIN

======================================================================
                              |
                              |

+====================================================================+
                     Telemetry Service
                     Alert Service
                     Analytics Service
                     Storage Service
                     Device Service

+==========================================================+


```




# Telematics Platform Architecture Validation (1M Vehicles)

## Project Structure

Three simplifications applied from the previous complex layout:

```text
telematics-platform/
├── .env                                       # Local-only secrets — never committed (blocked by .gitignore)
├── .env.example                               # Committed safe template — all keys present, no real values
├── .gitignore                                 # Blocks .env, *.pem, credentials.json, __pycache__, .venv
├── Dockerfile                                 # Root dev image — not used for production service builds
├── README.md                                  # Project overview, local setup, and service index
├── pyproject.toml                             # uv workspace root — declares all service members as workspace packages
├── uv.lock                                    # Monorepo-wide locked dependency graph — committed, guarantees reproducibility
│
├── scripts/                                   # Root automation and operations scripts
│   ├── bootstrap_kafka.py                     # KRaft cluster ID binding and initial provisioning
│   ├── create_topics.py                       # Programmatic 384-partition topic provisioning
│   ├── seed_demo_data.py                      # Simulated vehicle telemetry for pipeline testing
│   ├── generate_proto.sh                      # Compiles .proto files into service-local _pb2.py modules
│   └── security_scan.py                       # Pre-CI secret scan — detects hardcoded keys, tokens, PEM blobs
│
├── .github/                                   # GitHub Actions CI/CD — version-controlled with source code
│   └── workflows/
│       ├── ci.yaml                            # PR gate: lint → type-check → unit tests → integration tests
│       ├── build-images.yaml                  # Build + push all service Docker images to ACR on merge to main
│       ├── deploy-staging.yaml                # Helm upgrade to staging AKS cluster on image push
│       ├── deploy-prod.yaml                   # Gated Helm upgrade to prod — requires manual approval
│       ├── proto-compat-check.yaml            # Runs schema registry compatibility check against Protobuf contracts
│       └── secret-scan.yaml                   # Runs scripts/security_scan.py on every PR — blocks on detection
│
├── docs/                                      # Architecture documentation and decision records
│   └── adr/                                   # Architecture Decision Records — why, not just what
│       ├── 0001-kafka-kraft-no-zookeeper.md   # Why KRaft was chosen over ZooKeeper-based Kafka
│       ├── 0002-384-partitions-baseline.md    # Partition count rationale: 100k msg/sec ÷ ~260 msg/s/partition
│       ├── 0003-grpc-not-mqtt.md              # Transport decision: gRPC HTTP/2 persistent vs MQTT broker hop
│       ├── 0004-vin-partition-key.md          # VIN as Kafka partition key for per-vehicle message ordering
│       ├── 0005-bounded-queue-backpressure.md # asyncio.Queue cap + 503 flip instead of unbounded buffer
│       ├── 0006-helm-only-manifests.md        # Single Helm source-of-truth; no raw k8s/ committed
│       ├── 0007-platform-layer-no-plugouts.md # Why plugouts/ was merged into platform/ (single client layer)
│       └── 0008-workers-colocated.md          # Why workers/ moved inside owning services (team ownership)
│
├── deployment/                                # Kubernetes manifests — Helm is the ONLY source of truth
│   └── helm/                                  # All environments rendered from here; no raw k8s/ files
│       ├── Chart.yaml                         # Chart name, version, appVersion metadata
│       ├── values.yaml                        # Default values — dev baseline replicas and limits
│       ├── values-prod.yaml                   # Production overrides — replicas, HPA bounds, limits
│       └── templates/                         # Helm-templated Kubernetes resource manifests
│           ├── _helpers.tpl                   # Shared label, name, selector helper macros
│           ├── deployment-api.yaml            # Ingestion pod deployment (up to 100 replicas via HPA)
│           ├── deployment-workers.yaml        # Per-service worker deployment template
│           ├── service-api.yaml               # ClusterIP service for ingestion tier
│           ├── ingress.yaml                   # k8s Ingress backed by App Gateway ingress controller
│           ├── hpa.yaml                       # HPA — RPS + asyncio queue depth + publish latency
│           ├── pdb.yaml                       # PodDisruptionBudget — quorum safety on rolling updates
│           └── serviceaccount.yaml            # RBAC service account binding per deployed service
│
├── infra-kafka/                               # Local KRaft cluster (3 controllers + 6 brokers, 384 partitions)
│   ├── docker-compose.yml                     # Local dev cluster orchestration stack
│   ├── configs/
│   │   └── kraft/                             # KRaft mode (no ZooKeeper) config files
│   │       ├── controller-1.properties        # KRaft controller node 1 (AZ-a)
│   │       ├── controller-2.properties        # KRaft controller node 2 (AZ-b)
│   │       ├── controller-3.properties        # KRaft controller node 3 (AZ-c)
│   │       ├── broker1.properties             # Broker 1 config (AZ-a)
│   │       ├── broker2.properties             # Broker 2 config (AZ-a)
│   │       ├── broker3.properties             # Broker 3 config (AZ-b)
│   │       ├── broker4.properties             # Broker 4 config (AZ-b)
│   │       ├── broker5.properties             # Broker 5 config (AZ-c)
│   │       └── broker6.properties             # Broker 6 config (AZ-c)
│   └── data/                                  # Persistent event log mounts for local dev
│       ├── broker-logs1/                      # Broker 1 log segment data
│       ├── broker-logs2/                      # Broker 2 log segment data
│       ├── broker-logs3/                      # Broker 3 log segment data
│       ├── broker-logs4/                      # Broker 4 log segment data
│       ├── broker-logs5/                      # Broker 5 log segment data
│       ├── broker-logs6/                      # Broker 6 log segment data
│       ├── controller-logs1/                  # Controller 1 metadata logs
│       ├── controller-logs2/                  # Controller 2 metadata logs
│       ├── controller-logs3/                  # Controller 3 metadata logs
│       ├── metadata1/                         # KRaft metadata quorum store (controller 1)
│       ├── metadata2/                         # KRaft metadata quorum store (controller 2)
│       └── metadata3/                         # KRaft metadata quorum store (controller 3)
│
├── infra/                                     # Shared infra config templates — no real secrets committed here
│   └── secrets/                               # .env.example templates per service — safe reference files
│       ├── ingestion_service.env.example      # Required env vars for ingestion_service (KAFKA_BROKERS, JWKS_URL, etc.)
│       ├── auth_service.env.example           # Required env vars for auth_service (DB_URL, JWT_SECRET_REF, etc.)
│       ├── telemetry_service.env.example      # Required env vars for telemetry_service (CLICKHOUSE_URL, etc.)
│       ├── analytics_service.env.example      # Required env vars for analytics_service (SPARK_MASTER, ADLS_ACCOUNT, etc.)
│       ├── ai_service.env.example             # Required env vars for ai_service (OPENAI_KEY_REF, VECTOR_STORE_URL, etc.)
│       └── platform.env.example               # Shared platform vars (REDIS_URL, SCHEMA_REGISTRY_URL, OTEL_ENDPOINT)
│
├── infra-azure/                               # Azure PaaS infrastructure layer (DNS routing + gateway)
│   ├── traffic-manager/                       # Azure Traffic Manager — global DNS-based routing
│   │   ├── profile.bicep                      # Traffic Manager profile (Performance routing method)
│   │   └── endpoints.bicep                    # Per-region endpoint config (primary + failover AZs)
│   └── app-gateway/                           # Azure Application Gateway / WAF — Layer 7 LB + WAF
│       ├── gateway.bicep                      # App Gateway SKU, backend pools, HTTP listeners
│       ├── waf-policy.bicep                   # WAF policy (OWASP ruleset + custom rate rules)
│       └── ssl-cert.bicep                     # TLS certificate binding (Azure Key Vault reference)
│
├── tests/                                     # Multi-layer validation and reliability testing
│   ├── unit/                                  # Isolated logic tests (no network/broker required)
│   │   ├── test_ingestion_auth_context.py     # VIN extraction from JWT claims
│   │   ├── test_ingestion_queue.py            # Bounded queue backpressure and overload shedding
│   │   ├── test_platform_topic_registry.py    # Topic metadata and partition routing
│   │   ├── test_service_loader.py             # Service module discovery and registration
│   │   └── test_validators.py                 # Payload schema and field validation
│   ├── integration/                           # Subsystem wire contract tests (live broker needed)
│   │   ├── test_api_v1_ingestion.py           # v1 endpoint contract and response semantics
│   │   ├── test_api_v2_ingestion.py           # v2 endpoint contract and response semantics
│   │   ├── test_kafka_publish_workers.py      # Queue-drain to Kafka publish worker correctness
│   │   ├── test_schema_registry_compat.py     # Protobuf schema compatibility against registry
│   │   └── test_dlq_routing.py                # Malformed payload routing to DLQ topics
│   ├── load/                                  # Edge saturation tests via Locust
│   │   ├── locustfile_ingestion_v1.py         # v1 ingest load scenario (100k msg/sec target)
│   │   ├── locustfile_ingestion_v2.py         # v2 ingest load scenario
│   │   └── scenarios/                         # Named load test failure-mode scenarios
│   │       ├── reconnect_storm.py             # 1M vehicles reconnecting simultaneously
│   │       ├── broker_degraded.py             # Broker partition leader failure simulation
│   │       └── queue_saturation.py            # Bounded queue overload and circuit-breaker test
│   └── e2e/                                   # Full end-to-end pipeline correctness tests
│       ├── test_vehicle_to_kafka_path.py      # Vehicle packet → Kafka message correctness
│       ├── test_kafka_to_clickhouse_path.py   # Kafka → ClickHouse sink write verification
│       └── test_kafka_to_opensearch_path.py   # Kafka → OpenSearch index write verification
│
└── APP/                                       # Application source root — all services live here
  ├── main.py                                # Top-level app factory — dev image entry only, not per-service
  ├── config.py                              # Root config loader — reads .env via pydantic-settings
  ├── versioning.py                          # API version constants and route negotiation helpers
  │
  ├── kernel/                                # Shared runtime primitives — all services import from here
  │   ├── lifecycle.py                       # FastAPI lifespan hooks — Kafka producer start/stop/flush
  │   ├── settings.py                        # Pydantic BaseSettings model — reads env vars at startup
  │   ├── health.py                          # /health (liveness) and /ready (readiness) probe handlers
  │   ├── state_machine.py                   # Circuit-breaker — normal / degraded / open state transitions
  │   └── errors.py                          # Shared exception hierarchy and structured error codes
  │
  ├── contracts/                             # Cross-service canonical data contracts
  │   ├── events/                            # Protobuf source files — compiled by generate_proto.sh
  │   │   ├── telemetry.proto                # Vehicle telemetry wire format (GPS, battery, speed, IMU)
  │   │   ├── diagnostics.proto              # DTC fault-code event wire format
  │   │   ├── trips.proto                    # Trip lifecycle event wire format (start/waypoints/end)
  │   │   ├── ota.proto                      # OTA status event wire format
  │   │   └── common.proto                   # Shared types — VIN, timestamp, W3C trace header
  │   ├── schemas/                           # Versioned Pydantic models for internal validation
  │   │   ├── telemetry_v1.py                # Stable v1 telemetry shape — public contract
  │   │   ├── telemetry_v2.py                # Extended v2 telemetry — additional sensor fields
  │   │   ├── diagnostics_v1.py              # v1 diagnostics shape
  │   │   ├── diagnostics_v2.py              # v2 diagnostics — richer DTC metadata
  │   │   └── common.py                      # Shared enums, field types, base model class
  │   └── topics.py                          # Kafka topic names, partition counts, retention class, compaction
  │
  ├── platform/                              # Single shared client code layer — no separate plugouts/
  │   ├── messaging/                         # Kafka clients — ONLY allowed path to create producers
  │   │   ├── kafka_producer.py              # AIOKafka singleton producer factory + lifespan binding
  │   │   ├── kafka_consumer.py              # Consumer group factory with offset commit helpers
  │   │   ├── topic_registry.py              # Topic → partition count → VIN key routing lookup
  │   │   ├── retention_policies.py          # Per-topic retention config (hot / cold / compaction)
  │   │   ├── schema_registry.py             # Confluent/Apicurio registry client + compatibility check
  │   │   ├── topic_admin.py                 # Topic creation, partition expansion, ACL management
  │   │   └── dlq.py                         # DLQ topic publish + structured error metadata header writer
  │   ├── observability/                     # Instrumentation — all services wire through here
  │   │   ├── logging.py                     # Structured JSON logger with correlation ID injection
  │   │   ├── metrics.py                     # Prometheus counter/gauge/histogram registry
  │   │   ├── otel.py                        # OpenTelemetry SDK bootstrap — OTLP exporter config
  │   │   ├── tracing.py                     # W3C TraceContext propagation — gateway → Kafka headers
  │   │   └── prometheus_exporter.py         # /metrics scrape endpoint — Prometheus pull adapter
  │   ├── security/                          # Perimeter security enforcement
  │   │   ├── jwt.py                         # JWT decode, JWKS cache, signature verify, expiry check
  │   │   ├── oauth.py                       # OAuth2 token lifecycle helpers (introspect, refresh)
  │   │   ├── certificates.py                # mTLS vehicle certificate verification
  │   │   └── scopes.py                      # Scope-to-endpoint authorization matrix
  │   ├── cache/                             # Distributed cache clients
  │   │   └── redis_client.py                # Redis cluster client — rate limiting + hot state lookups
  │   ├── storage/                           # All external storage clients in one place
  │   │   ├── db.py                          # SQLAlchemy async engine factory
  │   │   ├── models.py                      # Base declarative model + shared column mixins
  │   │   ├── session.py                     # Async session context manager for request scope
  │   │   ├── clickhouse_client.py           # ClickHouse async insert client — HOT PATH time-series
  │   │   ├── opensearch_client.py           # OpenSearch bulk index client — METRICS PATH
  │   │   ├── adls_client.py                 # Azure Data Lake Gen2 upload client — COLD PATH
  │   │   └── parquet_writer.py              # Delta Lake / Parquet columnar write helper
  │   ├── stream/                            # Stream and batch compute clients
  │   │   ├── flink_client.py                # Flink/Faust job submit and status client
  │   │   └── spark_client.py                # Spark batch job launcher and monitoring client
  │   ├── notifications/                     # Outbound notification clients
  │   │   ├── webhook_client.py              # Outbound webhook delivery with retry + exponential backoff
  │   │   └── push_client.py                 # Push notification channel client
  │   └── utils/                             # Common helpers shared across all services
  │       ├── ids.py                         # Collision-resistant request/packet ID generation (UUID7)
  │       ├── time.py                        # UTC timestamp helpers, interval math, ISO8601 formatting
  │       └── validators.py                  # VIN checksum, ICCID, and payload field validators
  │
  └── services/                              # Independently deployable service images
      ├── ingestion_service/                 # INGRESS AUTHORITY — only service accepting vehicle data
      │   ├── pyproject.toml                 # uv workspace member — inherits shared platform/ deps from workspace root
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Multi-stage build — targets 100-pod horizontal deployment
      │   ├── entrypoint.sh                  # Uvicorn startup with --workers tuned to pod CPU count
      │   ├── main.py                        # App factory — lifespan hooks wire AIOKafka producer singleton
      │   ├── router.py                      # Versioned route composition — mounts v1 + v2 APIRouters
      │   ├── deps.py                        # FastAPI dependency providers — producer, auth_context, settings
      │   ├── classes/
      │   │   ├── ingestion_manager.py       # Request lifecycle: validate → enqueue → respond 202
      │   │   ├── validation_manager.py      # Protobuf decode + schema registry compatibility gate
      │   │   └── publisher_manager.py       # Async queue drain → Kafka publish with DLQ fallback
      │   ├── middleware/
      │   │   ├── request_limits.py          # Max payload size + per-VIN request rate guardrails
      │   │   ├── request_id.py              # W3C traceparent injection + correlation header binding
      │   │   └── error_mapping.py           # Unified HTTP/gRPC error code normalization
      │   ├── infra/
      │   │   ├── auth_context.py            # Extracts trusted VIN + scopes from validated JWT claims
      │   │   ├── queue.py                   # asyncio.Queue (bounded 20k cap) + overload shedding + 503 flip
      │   │   ├── publish_workers.py         # 20 async tasks draining queue to AIOKafka producer
      │   │   └── response.py                # 202 Accepted / 429 Overloaded / 503 Degraded factories
      │   ├── api/
      │   │   ├── v1/                        # Stable ingestion API — gRPC HTTP/2 + HTTPS
      │   │   │   ├── telemetry.py           # POST /v1/telemetry — raw Protobuf bytes, 202 on enqueue
      │   │   │   ├── diagnostics.py         # POST /v1/diagnostics — DTC fault event ingest
      │   │   │   ├── device_status.py       # POST /v1/device/status — compacted topic, latest state
      │   │   │   ├── trips_events.py        # POST /v1/trips/events — trip lifecycle event ingest
      │   │   │   └── ota_status.py          # POST /v1/ota/status — firmware update status ingest
      │   │   └── v2/                        # Extended API — new sensor fields and richer metadata
      │   │       ├── telemetry.py           # POST /v2/telemetry
      │   │       ├── diagnostics.py         # POST /v2/diagnostics
      │   │       ├── device_status.py       # POST /v2/device/status
      │   │       ├── trips_events.py        # POST /v2/trips/events
      │   │       └── ota_status.py          # POST /v2/ota/status
      │   └── domains/                       # VSS vehicle signal domain assets (ingestion-local only)
      │       ├── telemetry/
      │       │   ├── exceptions.py          # Telemetry-specific validation exception types
      │       │   ├── models.py              # Telemetry SQLAlchemy + domain model objects
      │       │   ├── schemas.py             # Pydantic input validation models
      │       │   ├── service.py             # Telemetry domain business logic (enrichment, dedup)
      │       │   ├── repository.py          # Persistence abstraction for telemetry domain
      │       │   ├── registry.py            # Schema registry binding for telemetry wire format
      │       │   └── proto/
      │       │       └── telematics.proto   # Protobuf telemetry contract (compiled → _pb2.py)
      │       └── vehicle/
      │           ├── models.py              # Vehicle identity + state model objects
      │           ├── schemas.py             # Vehicle Pydantic validation structures
      │           ├── service.py             # Vehicle domain orchestration logic
      │           ├── repository.py          # Vehicle persistence abstraction
      │           ├── registry.py            # Schema registry binding for vehicle wire format
      │           └── proto/
      │               └── vehicle.proto      # Protobuf vehicle contract (compiled → _pb2.py)
      │
      ├── auth_service/                      # TOKEN ISSUER — JWT issuance, JWKS, vehicle identity lifecycle
      │   ├── pyproject.toml                 # uv workspace member — declares auth-specific extras (cryptography, argon2-cffi)
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Auth image — separate for canary rollout safety
      │   ├── entrypoint.sh                  # Auth startup (min 12, baseline 20, max 60 replicas)
      │   ├── main.py                        # Auth service bootstrap + lifespan
      │   ├── service.py                     # JWT issuance, claim construction, JWKS publication
      │   ├── repository.py                  # Vehicle credential and identity store abstraction
      │   ├── schemas.py                     # Token request/response Pydantic schemas
      │   └── api/
      │       ├── v1/
      │       │   ├── tokens.py              # POST /v1/auth/tokens — issue short-lived access + refresh
      │       │   └── vehicles.py            # POST /v1/auth/vehicles/register — enroll new VIN
      │       └── v2/
      │           ├── tokens.py              # POST /v2/auth/tokens
      │           └── vehicles.py            # POST /v2/auth/vehicles/register
      │
      ├── telemetry_service/                 # TELEMETRY READ — query and SSE stream API over ClickHouse
      │   ├── pyproject.toml                 # uv workspace member — declares aiochclient, fastapi extras
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Telemetry image — baseline 8 replicas
      │   ├── entrypoint.sh                  # Telemetry process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # Query/stream orchestration (reads ClickHouse via platform/storage)
      │   ├── repository.py                  # ClickHouse + raw Kafka read abstraction
      │   ├── schemas.py                     # Query response Pydantic schemas
      │   ├── models.py                      # Telemetry domain view models (read-side)
      │   ├── workers/                       # Kafka consumers — owned and deployed by telemetry team
      │   │   ├── consumer.py                # AIOKafka consumer — vehicle.telemetry.raw partition group
      │   │   ├── processor.py               # Protobuf decode, transform, write to ClickHouse
      │   │   └── commit.py                  # Manual offset commit — post-write, exactly-once safe
      │   └── api/
      │       ├── v1/
      │       │   ├── stream.py              # GET /v1/telemetry/stream/{vin} — SSE live stream
      │       │   └── historical.py          # GET /v1/telemetry/history/{vin} — ClickHouse range query
      │       └── v2/
      │           ├── stream.py              # GET /v2/telemetry/stream/{vin}
      │           └── historical.py          # GET /v2/telemetry/history/{vin}
      │
      ├── diagnostics_service/               # DIAGNOSTICS — DTC fault processing and correlation
      │   ├── pyproject.toml                 # uv workspace member — declares diagnostics-specific deps
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Diagnostics image — baseline 6 replicas
      │   ├── entrypoint.sh                  # Diagnostics process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # DTC processing, fault scoring, remediation logic
      │   ├── repository.py                  # Diagnostics persistence abstraction (read + write)
      │   ├── schemas.py                     # DTC request/response Pydantic schemas
      │   ├── models.py                      # DTC and fault-code domain models
      │   ├── workers/                       # Kafka consumers — owned and deployed by diagnostics team
      │   │   ├── consumer.py                # AIOKafka consumer — vehicle.diagnostics.raw partition group
      │   │   ├── correlator.py              # Cross-vehicle fault pattern clustering and correlation
      │   │   └── commit.py                  # Offset commit after successful correlation write
      │   └── api/
      │       ├── v1/
      │       │   ├── dtc.py                 # GET/POST /v1/diagnostics/dtc
      │       │   └── clear.py               # POST /v1/diagnostics/clear-faults
      │       └── v2/
      │           ├── dtc.py                 # GET/POST /v2/diagnostics/dtc
      │           └── clear.py               # POST /v2/diagnostics/clear-faults
      │
      ├── alert_service/                     # ALERTS — real-time rules engine and alert management
      │   ├── pyproject.toml                 # uv workspace member — declares alert evaluation extras
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Alert image — baseline 8 replicas
      │   ├── entrypoint.sh                  # Alert process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # Rules evaluation and alert state management
      │   ├── repository.py                  # Alert rule and state persistence abstraction
      │   ├── schemas.py                     # Alert rule configuration and notification schemas
      │   ├── models.py                      # Alert rule and active alert domain models
      │   ├── workers/                       # Kafka consumers — owned and deployed by alert team
      │   │   ├── consumer.py                # High-priority low-latency AIOKafka consumer
      │   │   ├── rules_engine.py            # Threshold / geofence / anomaly rules evaluator
      │   │   └── commit.py                  # Offset commit after confirmed alert state write
      │   └── api/
      │       ├── v1/
      │       │   ├── configurations.py      # POST /v1/alerts/rules — create or update rule config
      │       │   └── active.py              # GET /v1/alerts/active — query active alerts
      │       └── v2/
      │           ├── configurations.py      # POST /v2/alerts/rules
      │           └── active.py              # GET /v2/alerts/active
      │
      ├── analytics_service/                 # ANALYTICS — window aggregation, all sink dispatch, summary API
      │   ├── pyproject.toml                 # uv workspace member — declares Spark client, sink, analytics extras
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Analytics image — baseline 8 replicas
      │   ├── entrypoint.sh                  # Analytics process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # Window aggregation and feature pipeline orchestration
      │   ├── repository.py                  # Analytics result persistence abstraction
      │   ├── workers/                       # All sink + DLQ workers — owned by analytics team
      │   │   ├── consumer.py                # Buffered AIOKafka consumer for analytics topic group
      │   │   ├── windows.py                 # Tumbling/sliding window calculations (5m, 1h, 24h)
      │   │   ├── commit.py                  # Batch offset commit after window flush to sink
      │   │   ├── clickhouse_sink.py         # HOT PATH — ClickHouse async bulk insert via platform/storage
      │   │   ├── opensearch_sink.py         # METRICS PATH — OpenSearch bulk index via platform/storage
      │   │   ├── dlq_worker.py              # DLQ consumer — reads *.dlq topics, emits structured alerts
      │   │   ├── spark_export.py            # COLD PATH — triggers Spark batch job via platform/stream
      │   │   └── parquet_writer.py          # Writes Delta Lake Parquet files to ADLS via platform/storage
      │   └── api/
      │       ├── v1/
      │       │   ├── aggregation.py         # GET /v1/analytics/utilization — fleet utilization summary
      │       │   └── metrics.py             # GET /v1/analytics/summary — aggregated metric snapshots
      │       └── v2/
      │           ├── aggregation.py         # GET /v2/analytics/utilization
      │           └── metrics.py             # GET /v2/analytics/summary
      │
      ├── fleet_service/                     # FLEET — vehicle group topology and inventory management
      │   ├── pyproject.toml                 # uv workspace member — declares fleet service extras
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # Fleet image — baseline 4 replicas
      │   ├── entrypoint.sh                  # Fleet process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # Fleet grouping, topology, and vehicle registry logic
      │   ├── repository.py                  # Fleet persistence abstraction (PostgreSQL)
      │   ├── schemas.py                     # Fleet group and vehicle Pydantic API schemas
      │   ├── models.py                      # Fleet group and vehicle inventory domain models
      │   └── api/
      │       ├── v1/
      │       │   ├── groups.py              # POST /v1/fleet/groups — create or update fleet group
      │       │   └── inventory.py           # GET /v1/fleet/vehicles — paginated vehicle list
      │       └── v2/
      │           ├── groups.py              # POST /v2/fleet/groups
      │           └── inventory.py           # GET /v2/fleet/vehicles
      │
      ├── ota_service/                       # OTA — firmware campaign lifecycle and HTTPS delivery
      │   ├── pyproject.toml                 # uv workspace member — declares OTA service extras
      │   ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
      │   ├── Dockerfile                     # OTA image — baseline 6 replicas
      │   ├── entrypoint.sh                  # OTA process startup
      │   ├── main.py                        # Service bootstrap + lifespan
      │   ├── service.py                     # Campaign orchestration and package validation logic
      │   ├── repository.py                  # OTA campaign and package persistence abstraction
      │   ├── schemas.py                     # Campaign/package API Pydantic schemas
      │   └── api/
      │       ├── v1/
      │       │   ├── campaigns.py           # POST /v1/ota/campaigns — create rollout campaign
      │       │   └── packages.py            # GET/POST /v1/ota/packages — firmware binary management
      │       └── v2/
      │           ├── campaigns.py           # POST /v2/ota/campaigns
      │           └── packages.py            # GET/POST /v2/ota/packages
      │
      └── ai_service/                        # AI — LangGraph multi-agent RAG orchestration + copilot API
          ├── pyproject.toml                 # uv workspace member — declares LangGraph, LangChain, vector DB extras
          ├── requirements.txt               # Docker build pin file — generated from pyproject.toml via `uv export`
          ├── Dockerfile                     # AI image — GPU-compatible base (nvidia/cuda) when needed
          ├── entrypoint.sh                  # AI startup — baseline 4 replicas, scales on concurrency
          ├── main.py                        # AI service bootstrap + lifespan
          ├── orchestrator.py                # LangGraph graph — routes tasks to specialist agents via RAG
          ├── prompts/                       # System prompt templates — one per agent role
          │   ├── fleet_health.md            # Fleet diagnostic analysis + cluster sensor eval prompt
          │   ├── predictive_maintenance.md  # Component degradation curves + failure horizon prompt
          │   └── safety.md                  # G-force/speed anomaly + real-time driver safety prompt
          ├── agents/                        # Specialist LangGraph agent workers
          │   ├── fleet_health_agent.py      # Cluster diagnostic analysis + direct sensor evaluation
          │   ├── predictive_maintenance_agent.py  # Degradation curves, failure probability predictions
          │   └── safety_agent.py            # Safety scoring, hazard detection, incident flagging
          ├── rag/                           # Fleet RAG Knowledge Base integration layer
          │   ├── retriever.py               # Hybrid vector + relational context retriever
          │   ├── embeddings.py              # Text/telemetry metadata vectorization pipeline
          │   └── vector_store.py            # Vector store client — FAISS local or Azure AI Search
          └── api/
              ├── v1/
              │   ├── copilot.py             # POST /v1/ai/copilot/chat — conversational fleet assistant
              │   └── recommendations.py     # GET /v1/ai/predictive/maintenance — maintenance predictions
              └── v2/
                  ├── copilot.py             # POST /v2/ai/copilot/chat
                  └── recommendations.py     # GET /v2/ai/predictive/maintenance
```


## Executive Verdict
Your design direction is strong and production-oriented. The core pattern is correct:
- Stateless ingestion edge
- Auth at perimeter
- Kafka as the decoupled event backbone
- VIN as partition key for per-vehicle ordering
- Separated downstream consumers by domain

Overall readiness: **Good foundation, not yet production-hardened for sustained 100,000 messages/sec** until backpressure, schema governance, and operational controls are tightened.

## Assumption Check (Given Scale Targets)
- Vehicles: 1,000,000
- Upload interval: 10 seconds
- Expected ingest rate: ~100,000 messages/sec
- Kafka partitions: 384 (expandable to 768)
- Brokers: 6 to 9 baseline
- FastAPI pods: up to 100

## What Is Already Correct
1. Thin ingestion service with minimal business logic.
2. Single shared asynchronous Kafka producer per process lifecycle.
3. Partition key by VIN to preserve message order per vehicle.
4. Separation of ingestion and downstream business processing.
5. Dedicated processing paths (alerts, analytics, diagnostics) after Kafka.
6. DLQ concept included.

## Critical Gaps To Close Before Production
1. Backpressure safety at ingestion edge is underdefined.
- Risk: memory pressure and pod crashes during Kafka or network degradation.
- Fix: bounded in-memory queue with overload shedding and circuit-breaker behavior.

2. Fire-and-forget send strategy needs delivery guarantees definition.
- Risk: silent drops if not instrumented and monitored.
- Fix: explicit reliability mode per endpoint class:
  - Critical control/status: await broker ack.
  - High-rate telemetry: queue then asynchronous send with failure accounting.

3. Schema governance is incomplete across teams.
- Risk: producer/consumer drift and runtime decode failures.
- Fix: mandatory schema registry compatibility policy and CI schema checks.

4. Topic model can be simplified for hot-path efficiency.
- Risk: unnecessary fan-out and operations overhead.
- Fix: consolidate highly similar raw streams where processing cadence is shared, and tag payload type.

5. Multi-region failover and data residency are not concretely defined.
- Risk: regional outage blast radius and latency spikes.
- Fix: region-local ingestion plus asynchronous replication to analytics region.

6. Security hardening is implied but not explicitly enforceable.
- Risk: trust boundary ambiguity.
- Fix: perimeter verification only, internal signed identity propagation, strict scope mapping matrix.

## Project Structure Validation
Your structure is comprehensive and modular. It is close to an enterprise-ready layout, but it is too broad for initial delivery unless ownership boundaries are explicit.

### Keep
- Dedicated shared libraries for kafka, observability, security.
- Domain modules split by bounded context.
- Infra and deployment tracks separated from app runtime.
- Worker groups separated by function.

### Improve
1. Introduce a clearly named ingestion boundary package.
- Purpose: host only edge handlers, auth context extraction, queueing, and Kafka publish adapters.

2. Separate platform libraries from domain module code ownership.
- Platform libraries: reusable runtime blocks.
- Domain modules: business workflows and APIs.

3. Add architecture decision records and service contracts folders.
- Purpose: avoid drift between code and architecture claims.

4. Add explicit load-test scenario definitions tied to SLOs.
- Include reconnect storm, broker loss, schema mismatch spike, and AZ failure cases.

5. Add runbooks for degraded modes.
- Queue full mode, registry unavailable mode, broker unavailable mode.

### Structural Improvements Applied (This Revision)

**1. uv Workspace (Dependency Management)**
- Root `pyproject.toml` declares all services as workspace members; `uv.lock` is the single locked graph.
- Each service has its own `pyproject.toml` for extras and a `requirements.txt` generated via `uv export` for Docker.
- Guarantees `pydantic`, `protobuf`, and `aiokafka` versions are consistent across all 9 services.

**2. Architecture Decision Records (`docs/adr/`)**
- 8 seed ADRs covering every major structural and protocol decision (KRaft, 384 partitions, gRPC-not-MQTT, VIN key, bounded queue, Helm-only, platform merge, workers colocation).
- Format: numbered, date-stamped markdown. Engineers read *why* before changing *what*.

**3. CI/CD Pipelines (`.github/workflows/`)**
- `ci.yaml` — PR gate: lint → type-check → unit → integration.
- `build-images.yaml` — builds and pushes all 9 service images to ACR on merge.
- `deploy-staging.yaml` / `deploy-prod.yaml` — Helm upgrade pipelines (prod requires manual approval gate).
- `proto-compat-check.yaml` — blocks merge if Protobuf schema breaks registry compatibility.
- `secret-scan.yaml` — runs `scripts/security_scan.py` on every PR; blocks on any detected secret.

**4. Secrets Management (`infra/secrets/` + `scripts/security_scan.py`)**
- `.env.example` at repo root: committed safe template with all required keys, no real values.
- `infra/secrets/*.env.example` per service: documents every required environment variable with descriptions.
- `scripts/security_scan.py`: regex + entropy scan for hardcoded tokens, PEM blocks, and connection strings.
- `.gitignore` explicitly blocks: `.env`, `*.pem`, `credentials.json`, `*_rsa`, `*.key`.

### Why This Correction Helps
1. Service-first ownership: ingestion, diagnostics, OTA, analytics, and fleet are cleanly separated.
2. Ingestion clarity: all edge concerns (auth context, queue, workers, middleware, routers) live in `ingestion_service`.
3. Domain specificity: VSS ingestion keeps dedicated schemas, models, protobuf, and service classes.
4. Integration safety: outbound systems remain replaceable through platform/ clients.
5. Team scalability: each service can evolve and deploy independently within one repository.

## Recommended Ingestion Runtime Pattern
1. Vehicle sends Protobuf payload over gRPC (or HTTPS fallback).
2. Edge gateway performs TLS termination, JWT validation, and rate limiting.
3. Ingestion API extracts validated identity context (VIN from trusted claims).
4. Ingestion API performs lightweight payload checks only.
5. Message enters bounded async queue.
6. Worker pool publishes to Kafka with partition key = VIN.
7. If queue exceeds threshold, reject with retry signal and metrics emission.

## FastAPI and Worker Sizing Guidance
Given your target envelope:
- Ingress pods: 100
- CPU per pod: 2 to 4 vCPU
- RAM per pod: 2 to 4 GB
- Kafka workers per pod: 20

Suggested operational starting point:
1. Start with 40 to 60 ingestion pods in 3 zones, then auto-scale.
2. Use bounded queue per pod, sized to absorb short spikes (for example 2 to 5 seconds of local load).
3. Keep worker concurrency aligned to CPU and broker throughput, not a fixed static number.
4. Use horizontal pod autoscaling on queue depth + request rate + send latency.

## Kafka Sizing and Topic Policy
1. Brokers: start at 6 across 3 zones; pre-plan rapid expansion to 9.
2. Partitions: 384 is acceptable for start; pre-wire expansion path to 768.
3. Replication factor: 3.
4. Enable compaction only for latest-state topics.
5. Use retention by topic class:
- Hot operational streams: short retention.
- Audit and replay streams: longer retention or tiered storage.

## Reliability and Failure Mode Controls
1. Circuit breaker at ingestion when publish latency or queue depth crosses threshold.
2. Dead-letter topics with structured error metadata.
3. Idempotent producer enabled where supported by chosen client mode.
4. Retry policies with bounded attempts and jitter.
5. Exactly define semantic contract per endpoint:
- At-least-once for telemetry.
- Stronger guarantees for control and safety updates.

## Observability Requirements (Minimum)
1. Ingestion queue depth and queue reject rate.
2. Kafka publish latency and publish error rate by topic.
3. Consumer lag by group and partition hot-spot detection.
4. End-to-end trace correlation from ingress request to downstream sink.
5. Cost signals: per-topic ingest volume, storage growth, cross-zone traffic.

## Security Validation Checklist
1. Perimeter-only authentication and authorization decisions.
2. Trusted identity propagation from gateway to internal services.
3. Short-lived tokens with clear scope matrix.
4. mTLS for service-to-service links where applicable.
5. Strict payload size limits and endpoint-specific quotas.

## Testing Strategy Validation
You have the right test tiers. To be production-ready, explicitly add:
1. Reconnect storm tests (vehicles rejoining after outage).
2. Broker failure and partition leader re-election tests.
3. Schema evolution compatibility tests.
4. Backpressure saturation tests at ingestion queue.
5. End-to-end correctness under duplicated/out-of-order deliveries.

## Priority Implementation Plan
Phase 1 (must-have)
1. Bounded ingestion queue + overload policy.
2. Queue-aware autoscaling and SLO dashboards.
3. Schema registry enforcement and CI compatibility checks.
4. DLQ strategy with automated alert thresholds.

Phase 2 (high impact)
1. Regional ingestion deployment with geo-routing.
2. Topic consolidation and retention tuning.
3. Tiered storage for historical stream cost reduction.

Phase 3 (optimization)
1. Dynamic sampling/aggregation at edge for low-change periods.
2. Adaptive batching by network quality and vehicle state.
3. Cost-aware workload shaping for analytics exports.

## Final Validation Against Attached Architecture Image

### Scope Considered
1. Monorepo with modular microservices and service/plugout boundaries.
2. Python server implementation using FastAPI + AIOKafka across up to 100 ingestion pods.
3. gRPC (HTTP/2) + HTTPS transport only — MQTT and EMQX broker are explicitly excluded by product decision.
4. Schema Registry integration for Protobuf wire compatibility.
5. 1M-vehicle scale target at roughly 100,000 messages/sec.

### Image-to-Target Validation (Pass/Conditional/Fail)
1. Ingestion edge separation and Kafka backbone: **Pass**.
2. Stateless ingestion pods with autoscaling: **Pass**.
3. Topic partitioning by VIN for per-vehicle order guarantees: **Pass**.
4. Processing split into real-time and cold-path pipelines: **Pass**.
5. OAuth/JWT/rate limit controls at gateway tier: **Pass**.
6. MQTT/EMQX broker layer: **Excluded by product decision — Pass**.
  - Transport: gRPC (HTTP/2, persistent connection) for all telemetry and command streams.
  - HTTPS for OTA delivery and non-streaming fallback paths.
  - No MQTT broker (EMQX or otherwise) is present in this architecture.
  - Vehicles connect directly to the ingestion tier over gRPC/HTTPS — no intermediate broker hop.
7. Scale label mismatch (image shows 500k while target is 1M): **Fail until corrected**.
  - Capacity and dashboard labels must reflect 1,000,000 vehicles and 100,000 msg/sec assumptions.

### Mandatory Corrections Before Production Sign-Off
1. Ingestion response semantics
  - Use HTTP 202 Accepted for enqueue success.
  - Do not return success when queue is saturated.

2. Raw Protobuf path
  - Ingestion handlers must read raw request bytes directly for telemetry hot-path.
  - Avoid JSON decode/encode in high-rate handlers.

3. Lifespan-managed singleton producer
  - One AIOKafkaProducer per process via application lifespan hooks.
  - Reused across all route handlers.

4. Bounded queue and worker pool
  - Add bounded asyncio queue in ingress process.
  - Kafka publish executed by worker pool, not by request thread.

5. Circuit breaker and degraded mode
  - When queue depth or publish latency breaches threshold, flip readiness to degraded and return 503.
  - This protects pod memory and enforces edge-side store-and-forward.

6. Idempotent and durable producer profile
  - Use idempotence with strong acknowledgements for durability-sensitive streams.
  - Define endpoint reliability classes (telemetry at-least-once; control/status stricter).

7. Schema Registry wire standardization
  - Enforce registry compatibility in CI.
  - Ensure all producers/consumers use registry-backed Protobuf encoding/decoding.

8. DLQ policy everywhere downstream
  - Any decode/validation failure routes to dedicated DLQ topics with error metadata headers.
  - DLQ volume alarms must be mandatory.

9. End-to-end tracing
  - Inject W3C trace context at gateway.
  - Propagate trace headers into Kafka message headers and downstream logs/spans.

### Monorepo Modular Microservices Validation
The corrected tree is valid for one-repo operation if you enforce this service deployment model:
1. Single monorepo, multi-image deployment model (not a single-image deployment).
2. One unified ingress authority in `services/ingestion_service` for all public ingestion endpoints.
3. `services/auth_service` is deployed with ingress tier capacity policy (same horizontal scale envelope where required).
4. Other services remain independently deployable: `ota_service`, `fleet_service`, `analytics_service`, `alert_service`, and `diagnostics_service`.
5. Data and ML planes are separately deployable units: ClickHouse, OpenSearch, AI RAG services, Spark jobs, and Azure Data Lake integration jobs.
6. Outbound integrations remain isolated in plugout adapters so sinks can be replaced without changing domain logic.
7. Shared platform messaging package is the only allowed path to Kafka producer creation.

### Confirmed Deployment Assumptions
1. Monorepo only, with service-level autonomous deployments.
2. Ingress authority exists only in `services/ingestion_service`; no duplicated ingress routers in other services.
3. `services/ingestion_service` is sized to the 100-pod ingress profile; `services/auth_service` scales independently with a lower baseline and burst capacity.
4. Domain/API services (`ota_service`, `fleet_service`, `analytics_service`, `alert_service`, `diagnostics_service`) are independently deployable.
5. Processing and storage systems (ClickHouse, OpenSearch), AI RAG plane, Spark workloads, and Azure Data Lake export pipelines are independently deployable.

### Kubernetes Manifest Standardization
Primary mechanism should be **Helm charts** for all environments.
1. Helm is the source of truth for rendered manifests.
2. Raw `deployment/k8s` files should be either generated artifacts or strictly reference-only examples.
3. CI should block drift between Helm templates and any committed rendered manifests.

### Deployment Validation Profile (Target)
1. Ingress pods (`ingestion_service`): up to 100 to handle 1M connected vehicle traffic.
2. Auth pods (`auth_service`): baseline 20, minimum 12, maximum 60 (burst up to 100 only during reconnect storms).
3. Pod sizing: 2 to 4 vCPU and 2 to 4 GB RAM.
4. Kafka publish workers per pod: baseline 20, tune by CPU saturation and publish latency.
5. Kafka brokers: start 6, expand to 9 as throughput and retention require.
6. Controllers: 3 (or 5 for larger control-plane resilience).
7. Partitions: 384 baseline with preplanned expansion to 768.
8. Availability zones: 3.
9. Domain/API services are horizontally scaled independently from ingress plane.
10. Data/ML pipelines (ClickHouse/OpenSearch/AI RAG/Spark/ADLS exporters) are deployed and scaled independently.

### Auth-Service Deployment Configuration (1M Vehicles)
1. Role split:
  - `auth_service` issues tokens and exposes JWKS.
  - Ingress path validates JWTs with cached JWKS to avoid per-request auth DB lookups.
2. Suggested pod profile:
  - Min replicas: 12
  - Baseline replicas: 20
  - Max replicas: 60
  - Emergency burst cap: 100 (only for large reconnect events)
3. HPA primary metrics:
  - token issuance RPS
  - p95 token issuance latency
  - CPU utilization
  - 429/5xx error rate
4. Runtime envelope per pod:
  - CPU: 2 to 4 vCPU
  - RAM: 2 to 4 GB
5. Operational guidance:
  - Use short-lived access tokens with cached public keys at ingress.
  - Keep refresh/reauth endpoints rate-limited separately from ingestion endpoints.
  - Configure PodDisruptionBudget to preserve quorum during rollouts.
  - Use canary rollout for auth changes to protect ingress stability.

### Deployment Matrix (Concrete)
| Service/Unit | Image Name | Replica Baseline | Autoscale Metric (Primary) | SLO (Primary) | Owning Team |
|---|---|---:|---|---|---|
| ingestion_service | `telematics/ingestion-service` | 24 | ingress RPS + queue depth + p95 publish latency | p95 ingest accept < 120 ms, availability 99.95% | Edge Ingestion Team |
| auth_service | `telematics/auth-service` | 20 | token issuance RPS + p95 issuance latency + CPU + 5xx rate | p95 token issuance < 120 ms, availability 99.95% | Identity Platform Team |
| diagnostics_service | `telematics/diagnostics-service` | 6 | CPU + Kafka consumer lag | p95 API < 250 ms, lag < 30 s | Diagnostics Team |
| ota_service | `telematics/ota-service` | 6 | request rate + job queue depth | p95 API < 300 ms, availability 99.9% | OTA Platform Team |
| telemetry_service | `telematics/telemetry-service` | 8 | stream session count + consumer lag | stream setup p95 < 500 ms, availability 99.9% | Telemetry Domain Team |
| alert_service | `telematics/alert-service` | 8 | rule eval throughput + consumer lag | alert decision p95 < 2 s, availability 99.9% | Fleet Safety Team |
| analytics_service | `telematics/analytics-service` | 8 | batch backlog + consumer lag + CPU | feature pipeline freshness < 5 min | Analytics Engineering Team |
| fleet_service | `telematics/fleet-service` | 4 | API RPS + DB latency | p95 API < 250 ms, availability 99.9% | Fleet Operations Team |
| ai_service (RAG/API) | `telematics/ai-service` | 4 | request concurrency + token latency + CPU/GPU utilization | p95 response < 2.5 s, availability 99.5% | AI Platform Team |
| clickhouse sink workers | `telematics/clickhouse-sink` | 6 | insert queue depth + flush latency | ingest-to-query latency < 60 s | Data Platform Team |
| opensearch sink workers | `telematics/opensearch-sink` | 6 | indexing backlog + reject rate | ingest-to-search latency < 90 s | Search Platform Team |
| spark export jobs | `telematics/spark-exports` | 3 | schedule delay + job duration | batch completion before SLA window end | Data Lake Team |
| adls export pipeline | `telematics/adls-exporter` | 3 | export backlog + failed export count | data availability in ADLS < 15 min | Data Lake Team |

Notes:
1. Baselines are starting points; autoscaling limits should be defined per environment (dev/stage/prod).
2. `ingestion_service` and `auth_service` scale independently from each other and from domain/API services.
3. Helm remains the manifest source of truth; matrix values should map to Helm values files per environment.

### End-State Validation (Python-Only, Defendable)
Validated end-state for design review:
1. Vehicle buffers and batches Protobuf at edge.
2. Transport uses persistent gRPC HTTP/2 for telemetry/commands and HTTPS for OTA/fallback.
3. Envoy/gateway performs TLS termination, JWT authn/authz, and rate limiting before app tier.
4. FastAPI ingestion pods perform lightweight checks and enqueue.
5. Bounded queue and worker pool publish through AIOKafka singleton producers.
6. Kafka feeds domain consumers (telemetry, alert, analytics, storage, device).
7. Consumers apply schema validation and DLQ fail-routing.
8. OpenTelemetry traces correlate request-to-storage path.

## Final Validation Outcome
- Architecture pattern: **Validated with required corrections noted above**.
- File-tree and modular service/plugout strategy: **Validated for single-repo, multi-image microservice operation**.
- Scale readiness for 1M vehicles: **Conditionally validated after mandatory corrections and load tests are passed**.

## Main Structural Features (Confirmed)
Conditionally approved for implementation planning and phased rollout. The structure is modular, monorepo-compatible, and deployable as independent service images with centralized ingress authority.

1. Single monorepo with multi-image, service-level autonomous deployment.
2. One ingress authority only in `services/ingestion_service`.
3. `ingestion_service` plus `auth_service` deployment model for ingress plane scaling (up to 100 pods as needed).
4. Other business services independently deployable.
5. ClickHouse/OpenSearch/AI RAG/Spark/ADLS pipelines independently deployable.
6. One primary Kubernetes generation mechanism: Helm as source of truth.



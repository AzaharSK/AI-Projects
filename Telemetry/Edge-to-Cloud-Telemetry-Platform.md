# Edge-to-Cloud Telemetry Platform
- Automotive
- IoT
- RDK-B Connected devices
- AI observability
- Fleet management
- Telecom
- Healthcare devices
- smart manufacturing
- Industrial automation
- EV infrastructure



Many large-scale telemetry platforms are built as domain-agnostic Edge-to-Cloud platforms and then customized for different industries.

## Layer 1: Common Telemetry Platform (Reusable)

This remains the same across Automotive, AI Observability, Fleet Management, Telecom, and Healthcare.

```json

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

## Core capabilities:

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



<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/e4ae0d8a-35b6-4cd3-81bb-8478af122f6a" />


```json

┌──────────────────────────────┐
│ Edge Devices                 │
│ Cars, Routers, AI Servers    │
│ Medical Devices              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Edge Agent                   │
│ OpenTelemetry Collector      │
│ FluentBit                    │
│ Custom Agent                 │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Protocol Gateway             │
│ MQTT                         │
│ HTTP                         │
│ gRPC                         │
│ Kafka                        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Streaming Layer              │
│ Apache Kafka                 │
│ Apache Pulsar                │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Real-Time Processing         │
│ Apache Flink                 │
│ Spark Streaming              │
└──────────────┬───────────────┘
               │
       ┌───────┴─────────┐
       ▼                 ▼
 Time-Series DB      Data Lake
 VictoriaMetrics     Iceberg
 ClickHouse          S3
 InfluxDB            MinIO
       ▼                 ▼
   Alerting       ML/Analytics

```

<img width="887" height="527" alt="image" src="https://github.com/user-attachments/assets/fc58ed6e-e28c-4485-baff-5861a6cbe8eb" />



```png
=========================================================================================================================
                                           INGESTION LAYER (EDGE & SECURITY)
=========================================================================================================================

                       [ 500,000 Connected Vehicles / Simulators ]
                                            |
                                    (MQTT over TLS 1.3)
                                            v
                                [ Azure Traffic Manager ] (Global DNS Routing)
                                            |
                                            v
                     [ Azure Application Gateway / WAF (Layer 7 LB) ] 
                                            |
                   +------------------------+------------------------+
                   |                                                 |
         [ OAuth2 Token Exchange ]                          [ Global Rate Limiting ]
         (Azure Entra ID Integration)                       (Redis Cluster Distributed Counter)
                   |                                                 |
                   +------------------------+------------------------+
                                            v
                           [ Internal Load Balancer (ILB) ]
                                            |
                                            v
                     [ EMQX Enterprise Broker Cluster ] (Auto-Scaling Node Group)
                                            |
                                      (HTTP/2 POST)
                                            v
                             [ Internal Load Balancer (ILB) ]
                                            |
                                            v
                     [ FastAPI Telemetry Servers ] (Stateless Pods / Auto-Scaling)
                                            |
                   +------------------------+------------------------+
                   |                                                 |
        [ Protobuf Deserialization ]                        [ Hot State Tracking / Lookups ]
        (Fast Memory Unpacking)                             (Redis Distributed Cache Cluster)
                   |                                                 |
                   +------------------------+------------------------+
                                            v
                               [ Apache Kafka Ingest Backbone ]
                               (Partitioned by Vehicle VIN)

=========================================================================================================================
                                     PROCESSING & DATA STORAGE PIPELINES
=========================================================================================================================

                                    [ Apache Kafka ]
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
   (HOT PATH: Near Real-Time)      (METRICS & LOGS PATH)            (COLD PATH: Big Data Analytics)
         |                                  |                                  |
         v                                  v                                  v
 [ Apache Flink / Faust ]            [ OpenSearch Cluster ]            [ Kafka Connect Engine ]
 (Stream Processing / Anomalies)    (Structured Traces & Logs)                 |
         |                                  |                        (Batch Files via Parquet)
         v                                  v                                  v
 [ ClickHouse Cluster ]                     |                    [ Azure Data Lake Storage (ADLS Gen2) ]
 (High-Throughput Time-Series)              |                                  |
         |                                  |                                  v
         +----------------------------------+                       [ Apache Spark Cluster ]
         |                                                          (Delta Lake Lakehouse Engine)
         |                                                                     |
         v                                                                     v
 [ Fleet RAG Knowledge Base ] <------------------------------------------- (Scheduled Batch Sync)
 (Hybrid Vector Store + Relational Context Engine)

=========================================================================================================================
                                ORCHESTRATION & MULTI-AGENT AI SYSTEM LAYER
=========================================================================================================================

                                [ Fleet RAG Knowledge Base ]
                                            |
                                            v
                                [ LangGraph Orchestrator ]
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
         v                                  v                                  v
 [ Fleet Health Agent ]          [ Predictive Maintenance Agent ]    [ Safety & Compliance Agent ]
 - Diagnostic Analysis           - Component Degradation Curves      - G-Force/Speed Inconsistencies
 - Direct Sensor State Evaluation - Failure Horizon Predictions       - Real-time Driver Safety Scoring

=========================================================================================================================
                                 ISOLATED OPERATIONAL OBSERVABILITY LAYER
=========================================================================================================================

 [ FastAPI Telemetry Pods ]        [ Spark/Flink Tasks ]        [ LangGraph Worker Threads ]
            |                                |                               |
     (Scrape: /metrics)               (OTel Exporter)                 (Tracing/Spans)
            +--------------------------------+-------------------------------+
                                             v
                               [ Prometheus Monitoring Cluster ]
                                             |
                                             v
                               [ Grafana Dashboards Engine ]
                               (System Health + Cost / AI Cost)

```



<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/1a26e9d8-b11c-47b5-8b1a-431213cc66b0" />

-------------------------------------------------------------


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
+-----------------------------------------------------------+
                           |
                           |
                  HTTPS / MQTT / gRPC
                           |
                           v

+-----------------------------------------------------------+
|                  Global Load Balancer                     |
+-----------------------------------------------------------+
                           |
                           v

+-----------------------------------------------------------+
|                 Ingestion API Layer                       |
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
                     Kafka Producer
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


```


Your vehicle telematics platform design is fundamentally solid. It follows industry best practices for high-throughput IoT ingestion: using a **Global Load Balancer**, a **stateless, thin ingestion layer**, and **Kafka** as the decoupled streaming backbone with `VIN` as the partition key to guarantee ordered processing per vehicle.

Since you explicitly want to **exclude MQTT**, we need to ensure your remaining protocols (HTTPS and gRPC) handle the unique challenges of connected vehicles—specifically intermittent connectivity, high overhead, and bi-directional communication (like OTA commands).

Here is a verification of your current architecture and targeted improvements to make it production-ready for 1 million vehicles.

----------------------------

## 1. Protocol Strategy (Without MQTT)

Without MQTT, you are left with **HTTPS** and **gRPC**. For a 1-million-vehicle fleet, here is how you should split their duties:

### Keep HTTPS for:

* **OTA Updates & Large File Uploads (`/v1/ota/status`):** Great for large payload chunks, retry mechanisms, and standard CDN integration.
* **Fallback Ingestion:** If a vehicle's environment restricts custom binary protocols, standard HTTPS/JSON or HTTPS/Protobuf works anywhere.

### Use gRPC for:

* **High-Frequency Telemetry & Location (`/v1/telemetry`, `/v1/location`):** gRPC runs over HTTP/2, allowing multiplexing (multiple requests over one connection) and heavy header compression (HPACK). This slashes cellular data costs compared to HTTPS.
* **Bi-directional Streaming:** Since you aren't using MQTT for push notifications, you need a way to send commands *to* the vehicle (e.g., remote unlock, OTA trigger). A long-lived **gRPC bi-directional streaming connection** can replace MQTT's pub/sub for this purpose.

---

## 2. Ingestion Layer Improvements

The current design states: *"The ingestion service doesn't care whether the payload contains speed, battery, GPS... Its job is simply: Validate schema, Publish to Kafka..."*

To support 1 million vehicles efficiently without MQTT, update your ingestion services with these enhancements:

### Move from Multi-Endpoint to Single Stream (for Telemetry)

Instead of forcing the vehicle client to make 4 separate HTTP/gRPC calls (`/v1/telemetry`, `/v1/device/status`, `/v1/diagnostics`, `/v1/trips/events`), **batch them into a single unified telemetry payload framework** (e.g., using Protobuf).

* *Why?* Opening separate network connections or hitting distinct endpoints on cellular networks drastically drains the vehicle's battery and wastes data overhead.

### Enforce Protobuf Schemas

Do not pass raw JSON through your ingestion layer. Use **Protocol Buffers (Protobuf)** across gRPC and HTTPS.

* It provides strict schema enforcement at the edge.
* The payload is binary, minimizing cellular bandwidth costs.

### Move Rate Limiting to the Load Balancer/API Gateway

Your diagram shows Rate Limiting inside the Ingestion API Layer (FastAPI/Go/Java).

* **Improvement:** Move token bucket rate limiting to your Global Load Balancer or a dedicated API Gateway (like Envoy or Kong). If 100,000 vehicles reconnect simultaneously after a tunnel, you want to drop unauthorized or abusive traffic *before* it hits your compute layer.

---

## 3. Kafka Infrastructure Right-Sizing

For 1 million vehicles emitting data (assuming a standard 10-second ping interval), your platform will handle roughly **100,000 writes per second**.

### Kafka Broker Count

Your diagram shows 6 Brokers. While this is a good starting point for high availability, you should scale this based on network throughput and retention rather than a arbitrary number. For 100k events/sec, **6 to 9 brokers** (across 3 Availability Zones) is a healthy, safe size.

### Topic Consolidation

You currently have 10 distinct topics. While logically clean, too many internal topics can cause high disk I/O and replication overhead if not managed carefully.

* **Recommendation:** Combine `.raw` topics that share the same processing cadence. For example, combine `vehicle.telemetry.raw`, `vehicle.location.raw`, and `vehicle.health.raw` into a single `vehicle.telemetry.raw` topic. You can use a `payload_type` field inside the Protobuf message to let downstream consumers filter what they need.

### Compaction vs. Deletion

* For status topics like `vehicle.device.status`, enable **Kafka Log Compaction**. This ensures Kafka only keeps the latest known state for each VIN, turning Kafka into a fast state cache for downstream applications.

---

## 4. Vehicle Edge Architecture Considerations

Because you are discarding MQTT (which natively handles offline storage and automatic retries), the responsibility shifts heavily to your vehicle edge agents (AAOS/Linux/RTOS):

* **Edge Buffering (SQLite / Flash Memory):** When a vehicle goes through a cellular dead zone, the Telemetry and GPS agents *must* write data to a local queue or embedded DB (like SQLite).
* **Backpressure & Batching:** When connectivity returns, the edge agent should not dump 2 hours of data all at once in separate API calls. It must batch the backlogged data and stream it via gRPC using a controlled backpressure algorithm so it doesn't overwhelm your Ingestion API.

---

## Optimized Architecture Flow

1. **Vehicle (AAOS/Linux)** $\rightarrow$ Batches data into **Protobuf** format.
2. **Transport** $\rightarrow$ Persistent **gRPC (HTTP/2)** tunnel for Telemetry/Commands; **HTTPS** for OTA.
3. **Gateway / Load Balancer** $\rightarrow$ Terminates TLS, handles Rate Limiting, authenticates JWT tokens.
4. **Ingestion Service (Go / Java)** $\rightarrow$ Lightweight validation, routes to a consolidated `vehicle.data.raw` Kafka topic (Partitioned by `VIN`).




To take that conceptual pipeline and turn it into actual infrastructure for 1 million vehicles, you have to lean heavily on the capabilities of **gRPC, Envoy (or a similar cloud-native API Gateway), and standard public key cryptography**.

Here is exactly *how* each step happens under the hood, along with the concrete configuration patterns used to build it.

---

## 1. Vehicle Side: Batching and Streaming via gRPC

Instead of sending JSON over standard HTTP REST endpoints, the vehicle's telemetry agent compiles data into a highly compressed binary format using **Protocol Buffers (Protobuf)**, and streams it over a single, long-lived connection.

### How the Data is Defined (Protobuf)

You define a single, unified schema that can hold various types of metrics (location, battery, diagnostics).

```protobuf
syntax = "proto3";
package telematics;

message TelemetryRecord {
  int64 timestamp = 1;
  GPSData gps = 2;
  BatteryData battery = 3;
  repeated DiagnosticTroubleCode dtcs = 4;
}

message TelemetryStreamRequest {
  // Token passed in gRPC Metadata (headers), VIN inferred from token by backend
  repeated TelemetryRecord records = 1; 
}

message StreamResponse {
  string status = 1; // e.g., "ACK"
}

service TelemetryService {
  // Client-to-server streaming: Vehicle opens one stream and pushes batches continuously
  rpc StreamTelemetry(stream TelemetryStreamRequest) returns (StreamResponse);
}

```

### How the Vehicle Executes This:

1. **Edge Buffering:** The Telemetry Agent writes data points to an internal lightweight cache (like an in-memory ring buffer or SQLite) every second.
2. **Batching:** Every 10 seconds (or 30 seconds to save cellular data), it flushes the cache, serializes the `TelemetryStreamRequest` into a tight binary payload, and pushes it over the open gRPC stream.
3. **Multiplexing:** Because gRPC runs on HTTP/2, if a remote command needs to be sent *to* the vehicle (like a door unlock request), the cloud can send a message down the exact same TCP connection simultaneously without waiting for the vehicle's upload upload to finish.

---

## 2. Gateway / Load Balancer: The "Heavy Lifter"

You should not write custom code in Java or Go to handle TLS termination, rate limiting, and token validation for 1 million concurrent connections. You offload this entirely to a reverse proxy/infrastructure layer like **Envoy Proxy**, **AWS ALB**, or **Kong Gateway**.

Here is exactly how a gateway like Envoy handles a vehicle request:

### A. TLS Termination

The vehicle establishes an encrypted connection. The Load Balancer handles the heavy cryptographic math of decrypting the packet (TLS termination) right at the edge of your cloud data center. From the Load Balancer inward to your Ingestion API, the traffic usually travels over fast, unencrypted HTTP/2.

### B. Rate Limiting at the Edge

The gateway keeps track of incoming connections using a **Token Bucket** algorithm (often backed by a fast, central Redis cluster).

* If a vehicle malfunctions and tries to flood the system with 1,000 gRPC requests per second, the Gateway instantly drops the traffic and returns an HTTP `429 Too Many Requests` status (or gRPC code `ResourceExhausted`).
* **Crucial benefit:** Your actual Ingestion API code never sees this abusive traffic, protecting your Kafka clusters from collapsing.

### C. JWT Authentication (Zero-Lookup Validation)

This is where the magic happens. The Gateway does not talk to your database or call your Auth Service to check if the vehicle is logged in. It uses **Asymmetric Cryptography**.

1. **The Public Key Cache:** When your Auth Service boots up, it publishes its *Public Key* to an internal URL (known as a JWKS endpoint). The Gateway downloads this public key and stores it in memory.
2. **The Verification Math:** When the vehicle sends a gRPC request, it passes the JWT in the request metadata (headers). The Gateway grabs the JWT, uses the cached public key to run a mathematical check against the token signature.
3. **The Result:** If the math checks out, the Gateway *knows* with 100% certainty that the Auth Service issued this token, that the token hasn't been modified, and that it is still valid.

---

## 3. Passing Data from Gateway to Ingestion API

Once the Gateway approves the token, it forwards the decrypted, authenticated gRPC stream to your downstream Ingestion API (written in Go or Java).

To make life easy for your Ingestion API, the Gateway extracts the **VIN** from the validated JWT claims and injects it into a standard internal header (e.g., `X-Validated-VIN`).

### Envoy Configuration Example (Conceptual)

This snippet shows how Envoy natively handles the JWT verification and header injection without touching your application code:

```yaml
http_filters:
  - name: envoy.filters.http.jwt_authn
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
      providers:
        auth_service_provider:
          issuer: auth.telematics.yourcompany.com
          remote_jwks:
            http_uri:
              uri: http://auth-service.internal/.well-known/jwks.json
              cluster: auth_service_cluster
              timeout: 1s
          # Extract claims and inject them into custom headers for the Ingestion API
          payload_in_metadata: verified_jwt_payload
  - name: envoy.filters.http.router # Forwards the request to your Go/Java service

```

### The Ingestion API's Only Job:

By the time the request hits your Go or Java service, it is guaranteed to be clean, authenticated, and rate-limited. Your code simply reads the `X-Validated-VIN` header, takes the binary Protobuf payload, and pushes it directly into Kafka using the VIN as the partition key.


```
# Step: 1 Auth services:

Yes, in a production-scale telematics platform (handling 1 million+ vehicles), the **Auth Service should absolutely be a separate microservice**.

The Ingestion API layer must remain as lightweight and stateless as possible. It should not be querying a database to verify credentials on every single gRPC/HTTPS request. Instead, it should offload credential verification to the dedicated Auth Service, which issues a short-lived cryptographically signed token (like a JWT). The Ingestion API then verifies this token locally using public keys.

Here is how you can architect the authentication flow using **VIN** and **Service Scopes**, optimized for a high-performance gRPC/HTTPS infrastructure.

---

## 1. Architecture Flow

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

---

## 2. Designing the Token (JWT Payload)

The token issued by the Auth Service should embed the **VIN** (as the subject or a custom claim) and the allowed **scopes** (the services or endpoints the vehicle is authorized to access).

Using a standard JWT format allows your Ingestion API to validate the payload in microseconds without a database lookup.

### Example Decoded JWT Payload:

```json
{
  "iss": "auth.telematics.yourcompany.com",
  "sub": "vin_1234567890ABCDEFG",
  "iat": 1718100000,
  "exp": 1718186400,
  "vin": "1234567890ABCDEFG",
  "scopes": [
    "telemetry:write",
    "diagnostics:write",
    "ota:read",
    "ota:write"
  ]
}

```




---

## 3. Step-by-Step Authentication & Authorization Process

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

---

## 4. How the Ingestion API Enforces the Scopes

Your Ingestion API can use a simple interceptor or middleware matrix to map incoming endpoints to required token scopes:

| Incoming Endpoint / gRPC Method | Required Scope in Token | Ingestion Action |
| --- | --- | --- |
| `POST /v1/telemetry` | `telemetry:write` | Extracts `vin` from token $\rightarrow$ Sets Kafka Partition Key to `vin` $\rightarrow$ Publishes. |
| `POST /v1/diagnostics` | `diagnostics:write` | Extracts `vin` from token $\rightarrow$ Publishes to diagnostics Kafka topic. |
| `POST /v1/ota/status` | `ota:write` | Extracts `vin` from token $\rightarrow$ Tracks update progress. |

### Why this is highly secure:

The vehicle *cannot lie* about its VIN. Even if a malicious client modifies the data payload to say `VIN: SPY_VIN`, the Ingestion API ignores the payload's claims and strictly uses the `vin` extracted from the cryptographically verified token to populate the Kafka partition key. This prevents cross-vehicle data tampering completely.


# Step 2: ingestion services:  Vehicle Side APIs for 1M Vehicle Platform:

The ingestion service doesn't care whether the payload contains speed, battery, GPS, CPU, or connectivity data. Its job is simply:

- Authenticate vehicle
- Validate schema
- Add metadata (receive timestamp, vehicle ID, etc.)
- Publish to Kafka
- Return 200 Accepted


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
      +--> vehicle.telemetry.raw

/v1/device/status
      |
      +--> vehicle.device.status

/v1/diagnostics
      |
      +--> vehicle.diagnostics.raw

/v1/trips/events
      |
      +--> vehicle.trip.events

/v1/ota/status
      |
      +--> vehicle.ota.status

```

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


### Vehicle API Service
```
GET /vehicles/{vin}
GET /vehicles/{vin}/health
GET /vehicles/{vin}/telemetry/latest
```
Reads from:
```
PostgreSQL
Redis
ClickHouse
```
__Not directly from Kafka producer/broker.__


### Fleet API Service

```
GET /fleet/summary
GET /fleet/trips
GET /fleet/alerts
Analytics API Service
GET /analytics/top-speeding-vehicles
GET /analytics/battery-health
```
__Queries ClickHouse or Cassandra.__



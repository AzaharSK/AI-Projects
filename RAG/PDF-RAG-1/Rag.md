<img width="1842" height="988" alt="image" src="https://github.com/user-attachments/assets/88452afc-7f22-4d62-b311-c7ef223c8353" />
<img width="1573" height="905" alt="image" src="https://github.com/user-attachments/assets/c2878ecc-24ee-4f17-902e-45433fbbeb9f" />
<img width="1796" height="915" alt="image" src="https://github.com/user-attachments/assets/0e1f14ef-c2f9-4188-9326-1f60fe122933" />

<img width="1573" height="905" alt="image" src="https://github.com/user-attachments/assets/585f837b-5710-4c77-a634-2de5080bb74c" />
<img width="1796" height="915" alt="image" src="https://github.com/user-attachments/assets/a8f426e2-458c-4a07-b095-b65a38e1b88d" />
<img width="1796" height="915" alt="image" src="https://github.com/user-attachments/assets/2d710245-871b-4201-a298-9baf16c955f5" />
<img width="1796" height="915" alt="image" src="https://github.com/user-attachments/assets/b1c1435d-bbe1-4dd6-b4fc-6d76dc9e68c5" />


<img width="1376" height="768" alt="Gemini_Generated_Image_ck1npick1npick1n" src="https://github.com/user-attachments/assets/32af98cd-a25e-4b57-a851-4047a699e8f1" />


# RAG Architecture Specification

Based on the system architectural diagram and technical breakdown, the custom Retrieval-Augmented Generation (RAG) pipeline is structured into six independent operational layers. The system is designed framework-free to give fine-grained control over document processing, embedding generation, vector indexing, and completion logic.

---

## 1. User Interface (Streamlit Web UI)
Acts as the presentation layer, bridging user actions with the underlying RAG system engine.
* **File Uploader:** Provides an interactive upload zone for users to ingest target PDF documents dynamically into the runtime filesystem.
* **Query Interface:** A contextual input field enabling users to submit natural language questions and "chat" directly with their uploaded files.
* **Model Toggling & Interactivity:** Employs Streamlit control components (such as radio buttons) to allow the end-user to dynamically switch model configurations mid-session.

## 2. Session State Management
Ensures application state persistence, context tracking, and data continuity across stateless rendering cycles.
* **RAG System Instance:** Holds a persistent reference to the core engine, preserving database configurations, connection pools, and instantiated model bindings.
* **Processed Files Set:** Maintains an in-memory unique registry of previously ingested document signatures to mitigate redundant parsing and duplicated vector creation.
* **State Operations:** Syncs user-driven configuration changes (e.g., swapping from cloud APIs to local models) to maintain real-time application responsiveness.

## 3. PDF Processing Module
Responsible for custom document ingestion, text sanitization, and structural decomposition without reliance on heavy framework orchestrators.
* **SimplePDFProcessor:** The central processing controller overseeing the ingestion workflow for raw document inputs.
* **read_pdf:** Extracts raw textual sequences and metadata out of complex, binary-encoded portable document format (PDF) inputs.
* **create_chunks:** Executes splitting algorithms to segment large strings into optimal, uniform token lengths (chunks), preparing text blocks for serialization and vector mapping.

## 4. Core RAG System Engine
Coordinating orchestrator that ties text fragments, vector maps, operational business logic, and completion nodes together.
* **SimpleRAGSystem:** The underlying engine class supervising workflows between semantic searches, text chunks, models, and metadata tracking.
* **Embedding Function Interface:** A standardized wrapper providing unified input/output mapping for generating vector vectors from text fragments.
* **LLM Model Selector:** Abstracted model execution layer that uniformizes text prompt payloads and token completion parameters across disparate infrastructure engines.

## 5. Collection Management & Vector Storage
Manages index lifecycles, structured data updates, and low-latency nearest-neighbor semantic search execution.
* **Setup Collection:** Creates and configures isolated namespaces or relational tables inside the vector index parameters.
* **Add Documents:** Feeds text chunks to active embedding functions and persists the resulting multi-dimensional arrays inside the vector collection.
* **Query Documents:** Calculates the spatial embedding of an incoming user question, performing semantic similarity searches to extract relevant text fragments.
* **ChromaDB Client:** The database engine interfacing with local disk storage or external service instances to handle data persistence and indexing.

## 6. Response Generation
Constructs contextualized text configurations and handles generative execution loops.
* **Create Prompt:** Constructs the final "augmented prompt" payload by stitching the original user query alongside relevant semantic fragments harvested by document queries.
* **Generate Response:** Hands the structured prompt off to the assigned model context, receiving the token output stream and passing it back to the UI layout.

## 7. External Services
Provides underlying foundation models, offering modular support for cloud-hosted environments and local processing architectures.
* **OpenAI API:** Bridges cloud queries to proprietary models, offering support for high-fidelity generation (e.g., **GPT-4**) and industrial-grade embeddings (**OpenAI Embeddings**).
* **Ollama API:** Manages secure, local loopback requests to run open-weight open-source architectures (e.g., **Llama 2 / Llama 3** for generation or native embeddings) entirely offline.


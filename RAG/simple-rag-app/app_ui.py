import streamlit as st
import requests

# Page Layout Configurations
st.set_page_config(page_title="RAG Enterprise UI", page_icon="🤖", layout="wide")

# API Target Endpoints Context 
BACKEND_URL = "http://localhost:8000/api/v1"

st.title("🤖 Enterprise RAG Chat Interface")
st.markdown("Interact seamlessly with your document repository across isolated compute spaces.")

# --- Session State Initialization Matrix ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Persists the conversation thread across UI refreshes
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()

# --- Sidebar Configuration Management ---
st.sidebar.header("⚙️ Configuration Engine")

# Fetch available backend system options dynamically
try:
    capabilities_res = requests.get(f"{BACKEND_URL}/capabilities", timeout=5).json()
    available_llms = capabilities_res.get("available_llms", {"openai": "OpenAI"})
    available_embeddings = capabilities_res.get("available_embeddings", {"openai": "OpenAI"})
except Exception:
    st.sidebar.error("⚠️ Unable to connect to the FastAPI backend service. Ensure it is running on port 8000.")
    st.stop()

# Dynamic Option dropdown select arrays mapped to enum parameters
llm_choice = st.sidebar.selectbox(
    "Select Inference LLM Node:",
    options=list(available_llms.keys()),
    format_func=lambda x: available_llms[x]
)

embedding_choice = st.sidebar.selectbox(
    "Select Vector Space Layout:",
    options=list(available_embeddings.keys()),
    format_func=lambda x: available_embeddings[x]["name"]
)

st.sidebar.markdown("---")
st.sidebar.header("📁 Document Management")

# Direct file streams uploaded straight to FastAPI multipart forms boundaries
uploaded_file = st.sidebar.file_uploader("Ingest target documentation (PDF):", type=["pdf"])

if uploaded_file is not None:
    file_key = f"{embedding_choice}_{uploaded_file.name}"
    
    if file_key not in st.session_state.indexed_files:
        with st.sidebar.spinner("Streaming file binary matrix to extraction servers..."):
            try:
                # Prepare structural payload tracking rules
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"embedding_model": embedding_choice, "llm_model": llm_choice}
                
                # Push file stream straight over network layers
                response = requests.post(f"{BACKEND_URL}/ingest", files=files, data=data, timeout=60)
                
                if response.status_code == 200:
                    res_data = response.json()
                    if res_data.get("status") == "skipped":
                        st.sidebar.info(res_data.get("details"))
                    else:
                        st.sidebar.success(f"🟢 Successfully indexed: {res_data.get('segments_indexed')} segments cached!")
                    st.session_state.indexed_files.add(file_key)
                else:
                    st.sidebar.error(f"Ingestion Fault: {response.json().get('detail')}")
            except Exception as e:
                st.sidebar.error(f"Network Timeout/Error Context: {e}")
    else:
        st.sidebar.info("📄 File footprint matched inside system vector indexes.")


# --- Primary Chat Interface Workspace ---
# Render historic message strings preserved in states
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If tracking reference passages exist, display them neatly tucked away inside expanders
        if "sources" in message and message["sources"]:
            with st.expander("Inspect Retrieval Context Passages"):
                for src in message["sources"]:
                    st.caption(f"**Source Node [{src['passage_index']}] - File: {src['source']}**")
                    st.info(src["text"])

# Accept new natural language query input configurations
if user_prompt := st.chat_input("Ask something about your uploaded documents..."):
    
    # Render user prompt immediately in workspace view
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Call generative API loops
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Executing similarity mapping matrices & generating text synthesis..."):
            try:
                payload = {
                    "query": user_prompt,
                    "embedding_model": embedding_choice,
                    "llm_model": llm_choice,
                    "n_results": 3
                }
                
                # Issue structured POST request targeting query execution modules
                response = requests.post(f"{BACKEND_URL}/query", json=payload, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    answer_text = result.get("answer", "")
                    passages_metadata = result.get("source_passages", [])
                    
                    # Output main answer content configuration
                    response_placeholder.markdown(answer_text)
                    
                    # Display associated backend text segments reference parameters
                    if passages_metadata:
                        with st.expander("Inspect Retrieval Context Passages"):
                            for src in passages_metadata:
                                st.caption(f"**Source Node [{src['passage_index']}] - File: {src['source']}**")
                                st.info(src["text"])
                    
                    # Save context logs into memory layers
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "sources": passages_metadata
                    })
                else:
                    error_details = response.json().get("detail", "Unknown processing error.")
                    response_placeholder.error(f"Backend Exception: {error_details}")
            except Exception as err:
                response_placeholder.error(f"Failed to communicate with API Core gateway engine: {err}")
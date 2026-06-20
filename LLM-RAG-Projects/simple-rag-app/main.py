import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from schema import SystemCapabilitiesResponse, RAGQueryResponse, QueryInputPayload, LLMProvider, EmbeddingProvider
from models_factory import SimpleModelSelector
from pdf_processor import SimplePDFProcessor
from core_rag import SimpleRAGSystem

app = FastAPI(
    title="Enterprise Framework-Free RAG Engine API",
    description="De-coupled asynchronous microservice engine running clean validation schemas and modular extraction pipelines.",
    version="2.0.0"
)

# Enable CORS parameters to let any front-end connect safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global internal tracking layer mapping (In production configurations, bind this to cache/DB states)
processed_files_registry = set()

@app.get("/api/v1/capabilities", response_model=SystemCapabilitiesResponse, tags=["Metadata"])
async def get_system_capabilities():
    """Queries configuration registries to fetch available LLM variations and vector configurations."""
    return SimpleModelSelector().get_system_capabilities()


@app.post("/api/v1/ingest", tags=["Ingestion Pipeline"])
async def ingest_document_stream(
    file: UploadFile = File(...),
    embedding_model: EmbeddingProvider = Form(EmbeddingProvider.OPENAI),
    llm_model: LLMProvider = Form(LLMProvider.OPENAI)
):
    """Parses incoming multipart file streams, runs data sanitization loops, and seeds vector collections."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid layout configuration footprint. Input must be a valid PDF.")
    
    file_fingerprint = f"{embedding_model.value}_{file.filename}"
    if file_fingerprint in processed_files_registry:
        return {"status": "skipped", "details": f"File '{file.filename}' already processed for the chosen embedding layer."}
        
    try:
        file_bytes = await file.read()
        pdf_stream = io.BytesIO(file_bytes)
        
        # Parse text chunks
        processor = SimplePDFProcessor()
        extracted_text = processor.read_pdf(pdf_stream)
        chunks = processor.create_chunks(extracted_text, file.filename)
        
        if not chunks:
            raise HTTPException(status_code=422, detail="PDF extraction yielded an empty textual payload.")
            
        # Instantiate RAG core structures safely
        rag_system = SimpleRAGSystem(embedding_model=embedding_model, llm_model=llm_model)
        success = rag_system.add_documents(chunks)
        
        if not success:
            raise HTTPException(status_code=500, detail="Database write anomalies intercepted during insertion loops.")
            
        processed_files_registry.add(file_fingerprint)
        return {
            "status": "success",
            "filename": file.filename,
            "segments_indexed": len(chunks),
            "storage_namespace": f"system_index_layer_{embedding_model.value}"
        }
    except ValueError as val_err:
        raise HTTPException(status_code=401, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected pipeline transformation fault: {str(e)}")


@app.post("/api/v1/query", response_model=RAGQueryResponse, tags=["Retrieval Core"])
async def execution_query_loop(payload: QueryInputPayload):
    """Runs high-speed distance searches across tracking namespaces and synthesizes a verified answer choice."""
    try:
        # Initialize engine configuration instances
        rag_system = SimpleRAGSystem(embedding_model=payload.embedding_model, llm_model=payload.llm_model)
        
        # Pull vector matches down from database maps
        matched_passages = rag_system.query_documents(query=payload.query, n_results=payload.n_results)
        
        if not matched_passages:
            return {
                "query": payload.query,
                "answer": "No reference documentation metrics matching your search vector layout could be found inside database index structures.",
                "source_passages": []
            }
            
        # Call generative completion pipelines
        generation_outcome = rag_system.generate_response(query=payload.query, context_passages=matched_passages)
        
        return {
            "query": payload.query,
            "answer": generation_outcome,
            "source_passages": matched_passages
        }
    except ValueError as val_err:
        raise HTTPException(status_code=401, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution module runtime exception intercepted: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
try:
    from langchain.chains import RetrievalQA
except ImportError:
    from langchain_classic.chains import RetrievalQA
import os
from langchain_core.prompts import PromptTemplate

from app.components.llm import load_llm
from app.components.pdf_loader import create_text_chunks, load_pdf_files
from app.components.vector_store import save_vector_store
from app.components.vector_store import load_vector_store

from app.common.logger import get_logger
from app.common.custom_exception import CustomException


logger = get_logger(__name__)

CUSTOM_PROMPT_TEMPLATE = """Answer the following medical question in
two to three lines maximum
using only the information provided in the context.

Context:
{context}

Question:
{question}

Answer:
"""


def set_custom_prompt():
    return PromptTemplate(
        template=CUSTOM_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_qa_chain():
    try:
        logger.info("Loading vector store for context")
        db = load_vector_store()

        if db is None:
            if not _env_flag("AUTO_BUILD_VECTORSTORE_ON_STARTUP", False):
                logger.warning(
                    "Vector store missing and "
                    "AUTO_BUILD_VECTORSTORE_ON_STARTUP is disabled. "
                    "Upload a PDF to initialize retrieval."
                )
                return None

            logger.info("Vector store not found, building from local PDFs")
            documents = load_pdf_files()
            if not documents:
                logger.warning(
                    "No local PDFs found in data directory "
                    "to build vector store",
                )
                return None

            text_chunks = create_text_chunks(documents)
            if not text_chunks:
                logger.warning("No text chunks generated from local PDFs")
                return None

            db = save_vector_store(text_chunks)

        if db is None:
            return None

        llm = load_llm()

        if llm is None:
            raise CustomException("LLM not loaded")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={'k': 1}),
            return_source_documents=False,
            chain_type_kwargs={'prompt': set_custom_prompt()}
        )

        logger.info("Successfully created the QA chain")
        return qa_chain

    except Exception as e:
        error_message = CustomException("Failed to make a QA chain", e)
        logger.error(str(error_message))
        return None

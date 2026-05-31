from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.config.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

logger = get_logger(__name__)


def get_embedding_model():
    try:
        # Prefer OpenAI embeddings to avoid runtime HuggingFace downloads.
        if OPENAI_API_KEY:
            logger.info("Initializing OpenAI embedding model")
            model = OpenAIEmbeddings(
                api_key=OPENAI_API_KEY,
                model=OPENAI_EMBEDDING_MODEL,
            )
            logger.info("OpenAI embedding model loaded successfully")
            return model

        logger.info(
            "OPENAI_API_KEY missing; falling back to HuggingFace embeddings"
        )

        model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        logger.info("Huggingface embedding model loaded sucesfully....")

        return model

    except Exception as e:
        error_message = CustomException(
            "Error occured while loading embedding model",
            e,
        )
        logger.error(str(error_message))
        raise error_message

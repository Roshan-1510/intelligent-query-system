from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config import settings
import logging

logger = logging.getLogger(__name__)

class VectorIndex:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.vectorstore = None

    def add_documents(self, docs: list[Document]):
        logger.info("Embedding and indexing documents...")
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)

    def search(self, query: str, k: int = 3) -> list[Document]:
        if not self.vectorstore:
            raise RuntimeError("Vector store is empty")
        return self.vectorstore.similarity_search(query, k=k)

vector_index = VectorIndex()

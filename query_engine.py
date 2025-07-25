# query_engine.py
import os
import logging
import json
import requests
import pypdf
import docx
import eml_parser
from io import BytesIO
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IntelligentQueryEngine:
    def __init__(self):
        self.vector_store = None
        self.qa_chain = None
        self._initialize_models()

    def _initialize_models(self):
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables.")

            self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.0,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            logging.info("Google AI Models initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize models: {e}")
            self.llm = None
            self.embedding_model = None

    def _process_text_and_create_index(self, text: str):
        if not text or not text.strip():
            raise ValueError("No text was extracted from the document to process.")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        self.vector_store = FAISS.from_texts(texts=chunks, embedding=self.embedding_model)
        self._create_qa_chain()

    def process_document_from_url(self, url: str):
        if not self.embedding_model:
            raise RuntimeError("Embedding model is not initialized.")
        try:
            response = requests.get(url, timeout=30); response.raise_for_status()
            file_stream = BytesIO(response.content)
            text = ""
            main_url_part = url.split('?')[0].lower()
            content_type = response.headers.get('Content-Type', '')

            if main_url_part.endswith('.pdf') or 'application/pdf' in content_type:
                pdf_reader = pypdf.PdfReader(file_stream)
                if pdf_reader.is_encrypted: raise ValueError("The provided PDF is password-protected.")
                text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            elif main_url_part.endswith('.docx') or 'officedocument' in content_type:
                document = docx.Document(file_stream)
                text = "\n".join([para.text for para in document.paragraphs if para.text])
            elif main_url_part.endswith('.eml') or 'message/rfc822' in content_type:
                ep = eml_parser.EmlParser()
                parsed_eml = ep.decode_email_bytes(response.content)
                if parsed_eml.get('body'): text = "\n".join([item['content'] for item in parsed_eml['body']])
            else:
                raise ValueError(f"Unsupported file type. URL part: {main_url_part}, Content-Type: {content_type}")
            
            self._process_text_and_create_index(text)
            return True
        except Exception as e:
            logging.error(f"Failed to process document from URL: {e}"); return False

    def _create_qa_chain(self):
        prompt_template = """
        You are an expert AI assistant. Your task is to answer the user's question based ONLY on the provided context clauses.
        **Context Clauses:**\n{context}\n\n**User's Question:**\n{question}\n
        Your final output must be a single, direct, and concise answer to the question. Do not provide a rationale or any extra text. Just the answer.
        If the context does not contain the information, state that the information is not available in the provided document.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm, chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={'k': 5}),
            chain_type_kwargs={"prompt": prompt}
        )

    def answer_question(self, question: str):
        if not self.qa_chain: return {"error": "Document not processed yet."}
        try:
            result = self.qa_chain.invoke({"query": question})
            return result.get('result', "No answer could be generated.")
        except Exception as e:
            logging.error(f"Error during query: {e}"); return {"error": str(e)}
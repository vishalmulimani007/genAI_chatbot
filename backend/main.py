from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
import uvicorn

from config_loader import ConfigLoader
from api.routes import get_router

from database.chroma_client import ChromaClient
from ingestion.crawler import Crawler
import asyncio
from services.retrieval_service import RetrievalService
from services.llm_service import LLMService
from services.rag_service import RAGService
from prompt.prompt_builder import PromptBuilder
from models.response_builder import ResponseBuilder
from fastapi.middleware.cors import CORSMiddleware

# def initialize_database():
#     """
#     Initialize vector DB and run ingestion if empty.
#     """

#     chroma_client = ChromaClient()

#     doc_count = chroma_client.count_documents()

#     if doc_count == 0:
#         print("Vector database empty. Running ingestion pipeline...")

#         base_urls = [
#             "https://handbook.gitlab.com/",
#             "https://about.gitlab.com/direction/"
#         ]

#         # pipeline = IngestionPipeline(base_urls)
#         # pipeline.run()

#         print("Ingestion completed successfully.")

#     else:
#         print(f"Vector database already populated ({doc_count} documents).")

def initialize_database():
    """
    Initialize vector DB and run ingestion if empty.
    """

    chroma_client = ChromaClient()
    doc_count = chroma_client.count_documents()

    if doc_count == 0:
        print("🚀 Vector DB empty → Running crawler ingestion...")

        async def run_crawler():
            crawler = Crawler()
            await crawler.run()

        try:
            asyncio.run(run_crawler())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_crawler())

        print("✅ Ingestion completed successfully.")

    else:
        print(f"✅ Vector DB already populated ({doc_count} documents)")

def initialize_services() -> RAGService:
    """
    Initialize all backend services once during startup.
    """

    retrieval_service = RetrievalService()
    llm_service = LLMService()
    prompt_builder = PromptBuilder()
    response_builder = ResponseBuilder()
    

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        llm_service=llm_service,
        prompt_builder=prompt_builder,
        response_builder=response_builder
    )

    return rag_service


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    """

    config_loader = ConfigLoader()
    config_loader.get()

    # Ensure DB exists and ingestion is complete
    initialize_database()

    # Initialize RAG pipeline
    rag_service = initialize_services()

    app = FastAPI(
        title="GitLab GenAI Chatbot",
        description="RAG-based chatbot for GitLab Handbook and Direction pages",
        version="1.0.0"
    )

    # Register API routes with rag_service
    app.include_router(get_router(rag_service))

    return app


app = create_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":

    config_loader = ConfigLoader()
    server_config = config_loader.get_section("server")

    uvicorn.run(
        "main:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=False
    )